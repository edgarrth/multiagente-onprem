#Importamos la configuración
from conf.conf import *

## ################q######################################################################################
## @section Librerías
## #######################################################################################################

#Librería plugin para que Langchain pueda usar Ollama
from langchain_ollama import ChatOllama

#Utilitario para conectarnos a un modelo de embeddings
from langchain_ollama import OllamaEmbeddings

#Utilitario para crear la memoria a corto plazo del modelo
from langchain_core.chat_history import InMemoryChatMessageHistory

#Utilitario para definir reglas de "personalidad" en el modelo
from langchain_core.messages import SystemMessage

#Utilitario para enviar mensajes más complejos
from langchain_core.messages import HumanMessage

#Utilitario para leer PDFs
from langchain_community.document_loaders import PyPDFLoader

#Utilitario para cortar los textos en chunks
from langchain_text_splitters import RecursiveCharacterTextSplitter

#Utilitario para crear bases de conocimiento
from langchain_chroma import Chroma

#Utilitarios para interfaces gráficas
import gradio as gr

#Utilitario para deifinir las tools
from langchain_core.tools import tool

#Utilitario para definir prompts
from langchain_core.prompts import PromptTemplate

#Utilitario para crear agentes
from langchain.agents import create_agent

#Utilitario para obtener la fecha y hora
from datetime import datetime

#Utilitario para manipular JSONs
import json

#Librería para SQLite
import sqlite3

#Librería para manipular el sistema operativo
import os

#Librería para generar números aleatorios
import random

#Obtiene el modelo con el que trabajamos
def obtenerModelo():
  #Conexión a un modelo
  llm = ChatOllama(
    model = CONF_MODEL,
    base_url = CONF_SERVICE,
    keep_alive = CONF_KEEP_ALIVE
  )

  #Forzamos una invocación para que el modelo se cargue a la memoria RAM/VRAM
  print("Cargando modelo a la RAM/VRAM...")
  llm.invoke("Hola")

  return llm

#Obtiene el modelo para hacer embeddings
def obtenerModeloEmbedding():
  #Conexión a un modelo
  llmEmbedding = OllamaEmbeddings(
    model = CONF_MODEL_EMBEDDING,
    base_url = CONF_SERVICE,
    keep_alive = CONF_KEEP_ALIVE
  )

  return llmEmbedding

#Abre la sesión de chat con el modelo
def crearMemoriaCortoPlazo(
    contexto = None
):
  #Definimos el mensaje del sistema
  mensajeDelSistema = SystemMessage(
      content = [
          contexto
      ]
  )

  #Creamos la memoria a corto plazo
  memoriaCortoPlazo = InMemoryChatMessageHistory()

  #Agregamos la personalidad en la memoria a corto plazo
  memoriaCortoPlazo.add_message(mensajeDelSistema)

  return memoriaCortoPlazo

#Envia un mensaje al modelo
def enviarMensajeAlModelo(
    llm = None,
    memoriaCortoPlazo = None,
    mensaje = None
):
  #Construmos el JSON del mensaje
  mensajeHumano = HumanMessage(
    content=[
      {
        "type": "text",
        "text": mensaje
      }
    ]
  )

  #Agregamos el mensaje del ser humano
  memoriaCortoPlazo.add_user_message(mensajeHumano)

  #Envíamos el mensaje
  respuesta = llm.invoke(memoriaCortoPlazo.messages)

  #Guardamos en la memoria a corto plazo la respuesta de la IA
  memoriaCortoPlazo.add_ai_message(respuesta)

  return respuesta.content

#Función utilitaria
def leerDocumentoPDF(
  rutaDeDocumento = None
):

  #Apuntamos al documento que vamos a leer
  lector = PyPDFLoader(rutaDeDocumento)

  #Leemos el documento
  documento = lector.load()

  return documento

#Función utilitaria
def obtenerChunks(
  documento = None
):

  #Definimos el cortador y los tamaños de corte
  splitter = RecursiveCharacterTextSplitter(
      chunk_size = 1000,
      chunk_overlap = 200
  )

  #Obtenemos los cortes (chunks)
  chunks = splitter.split_documents(documento)

  return chunks

