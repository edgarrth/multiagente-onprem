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

#Definimos una clase
class UtilesAgenteDeBaseDeDatos:

  #Definimos el constructor
  def __init__(
      self,
      llm = None,
      dialectoDeBaseDeDatos = None,
      esquema = None
  ):
    self.llm = llm
    self.dialectoDeBaseDeDatos = dialectoDeBaseDeDatos
    self.esquema = esquema

  #Función para generar el código SQL desde NLP
  def generaCodigoSQLDesdeNLP(
    self,
    pregunta = None
  ):
    sql = None

    #Creamos una plantilla de prompt
    promptTemplate = PromptTemplate.from_template("""
      Eres un experto en bases de datos con este dialecto

      {dialectoDeBaseDeDatos}

      Tu tarea es convertir la siguiente solicitud en lenguaje natural en una consulta SQL válida y ejecutable en {dialectoDeBaseDeDatos}.

      Esquema de la base de datos:
      {esquema}

      Solicitud del usuario:
      {pregunta}

      Respuesta: SOLO la consulta SQL, sin explicaciones.
    """)

    #Creamos el prompt
    prompt = promptTemplate.format(
      dialectoDeBaseDeDatos = self.dialectoDeBaseDeDatos,
      esquema = self.esquema,
      pregunta = pregunta
    )

    #Invocamos el modelo
    respuesta = self.llm.invoke(prompt)

    #En ocasiones el llm agrega "```sql" y "```" al inicio y al final, hay que quitarlo
    sql = respuesta.content.replace("```sql", "").replace("```", "")

    return sql

  #Analiza el resultado de una consulta
  def analizarDatos(
    self,
    datos = None,
    sql = None,
    prompt = None
  ):
    #Creamos una plantilla de prompt
    promptTemplate = PromptTemplate.from_template("""
      Eres un experto en analizar tablas de datos

      Esta es la consulta en lenguaje natural del usuario:

      {prompt}

      Esta es la consulta SQL que se usó:

      {sql}

      Estos son los datos que esa consulta generó:

      {datos}

      Responde en lenguaje natural la consulta del usuario
    """)

    #Creamos el prompt
    consulta = promptTemplate.format(
      datos = datos,
      prompt = prompt,
      sql = sql
    )

    #Invocamos el modelo
    respuesta = self.llm.invoke(consulta)

    return respuesta.content