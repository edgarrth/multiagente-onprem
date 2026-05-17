import re
import uuid
from pathlib import Path
import base64
import sqlite3

import streamlit as st

from conf.conf import (
    CONF_BASE_DE_CONOCIMIENTO_NOMBRE,
    CONF_BASE_DE_CONOCIMIENTO_RUTA,
    CONF_BASE_DE_DATOS_RUTA,
    CONF_NOMBRE_PROYECTO,
    CONF_RUTA_REPORTES,
)
from multiagent.MultiAgenteChatbot.MultiAgenteChatbot import MultiAgenteChatbot
from multiagent.MultiAgenteReporteria import MultiAgenteReporteria
from agent.AgenteDeBaseDeDatos.UtilesBaseDeDatosSQLite import UtilesBaseDeDatosSQLite
from util.util_ia_onpremise import (
    crearBaseDeDatosDePrueba,
    insertarEnBaseDeConocimiento,
    leerBaseDeConocimientoDeUsuario,
    obtenerEsquemaDeMetadatos,
    obtenerModelo,
)

DEFAULT_PERSONALIDAD = """
Eres un asistente llamado "ArquiBot" que atendera consultas de alumnos para cursos, de
formacion de cursos de Arquitectura de soluciones y empresarial. Al contestar debes
seguir las siguientes reglas:

1. Debes contestar en un lenguaje formal pero amigable
2. Debes de usar emojis al responder
""".strip()

DEFAULT_CONDICIONES = """
Como minimo debe cumplirse estas condiciones:

- Es un mensaje relacionado a lo que se esperaria en una conversacion
- Es un mensaje que no contiene palabras groseras o que se consideren faltas de respeto
- Es un mensaje con un tema que una academia que dicta cursos esperaria recibir
""".strip()

DEFAULT_REGLAS_MEMORIA = """
- El nombre del usuario
- La edad del usuario
- El sexo del usuario
""".strip()

DEFAULT_PROMPT_REPORTERIA = """
Agrupa a los clientes por la edad y muestra por cada grupo:

- La cantidad de clientes en el grupo
- La cantidad de transacciones que han realizado
- El monto total de sus transacciones
- El monto promedio de sus transacciones
""".strip()


@st.cache_resource(show_spinner=False)
def get_llm():
    return obtenerModelo()


def build_chatbot(config: dict) -> MultiAgenteChatbot:
    return MultiAgenteChatbot(
        llm=get_llm(),
        baseDeConocimientoDeUsuario=config["base_de_conocimiento_usuario"],
        personalidad=config["personalidad"],
        condicionesDeContexto=config["condiciones"],
        reglasDeMemoriaDeLargoPlazo=config["reglas_memoria"],
    )


def ensure_paths():
    Path(CONF_RUTA_REPORTES).mkdir(parents=True, exist_ok=True)
    Path(CONF_BASE_DE_CONOCIMIENTO_RUTA).mkdir(parents=True, exist_ok=True)


st.set_page_config(page_title=f"{CONF_NOMBRE_PROYECTO} UI", layout="wide")
ensure_paths()

st.title(f"{CONF_NOMBRE_PROYECTO} - UI Streamlit")

st.sidebar.header("Configuracion de chatbot")
base_de_conocimiento_usuario = st.sidebar.text_input(
    "ID de usuario",
    value=st.session_state.get("base_de_conocimiento_usuario", "armg"),
)

personalidad = st.sidebar.text_area(
    "Personalidad",
    value=st.session_state.get("personalidad", DEFAULT_PERSONALIDAD),
    height=150,
)

condiciones = st.sidebar.text_area(
    "Condiciones de contexto",
    value=st.session_state.get("condiciones", DEFAULT_CONDICIONES),
    height=150,
)

reglas_memoria = st.sidebar.text_area(
    "Reglas de memoria",
    value=st.session_state.get("reglas_memoria", DEFAULT_REGLAS_MEMORIA),
    height=120,
)

if st.sidebar.button("Reiniciar chatbot"):
    st.session_state.pop("chatbot", None)
    st.session_state.pop("chat_history", None)

st.session_state["base_de_conocimiento_usuario"] = base_de_conocimiento_usuario
st.session_state["personalidad"] = personalidad
st.session_state["condiciones"] = condiciones
st.session_state["reglas_memoria"] = reglas_memoria

if "chatbot" not in st.session_state:
    st.session_state["chatbot"] = build_chatbot(
        {
            "base_de_conocimiento_usuario": base_de_conocimiento_usuario,
            "personalidad": personalidad,
            "condiciones": condiciones,
            "reglas_memoria": reglas_memoria,
        }
    )

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

chatbot_tab, reporteria_tab, herramientas_tab = st.tabs(
    ["Chatbot", "Reporteria", "Herramientas"]
)