#Creo o, si ya existe, obtiene, una base de conocimiento
def obtenerBaseDeConocimiento(
  nombre = None,
  ruta = None
):

  #Creamos la base de conocimiento en su carpeta y nos conectamos a ella para manipularla
  #Si es que esta ya existe, no se crea, solo se conecta
  baseDeConocimiento = Chroma(
      collection_name = nombre,
      persist_directory = ruta,
      embedding_function = obtenerModeloEmbedding()
  )

  return baseDeConocimiento

#Inserta información en base de conocimiento
def insertarEnBaseDeConocimiento(
  rutaDeDocumento = None,
  nombreDeBaseDeConocimiento = None,
  rutaDeBaseDeConocimiento = None
):

  #Leemos el documento
  documento = leerDocumentoPDF(
    rutaDeDocumento = rutaDeDocumento
  )

  #Obtenemos los chunks
  chunks = obtenerChunks(
    documento = documento
  )

  #Obtenemos la base de conocimiento
  baseDeConocimiento = obtenerBaseDeConocimiento(
      nombre = nombreDeBaseDeConocimiento,
      ruta = rutaDeBaseDeConocimiento
  )

  #Insertamos los chunks
  baseDeConocimiento.add_documents(chunks)

#Agrega el contexto al mensaje del usuario, desde una base de conocimiento
def mensajeConContextoDesdeBaseDeConocimiento(
    mensaje = None,
    nombreBaseDeConocimiento = None,
    rutaBaseDeConocimiento = None
):

  #Obtenemos la base de conocimiento desde que la recuperaremos la información
  baseDeConocimiento = obtenerBaseDeConocimiento(
    nombre = nombreBaseDeConocimiento,
    ruta = rutaBaseDeConocimiento
  )

  #Sobre la base de conocimiento, creamos un recuperador de información
  #Configuramos la cantidad de coincidencias
  recuperadorDeInformacion = baseDeConocimiento.as_retriever(
    search_kwargs = {
      "k": CONF_BASE_DE_CONOCIMIENTO_COINCIDENCIAS_MAXIMAS
    }
  )

  #Buscamos los chunks con las coincidencias en la base de conocimiento
  coincidencias = recuperadorDeInformacion.invoke(mensaje)

  #Variable que acumula todos los chunks de textos
  resultadoDeBusqueda = ""

  #Acumulamos todos los chunks
  for chunk in coincidencias:
    resultadoDeBusqueda = resultadoDeBusqueda + chunk.page_content + "\n"

  #Definimos el mensaje con contexto
  mensajeConContexto = f"""
    Usa los siguientes fragmentos de contexto para responder la pregunta.
    Si no encuentras la respuesta en el contexto, di que no lo sabes.

    Contexto:
    {resultadoDeBusqueda}

    Pregunta:
    {mensaje}
  """

  return mensajeConContexto

#Envia un mensaje al modelo
def enviarMensajeAlModeloConContextoDeBaseDeConocimiento(
    llm = None,
    memoriaCortoPlazo = None,
    mensaje = None,
    nombreBaseDeConocimiento = None,
    rutaBaseDeConocimiento = None
):
  #Contextualizamos el mensaje desde la base de conocimiento
  mensajeConContexto = mensajeConContextoDesdeBaseDeConocimiento(
      mensaje = mensaje,
      nombreBaseDeConocimiento = nombreBaseDeConocimiento,
      rutaBaseDeConocimiento = rutaBaseDeConocimiento
  )

  #Enviamos la pregunta
  respuesta = enviarMensajeAlModelo(
      llm = llm,
      memoriaCortoPlazo = memoriaCortoPlazo,
      mensaje = mensajeConContexto
  )

  #Devolvemos la respuesta
  return respuesta

#Función utilitaria para enviar mensajes a agentes
def enviarMensajeAlAgente(
    agente = None,
    mensaje = None
):
  #Construimos el JSON del mensaje
  mensajeHumano = HumanMessage(
      content=[
        {
          "type": "text",
          "text": mensaje
        }
      ]
    )

  #Ejecutamos el agente
  respuesta = agente.invoke(
      {
          "messages": [
              mensajeHumano
          ]
      }
  )

  #Retornamos la respuesta
  return respuesta["messages"][-1].content

#Función utilitaria para crear un agente
def crearAgente(
    llm = None,
    tools = None
):
  #Creamos el agente
  agente = create_agent(
    model = llm,
    tools = tools
  )

  #Lo devolvemos
  return agente

