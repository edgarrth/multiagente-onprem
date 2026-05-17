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

class FlujoMultiAgenteChatbot:

  #Instaciamos los objetos necesarios
  def __init__(
    self,
    nodosMultiAgenteChatbot = None
  ):
    #Nodos del flujo
    self.nodosMultiAgenteChatbot = nodosMultiAgenteChatbot

    #Indicamos desde que nodo se inicia la ejecución del grafo
    self.nodosMultiAgenteChatbot.constructor.set_entry_point("node_a1_agenteDeContexto")

    #Agregamos un flujo condicional
    self.nodosMultiAgenteChatbot.constructor.add_conditional_edges("node_a1_agenteDeContexto", lambda state: state["node_a1_agenteDeContexto"]["status"], {
        "PROMPT_VALIDO": "node_a3_agenteDeMemoriaLargoPlazo",
        "PROMPT_NO_VALIDO": "node_a2_promptNoValido"
    })

    #Agregamos un flujo condicional
    self.nodosMultiAgenteChatbot.constructor.add_conditional_edges("node_a3_agenteDeMemoriaLargoPlazo", lambda state: state["node_a3_agenteDeMemoriaLargoPlazo"]["estado"], {
        "INFORMACION_POR_RECORDAR": "node_a4_informacionPorRecordar",
        "NO_SE_DETECTO_INFORMACION_POR_RECORDAR": "node_a5_agenteDeChatbot"
    })

    #Conectamos un flujo secuencial
    self.nodosMultiAgenteChatbot.constructor.add_edge("node_a4_informacionPorRecordar", "node_a5_agenteDeChatbot")

    #Indicamos los nodos en donde finaliza el grafo
    self.nodosMultiAgenteChatbot.constructor.set_finish_point("node_a2_promptNoValido")
    self.nodosMultiAgenteChatbot.constructor.set_finish_point("node_a5_agenteDeChatbot")

    #Construimos el grafo
    self.grafo = self.nodosMultiAgenteChatbot.constructor.compile()

  #Ejecución
  def ejecutar(self, prompt):

    #Ejecutamos el grafo
    respuesta = self.grafo.invoke(
      {"prompt": prompt}
    )

    #Devolvemos la respuesta
    return respuesta["output"]["respuesta"]