with chatbot_tab:
    st.subheader("Chatbot multi-agente")

    for mensaje in st.session_state["chat_history"]:
        with st.chat_message(mensaje["role"]):
            st.markdown(mensaje["content"])

    prompt = st.chat_input("Escribe tu mensaje")
    if prompt:
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Generando respuesta..."):
            respuesta = st.session_state["chatbot"].ejecutar(prompt)

        st.session_state["chat_history"].append(
            {"role": "assistant", "content": respuesta}
        )
        with st.chat_message("assistant"):
            st.markdown(respuesta)

    with st.expander("Memoria del usuario"):
        memoria = leerBaseDeConocimientoDeUsuario(base_de_conocimiento_usuario)
        if memoria:
            st.code(memoria)
        else:
            st.write("Sin memoria almacenada.")

with reporteria_tab:
    st.subheader("Reporteria multi-agente")

    prompt_reporteria = st.text_area(
        "Describe el reporte",
        value=DEFAULT_PROMPT_REPORTERIA,
        height=180,
    )

    if st.button("Generar reporte"):
        with st.spinner("Ejecutando flujo de reporteria..."):
            utiles = UtilesBaseDeDatosSQLite(rutaDeBaseDeDatos=CONF_BASE_DE_DATOS_RUTA)
            multi_agente = MultiAgenteReporteria(
                llm=get_llm(),
                dialectoDeBaseDeDatos="SQLite",
                utilesBaseDeDatos=utiles,
                rutaDeReporte=str(CONF_RUTA_REPORTES),
            )
            respuesta = multi_agente.ejecutar(prompt_reporteria)

        st.success("Proceso terminado.")
        st.write(respuesta)

        reporte_match = re.search(r"ruta:\s*(.+\.html)", respuesta)
        if reporte_match:
            reporte_path = Path(reporte_match.group(1).strip())
            if reporte_path.exists():
                reporte_html = reporte_path.read_text(encoding="utf-8")
                reporte_b64 = base64.b64encode(reporte_html.encode("utf-8")).decode("ascii")
                with st.expander("Vista previa del reporte"):
                    st.iframe(f"data:text/html;base64,{reporte_b64}", height=600)
                st.download_button(
                    "Descargar reporte",
                    data=reporte_html,
                    file_name=reporte_path.name,
                    mime="text/html",
                )

with herramientas_tab:
    st.subheader("Utilitarios")

    col_izq, col_der = st.columns(2)

    with col_izq:
        if st.button("Crear base de datos de prueba"):
            with st.spinner("Creando base de datos..."):
                crearBaseDeDatosDePrueba(CONF_BASE_DE_DATOS_RUTA)
            st.success("Base de datos creada.")

            #Validamos inserciones
            try:
                conexion = sqlite3.connect(CONF_BASE_DE_DATOS_RUTA)
                cursor = conexion.cursor()
                conteos = {}
                for tabla in ["cliente", "empresa", "transaccion"]:
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                    conteos[tabla] = cursor.fetchone()[0]
                conexion.close()
                st.json(conteos)
            except Exception as exc:
                st.warning(f"No se pudo validar inserciones: {exc}")

        if st.button("Ver esquema de la base de datos"):
            esquema = obtenerEsquemaDeMetadatos(CONF_BASE_DE_DATOS_RUTA)
            st.json(esquema)

    with col_der:
        st.write("Ingesta de PDFs a la base de conocimiento")
        archivos = st.file_uploader(
            "Selecciona uno o varios PDFs",
            type=["pdf"],
            accept_multiple_files=True,
        )
        if st.button("Ingestar PDFs"):
            if not archivos:
                st.warning("No seleccionaste archivos.")
            else:
                uploads_dir = Path(CONF_BASE_DE_CONOCIMIENTO_RUTA) / "uploads"
                uploads_dir.mkdir(parents=True, exist_ok=True)
                with st.spinner("Procesando documentos..."):
                    for archivo in archivos:
                        destino = uploads_dir / f"{uuid.uuid4().hex}.pdf"
                        destino.write_bytes(archivo.getbuffer())
                        insertarEnBaseDeConocimiento(
                            rutaDeDocumento=str(destino),
                            nombreDeBaseDeConocimiento=CONF_BASE_DE_CONOCIMIENTO_NOMBRE,
                            rutaDeBaseDeConocimiento=str(CONF_BASE_DE_CONOCIMIENTO_RUTA),
                        )
                st.success("Ingesta terminada.")

    st.divider()
    st.write("Rutas activas")
    st.code(
        "\n".join(
            [
                f"Base de datos: {CONF_BASE_DE_DATOS_RUTA}",
                f"Base de conocimiento: {CONF_BASE_DE_CONOCIMIENTO_RUTA}",
                f"Reportes: {CONF_RUTA_REPORTES}",
            ]
        )
    )
