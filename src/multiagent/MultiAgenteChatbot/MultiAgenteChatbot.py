#Importamos la configuración
from conf.conf import *

#Importamos los utilitarios
from util.util_ia_onpremise import *

## ################q######################################################################################
## @section Librerías
## #######################################################################################################

#Utilitario para crear una plantilla de prompt
from langchain_core.prompts import PromptTemplate

from multiagent.MultiAgenteChatbot.FlujoMultiAgenteChatbot import *
from multiagent.MultiAgenteChatbot.NodosMultiAgenteChatbot import *
from multiagent.MultiAgenteChatbot.ObjetosMultiAgenteChatbot import *

#Utilitario para convertir la estructura string a json
import json

## #######################################################################################################
## @section Clase
## #######################################################################################################

#Definición de clase
class MultiAgenteChatbot:

  #Instaciamos los objetos necesarios
  def __init__(
    self,
    llm = None,
    baseDeConocimientoDeUsuario = None,
    personalidad = None,
    condicionesDeContexto = None,
    reglasDeMemoriaDeLargoPlazo = None
  ):

    #Objetos del flujo multi-agente
    self.objetosMultiAgenteChatbot = ObjetosMultiAgenteChatbot(
      llm = llm,
      baseDeConocimientoDeUsuario = baseDeConocimientoDeUsuario,
      personalidad = personalidad,
      condicionesDeContexto = condicionesDeContexto,
      reglasDeMemoriaDeLargoPlazo = reglasDeMemoriaDeLargoPlazo
    )

    #Nodos del flujo multi-agente
    self.nodosMultiAgenteChatbot = NodosMultiAgenteChatbot(
      objetosMultiAgenteChatbot = self.objetosMultiAgenteChatbot
    )

    #Flujo multi-agente
    self.flujoMultiAgenteChatbot = FlujoMultiAgenteChatbot(
      nodosMultiAgenteChatbot = self.nodosMultiAgenteChatbot
    )

  #Ejecución
  def ejecutar(self, prompt):
    return self.flujoMultiAgenteChatbot.ejecutar(prompt)