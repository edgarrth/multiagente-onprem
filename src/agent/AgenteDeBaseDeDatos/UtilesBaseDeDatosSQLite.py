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

#Utilitario para rutas
from pathlib import Path

#Definimos una clase
class UtilesBaseDeDatosSQLite:

  #Definimos el constructor
  def __init__(
      self,
      rutaDeBaseDeDatos = None
  ):
    self.rutaDeBaseDeDatos = rutaDeBaseDeDatos

  #Función utilitaria para obtener las tablas de una base de datos
  def obtenerTablas(
    self
  ):
    #Creamos una base de datos de prueba
    conexion = sqlite3.connect(self.rutaDeBaseDeDatos)

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
    self,
    tabla = None
  ):
    #Columnas de una tabla
    #Dentro, para cada columna, se indicará en un JSON:
    #
    # - nombreDeColumna: Nombre de la columna
    # - tipoDeDatoDeColumna: Tipo de dato de la columna
    columnasDeTabla = []

    #Creamos una base de datos de prueba
    conexion = sqlite3.connect(self.rutaDeBaseDeDatos)

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
    self
  ):
    #Nombres de tablas, e información de todos las columnas
    esquema = {}

    #Lo haremos en bucle para todas las tablas
    #Obtenemos las tablas
    tablas = self.obtenerTablas()

    #Iteramos todas las tablas
    for tabla in tablas:
      #Obtenemos la información de los campos
      informacion = self.obtenerInformacionDeColumnasDeTabla(
        tabla = tabla
      )

      #Asignamos el esquema a la tabla
      esquema[tabla] = informacion

    return esquema

  #Función para ejecutar una consulta en la base de datos
  def ejecutarConsulta(
    self,
    sql = None
  ):
    #Creamos una base de datos de prueba
    conexion = sqlite3.connect(self.rutaDeBaseDeDatos)

    #Creamos un cursor que consulte a la base de datos
    cursor = conexion.cursor()

    #Ejecutamos la consulta
    cursor.execute(sql)

    #Obtenemos los resultados
    resultados = cursor.fetchall()

    return resultados