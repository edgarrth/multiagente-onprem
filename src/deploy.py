from conf.conf import *
from util.util_ia_onpremise import *

##CREACIÓN DE BASE DE DATOS

print("Creando base de datos...")

#Creando base de datos
crearBaseDeDatosDePrueba(
  rutaDeBaseDeDatos = CONF_BASE_DE_DATOS_RUTA
)

## Section CREACIÓN DE BASE DE CONOCIMIENTO


print("Creando base de conocimiento...")

#Cargamos el documento del CURSO 1
insertarEnBaseDeConocimiento(
  rutaDeDocumento = CONF_DIRECTORIO_RECURSOS / "DOCUMENTOS/CURSO_1.pdf",
  nombreDeBaseDeConocimiento = CONF_BASE_DE_CONOCIMIENTO_NOMBRE,
  rutaDeBaseDeConocimiento = CONF_BASE_DE_CONOCIMIENTO_RUTA
)

#Cargamos el documento del CURSO 2
insertarEnBaseDeConocimiento(
  rutaDeDocumento = CONF_DIRECTORIO_RECURSOS / "DOCUMENTOS/CURSO_2.pdf",
  nombreDeBaseDeConocimiento = CONF_BASE_DE_CONOCIMIENTO_NOMBRE,
  rutaDeBaseDeConocimiento = CONF_BASE_DE_CONOCIMIENTO_RUTA
)


## section CARGA DEL MODELO A LA VRAM

#Obtenemos al modelo
llm = obtenerModelo()