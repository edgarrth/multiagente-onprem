from multiagent.MultiAgenteChatbot.MultiAgenteChatbot import *


#Obtenemos al modelo
llm = obtenerModelo()

#Construimos el flujo multi-agente
multiAgenteChatbot = MultiAgenteChatbot(
  llm = llm,
  baseDeConocimientoDeUsuario = "armg",
  personalidad = """
    Eres un asistente llamado "ArquiBot" que atenderá consultas de alumnos para cursos, de
      formación de cursos de Arquitectura de soluciones y empresarial. Al contestar debes
      seguir las siguientes reglas:

      1. Debes contestar en un lenguaje formal pero amigable
      2. Debes de usar emojis al responder
  """,
  condicionesDeContexto = """
    Como mínimo debe cumplirse estas condiciones:

      - Es un mensaje relacionado a lo que se esperaría en una conversación
      - Es un mensaje que no contiene palabras groseras o que se consideren faltas de respeto
      - Es un mensaje con un tema que una academia que dicta cursos esperaría recibir
  """,
  reglasDeMemoriaDeLargoPlazo = """
    - El nombre del usuario
    - La edad del usuario
    - El sexo del usuario
  """
)

#Ejecutamos
respuesta = multiAgenteChatbot.ejecutar(
  prompt = """
    Buenos días
  """
)

#Verificamos
print(respuesta)