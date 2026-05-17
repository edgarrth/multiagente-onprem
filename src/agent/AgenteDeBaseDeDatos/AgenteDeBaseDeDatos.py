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
from agent.AgenteDeBaseDeDatos.UtilesBaseDeDatosSQLite import *

#Utilitarios del agente de base de datos
from agent.AgenteDeBaseDeDatos.UtilesAgenteDeBaseDeDatos import *

#Definimos una clase
class AgenteDeBaseDeDatos:

  #Definimos el constructor
  def __init__(
      self,
      llm = None,
      dialectoDeBaseDeDatos = None,
      utilesBaseDeDatos = None
  ):
    #ATRIBUTOS
    self.llm = llm
    self.dialectoDeBaseDeDatos = dialectoDeBaseDeDatos
    self.utilesBaseDeDatos = utilesBaseDeDatos

    #OTROS OBJETOS
    self.esquema = self.utilesBaseDeDatos.obtenerEsquemaDeMetadatos()
    self.utilesAgenteDeBaseDeDatos = UtilesAgenteDeBaseDeDatos(
      llm = self.llm,
      dialectoDeBaseDeDatos = self.dialectoDeBaseDeDatos,
      esquema = self.esquema
    )

  #Ejecutar el agente
  def ejecutar(self, prompt):
    respuesta = None

    #Generamos el código SQL
    sql = self.utilesAgenteDeBaseDeDatos.generaCodigoSQLDesdeNLP(
        pregunta = prompt
    )

    #Ejecutamos la consulta SQL
    resultados = self.utilesBaseDeDatos.ejecutarConsulta(
        sql = sql
    )

    #Analizamos los resultados
    analisis = self.utilesAgenteDeBaseDeDatos.analizarDatos(
        datos = resultados,
        sql = sql,
        prompt = prompt
    )

    #Construimos la respuesta
    respuesta = {
        "sql": sql,
        "resultados": resultados,
        "analisis": analisis
    }

    #Devolvemos la respuesta
    return respuesta

#Definición de clase
class AgenteDeVisualizacion:

  def __init__(
    self,
    llm = None,
    rutaDeReporte = None
  ):
    #Guardamos los atributos
    self.llm = llm
    self.rutaDeReporte = rutaDeReporte

    #Plantilla de prompt
    self.promptTemplate = PromptTemplate.from_template("""
      Vas a generar códigos HTML para páginas web de reportes. En tus respuestas solo debes darme el código HTML,
      no agregues más comentarios u otras cosas, sólo el HTML

      El reporte debe cumplir la siguiente descripción:

      {descripcion}

      Y estos son los datos para el reporte

      {datos}
    """)

  #Envía un mensaje
  def ejecutar(
      self,
      descripcion = None,
      datos = None
  ):
    respuesta = None

    #Creamos el prompt
    promt = self.promptTemplate.format(
      descripcion = descripcion,
      datos = datos
    )

    #Invocamos el modelo y reemplazamos la marca "html"
    respuesta = self.llm.invoke(promt).content.replace("```html", "").replace("```", "")

    #Nombre de reporte (fecha + hora a nivel de microsegundo)
    nombreReporte = datetime.now().strftime("%Y%m%d%H%M%S%f")

    #Ruta completa del reporte:
    rutaCompletaDelReporte = self.rutaDeReporte+"/REPORTE_"+nombreReporte+".html"

    #Guardamos el reporte
    with open(rutaCompletaDelReporte, "w", encoding="utf-8") as archivo:
      archivo.write(respuesta)

    #Devolvemos el contenido de la respuesta
    return f"El reporte se ha generado en la ruta: {rutaCompletaDelReporte}"