#Importamos la configuración
from conf.conf import *

#Importamos los utilitarios
from util.util_ia_onpremise import *

#Importamos los agentes necesarios
from agent.AgenteDeAnalisis import *
from agent.AgenteDeChatbot import *
from agent.AgenteDeContexto import *
from agent.AgenteDeMemoriaLargoPlazo import *
from agent.AgenteDeVisualizacion import *
from agent.AgenteGenerativo import *

## ################q######################################################################################
## @section Librerías
## #######################################################################################################

#Utilitario para crear una plantilla de prompt
from langchain_core.prompts import PromptTemplate

#Utilitario para convertir la estructura string a json
import json

## #######################################################################################################
## @section Clase
## #######################################################################################################

#Definición de clase
class ObjetosMultiAgenteChatbot:

  #Instaciamos los objetos necesarios
  def __init__(
    self,
    llm = None,
    baseDeConocimientoDeUsuario = None,
    personalidad = None,
    condicionesDeContexto = None,
    reglasDeMemoriaDeLargoPlazo = None
  ):
    #Modelo
    self.llm = llm

    #Creamos un agente de contexto
    #Es el que verifica que el mensaje cumpla las condiciones
    self.agenteDeContexto = AgenteDeContexto(
      llm = llm,
      condiciones = condicionesDeContexto
    )

    #Creamos un agente de memoria a largo plazo
    #Es el que veriica si hay o no información por recordar
    self.agenteDeMemoriaLargoPlazo = AgenteDeMemoriaLargoPlazo(
      llm = llm,
      condiciones = reglasDeMemoriaDeLargoPlazo
    )

    #Creamos el agente de analisis
    #Es el que dara coherencia a la información que el usuario afirma, con lo que tenemos en su base de conocimiento
    self.agenteDeAnalisis = AgenteDeAnalisis(
      llm = llm,
      descripcion = """
        Para un texto, si hay informacion que se contradicen entre sí
        trata de darle coherencia, quedandote con la información más reciente,
        dentro del texto. Sólo dame las lineas de este texto
        según las indicaciones que te di en la variable json "textoCoherente"
        Esta variable "textoCoherente" es del tipo "str", si ha varias líneas,
        sepáralas con un enter
      """
    )

    #Almacenamos el nombre de la base de conocimiento del usuario
    self.baseDeConocimientoDeUsuario = baseDeConocimientoDeUsuario

    #Leemos la información actual del usuario desde su base de conocimiento
    self.informacionDeUsuario = leerBaseDeConocimientoDeUsuario(
        baseDeConocimientoDeUsuario = baseDeConocimientoDeUsuario
    )

    #Creamos un agente de chatbot
    self.agenteDeChatbot = AgenteDeChatbot(
      llm = llm,
      contexto = f"""
        {personalidad}

        También considera esta información del usuario:

        {self.informacionDeUsuario}
      """
    )