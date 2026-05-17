from multiagent.MultiAgenteChatbot.MultiAgenteChatbot import *

#Importamos los utilitarios de la base de datos
from agent.AgenteDeBaseDeDatos.UtilesBaseDeDatosSQLite import *

#Importamos el MultiAgente
from multiagent.MultiAgenteReporteria import *

#Obtenemos el modelo
llm = obtenerModelo()

print("Cargando utilitarios de base de datos...")

#Utilitarios de la base de datos
utilesBaseDeDatos = UtilesBaseDeDatosSQLite(
    rutaDeBaseDeDatos = CONF_BASE_DE_DATOS_RUTA
)

print("Construyendo el multi-agente...")

#Construimos el flujo multi-agente
multiAgenteReporteria = MultiAgenteReporteria(
  llm = llm,
  dialectoDeBaseDeDatos = "SQLite",
  utilesBaseDeDatos = utilesBaseDeDatos,
  rutaDeReporte = CONF_RUTA_REPORTES
)

print("Ejecutando sentencia...")

#Ejecutamos
respuesta = multiAgenteReporteria.ejecutar(
  prompt = """
    Agrupa a los clientes por la edad y muestra por cada grupo:

    - La cantidad de clientes en el grupo
    - La cantidad de transacciones que han realizado
    - El monto total de sus transacciones
    - El monto promedio de sus transacciones
  """
)

#Verificamos
print(respuesta)