#Obtiene los parámetros del agente
def obtenerParametrosDeAgente(input):
  parametros = None

  #Tratamos de obtener el json de los parámetros
  try:
    parametros = json.loads(input)
  except Exception as e:
    #Si falla, cremos un JSON vacío
    parametros = {}

  return parametros

#Definimos una clase
class Agente:

  #Definimos el constructor
  def __init__(
      self,
      llm = None,
      tools = None
  ):
    #Creamos el agente
    self.agente = crearAgente(
        llm = llm,
        tools = tools
    )

  #Ejecutar el agente
  def ejecutar(self, prompt):
    #Ejecutamos el agente con el prompt
    respuesta = enviarMensajeAlAgente(
        agente = self.agente,
        mensaje = prompt
    )

    #Devolvemos la respuesta
    return respuesta

#Utilitario para escribir en base de conocimiento de usuario
def actualizarBaseDeConocimientoDeUsuario(
  baseDeConocimientoDeUsuario = None,
  contenido = None
):
  #Creamos la carpeta si no existe
  os.makedirs(CONF_BASE_DE_CONOCIMIENTO_USUARIOS, exist_ok = True)

  #Almacenamos el contenido en un archivo
  with open(CONF_BASE_DE_CONOCIMIENTO_USUARIOS+"/"+baseDeConocimientoDeUsuario+".txt", "w", encoding="utf-8") as archivo:
    archivo.write(contenido)

#Utilitario para leer desde base de conocimiento de usuario
def leerBaseDeConocimientoDeUsuario(
  baseDeConocimientoDeUsuario = None
):
  #Verificamos si existe el archivo
  if os.path.exists(CONF_BASE_DE_CONOCIMIENTO_USUARIOS / f"{baseDeConocimientoDeUsuario}.txt"):
    #Leemos el contenido del archivo
    with open(CONF_BASE_DE_CONOCIMIENTO_USUARIOS / f"{baseDeConocimientoDeUsuario}.txt", "r", encoding="utf-8") as archivo:
        contenido = archivo.read()
  else:
    contenido = ""

  return contenido

#Función para crear una base de datos de prueba
def crearBaseDeDatosDePrueba(
  rutaDeBaseDeDatos = None
):
  #Borramos el archivo de base de datos
  if os.path.exists(rutaDeBaseDeDatos):
      os.remove(rutaDeBaseDeDatos)

  #Creamos el directorio si no existe
  Path(rutaDeBaseDeDatos).parent.mkdir(parents=True, exist_ok=True)

  #Creamos una base de datos de prueba
  conexion = sqlite3.connect(rutaDeBaseDeDatos)

  #Creamos un cursor que modifique la base de datos
  cursor = conexion.cursor()

  #Creamos una tabla
  cursor.execute("""
  CREATE TABLE IF NOT EXISTS cliente (
      id INTEGER PRIMARY KEY,
      edad INTEGER,
      nombre TEXT,
      correo TEXT
  )
  """)

  #Insertamos algunos registros de prueba
  cursor.executemany("""
  INSERT INTO cliente (id, edad, nombre, correo) VALUES (?, ?, ?, ?)
  """, [
      (1, 28, "Lucía Ríos", "lucia.rios@mail.com"),
      (2, 35, "Carlos Pérez", "carlos.perez@mail.com"),
      (3, 42, "María Gómez", "maria.gomez@mail.com"),
      (4, 30, "José Torres", "jose.torres@mail.com"),
      (5, 26, "Andrea Silva", "andrea.silva@mail.com"),
      (6, 38, "Luis Ramírez", "luis.ramirez@mail.com"),
      (7, 31, "Paula Díaz", "paula.diaz@mail.com"),
      (8, 45, "Renato Chávez", "renato.chavez@mail.com"),
      (9, 29, "Camila León", "camila.leon@mail.com"),
      (10, 34, "Javier Soto", "javier.soto@mail.com")
  ])

  #Creamos una tabla
  cursor.execute("""
  CREATE TABLE IF NOT EXISTS empresa (
      id INTEGER PRIMARY KEY,
      nombre TEXT
  )
  """)

  #Insertamos algunos registros de prueba
  cursor.executemany("""
  INSERT INTO empresa (id, nombre) VALUES (?, ?)
  """, [
      (1, "TecnoPerú SAC"),
      (2, "Inversiones Andinas SRL"),
      (3, "Soluciones Digitales SA"),
      (4, "Grupo Constructor del Sur"),
      (5, "Comercial San Miguel EIRL"),
      (6, "AgroExport Perú"),
      (7, "Servicios Médicos Los Andes"),
      (8, "Logística y Transporte Lima"),
      (9, "Educación Global SAC"),
      (10, "Finanzas Seguras SRL")
  ])

  #Creamos una tabla
  cursor.execute("""
  CREATE TABLE IF NOT EXISTS transaccion (
      id INTEGER PRIMARY KEY,
      cliente_id INTEGER,
      empresa_id INTEGER,
      monto REAL,
      fecha TEXT
  )
  """)

  #Registros que se generarán
  transacciones = []

  #Insertamos algunos registros de prueba
  for i in range(1, 101):
    #Obtenemos un identificador único aleatorio
    id_transaccion = i

    #Obtenemos un ID de cliente aleatorio
    cliente_id = random.randint(1, 10)

    #Obtenemos un ID de empresa aleatorio
    empresa_id = random.randint(1, 10)

    #Obtenemos un monto aleatorio entre 100 y 5000
    monto = round(random.uniform(100.0, 5000.0))

    #Definimos una fecha para la transacción
    fecha = "2025-03-25"

    #Agregamos la transacción
    transacciones.append(
        (id_transaccion, cliente_id, empresa_id, monto, fecha)
    )

  #Insertamos las transacciones
  cursor.executemany("""
    INSERT INTO transaccion (id, cliente_id, empresa_id, monto, fecha) VALUES (?, ?, ?, ?, ?)
  """, transacciones)

  #Confirmamos la inserción
  conexion.commit()

