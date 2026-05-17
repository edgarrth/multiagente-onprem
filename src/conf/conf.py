#Utilitario para obtener ruta
from pathlib import Path

#Directorio de recursos del proyecto
CONF_DIRECTORIO_RECURSOS = Path(__file__).resolve().parents[2] / "resources"
print("RUTA DE RECURSOS DEL PROYECTO:")
print(CONF_DIRECTORIO_RECURSOS)

#Nombre del proyecto
CONF_NOMBRE_PROYECTO = "Agente On Premise"

#Identificador del modelo que queremos usar
#CONF_MODEL = "gpt-oss:20b"
CONF_MODEL = "llama3.1:latest "
#Identificador del modelo de embedding que queremos usar
CONF_MODEL_EMBEDDING = "nomic-embed-text"

#Puerto por donde el servicio escucha
CONF_SERVICE = "http://localhost:11434"

#Cantidad de tiempo (en segundos) que vive el modelo en la RAM/VRAM
CONF_KEEP_ALIVE = 10800

#Nombre de la base de conocimiento
CONF_BASE_DE_CONOCIMIENTO_NOMBRE = "bc_enterprise"

#Ruta de la base de conocimiento
CONF_BASE_DE_CONOCIMIENTO_RUTA = CONF_DIRECTORIO_RECURSOS / "content/bc_enterprise"

#Cantidad de coincidencias máximas en la base de conocimiento
CONF_BASE_DE_CONOCIMIENTO_COINCIDENCIAS_MAXIMAS = 100

#Ruta de la base de datos
CONF_BASE_DE_DATOS_RUTA = CONF_DIRECTORIO_RECURSOS / "content/enterprise.db"

#Lo usaremos como base de conocimiento de información de cada usuario
CONF_BASE_DE_CONOCIMIENTO_USUARIOS = CONF_DIRECTORIO_RECURSOS / "content/bc_usuarios"

#Ruta de reportes generados
CONF_RUTA_REPORTES = CONF_DIRECTORIO_RECURSOS / "content/reportes"