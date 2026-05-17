#Importamos la configuración
from conf.conf import *

#Importamos los utilitarios
from util.util_ia_onpremise import *

## ################q######################################################################################
## @section Librerías
## #######################################################################################################

#Utilitario para crear una plantilla de prompt
from langchain_core.prompts import PromptTemplate

#Utilitario para convertir la estructura string a json
import json

#Utilitarios del motor de base de datos
from agent.AgenteDeBaseDeDatos.AgenteDeBaseDeDatos import *

#Utilitarios del agente de base de datos
from agent.AgenteDeVisualizacion import *

#Definición de clase
class MultiAgenteReporteria:

  #Instaciamos los objetos necesarios
  def __init__(
    self,
    llm = None,
    dialectoDeBaseDeDatos = None,
    utilesBaseDeDatos = None,
    rutaDeReporte = None
  ):
    #Atributos
    self.llm = llm
    self.dialectoDeBaseDeDatos = dialectoDeBaseDeDatos
    self.utilesBaseDeDatos = utilesBaseDeDatos
    self.rutaDeReporte = rutaDeReporte

    #Creamos un agente de base de datos
    self.agenteDeBaseDeDatos = AgenteDeBaseDeDatos(
        llm = self.llm,
        dialectoDeBaseDeDatos = self.dialectoDeBaseDeDatos,
        utilesBaseDeDatos = self.utilesBaseDeDatos
    )

    #Creamos un agente de visualización
    self.agenteDeVisualizacion = AgenteDeVisualizacion(
      llm = self.llm,
      rutaDeReporte = self.rutaDeReporte
    )

  #Ejecución
  def ejecutar(self, prompt):
    respuesta = None

    #Ejecutamos el agente de base de datos
    respuestaDeBaseDeDatos = self.agenteDeBaseDeDatos.ejecutar(
        prompt = prompt
    )

    #Ejecutamos el agente de reportería
    respuestaDeVisualizacion = self.agenteDeVisualizacion.ejecutar(
        descripcion = prompt + "\n\n" + """
        - Una párrafo descriptivo
        - Una tabla de datos
        - Usa un estilo empresarial
        - Sólo usa tonalidades oscuras
        - También en función de los datos, agrega un título
        - También, analiza los datos y agrega una recomendación de los patrones que veas
        - Incluye algún tipo de gráfico con código html que resuma la información
        - Agrega un buscador que permita filtrar los registros de la tabla
        """,
        datos = respuestaDeBaseDeDatos
    )

    respuesta = respuestaDeVisualizacion + "\n\n" + respuestaDeBaseDeDatos["analisis"]

    return respuesta