#Función utilitaria para obtener las tablas de una base de datos
def obtenerTablas(
  rutaDeBaseDeDatos = None
):
  #Creamos una base de datos de prueba
  conexion = sqlite3.connect(rutaDeBaseDeDatos)

  #Creamos un cursor que modifique la base de datos
  cursor = conexion.cursor()

  #Lanzamos la consulta en la tabla maestra que guarda la información de las otras tablas
  cursor.execute("""
    SELECT
      name
    FROM
      sqlite_master
    WHERE
      type='table' AND
      name NOT LIKE 'sqlite_%'
  """)

  #Obtenemos los nombres de las tablas
  tablas = []

  #Iteramos la consulta
  for fila in cursor.fetchall():
    tablas.append(fila[0])

  return tablas

#Función utilitaria para obtener la información de las columnas de una tabla
def obtenerInformacionDeColumnasDeTabla(
  rutaDeBaseDeDatos = None,
  tabla = None
):
  #Columnas de una tabla
  #Dentro, para cada columna, se indicará en un JSON:
  #
  # - nombreDeColumna: Nombre de la columna
  # - tipoDeDatoDeColumna: Tipo de dato de la columna
  columnasDeTabla = []

  #Creamos una base de datos de prueba
  conexion = sqlite3.connect(rutaDeBaseDeDatos)

  #Creamos un cursor que modifique la base de datos
  cursor = conexion.cursor()

  #Obtenemos la descripción de la tabla
  cursor.execute(f"PRAGMA table_info({tabla})")

  #Obtenemos la información de las columnas de la tabla
  informacionDeColumnas = cursor.fetchall()

  #Iteramos la información de cada columna
  for informacion in informacionDeColumnas:
    columnasDeTabla.append(
      {
        "nombreDeColumna": informacion[1],
        "tipoDeDatoDeColumna": informacion[2]
      }
    )

  return columnasDeTabla

#Función para obtener el esquema de metadatos de la base de datos
def obtenerEsquemaDeMetadatos(
  rutaDeBaseDeDatos = None
):
  #Nombres de tablas, e información de todos las columnas
  esquema = {}

  #Lo haremos en bucle para todas las tablas
  #Obtenemos las tablas
  tablas = obtenerTablas(
    rutaDeBaseDeDatos = rutaDeBaseDeDatos
  )

  #Iteramos todas las tablas
  for tabla in tablas:
    #Obtenemos la información de los campos
    informacion = obtenerInformacionDeColumnasDeTabla(
      rutaDeBaseDeDatos = rutaDeBaseDeDatos,
      tabla = tabla
    )

    #Asignamos el esquema a la tabla
    esquema[tabla] = informacion

  return esquema