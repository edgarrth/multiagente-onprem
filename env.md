# Variables de entorno sugeridas

Este proyecto lee su configuracion desde `src/conf/conf.py`. Si deseas parametrizar por entorno, puedes usar este archivo como guia.

```dotenv
# Nombre del proyecto
CONF_NOMBRE_PROYECTO="Agente On Premise"

# Modelos Ollama
CONF_MODEL="gpt-oss:20b"
CONF_MODEL_EMBEDDING="nomic-embed-text"

# Servicio Ollama
CONF_SERVICE="http://localhost:11434"
CONF_KEEP_ALIVE=10800

# Base de conocimiento (Chroma)
CONF_BASE_DE_CONOCIMIENTO_NOMBRE="bc_enterprise"
CONF_BASE_DE_CONOCIMIENTO_RUTA="resources/content/bc_enterprise"
CONF_BASE_DE_CONOCIMIENTO_COINCIDENCIAS_MAXIMAS=100

# Base de datos SQLite
CONF_BASE_DE_DATOS_RUTA="resources/content/enterprise.db"

# Memoria de usuarios
CONF_BASE_DE_CONOCIMIENTO_USUARIOS="resources/content/bc_usuarios"

# Reportes
CONF_RUTA_REPORTES="resources/content/reportes"
```

Notas:
- Estos valores reflejan los defaults actuales en `src/conf/conf.py`.
- Si quieres que el proyecto los lea automaticamente desde un `.env`, puedo agregar esa lectura.

