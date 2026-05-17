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

#Utilitario para crear grafos
from langgraph.graph import StateGraph

## #######################################################################################################
## @section Clase
## #######################################################################################################

#Definición de clase
class NodosMultiAgenteChatbot:

  #Instaciamos los objetos necesarios
  def __init__(
    self,
    objetosMultiAgenteChatbot = None
  ):
    #Objetos del flujo
    self.objetosMultiAgenteChatbot = objetosMultiAgenteChatbot

    #Nodo de Agente de Contexto
    def node_a1_agenteDeContexto(state: dict) -> dict:
      #Definimos la salida
      output = state
      output["node_a1_agenteDeContexto"] = {}

      #Imprimimos un mensaje para saber en qué nodo estamos
      print("Ejecutando node_a1_agenteDeContexto...")

      #Obtenemos los parámetros
      prompt = state["prompt"]

      #Ejecutamos el agente
      respuesta = self.objetosMultiAgenteChatbot.agenteDeContexto.ejecutar(prompt)

      #Normalizamos estados inesperados para evitar rutas invalidas
      if respuesta.get("status") not in {"PROMPT_VALIDO", "PROMPT_NO_VALIDO"}:
        respuesta = {
          "status": "PROMPT_NO_VALIDO",
          "message": respuesta.get("message", "Respuesta invalida del modelo")
        }

      #Construimos la salida
      output["node_a1_agenteDeContexto"] = respuesta

      #Devolvemos la salida
      return output

    #Nodo de prompt no valido
    def node_a2_promptNoValido(state: dict) -> dict:
      #Definimos la salida
      output = state
      output["output"] = {}

      #Imprimimos un mensaje para saber en qué nodo estamos
      print("Ejecutando node_a2_promptNoValido...")

      #Ejecutamos el agente
      respuesta = state["node_a1_agenteDeContexto"]["message"]

      #Construimos la salida
      output["output"]["respuesta"] = respuesta

      #Devolvemos la salida
      return output

    #Nodo de Agente de Memoria a Largo Plazo
    def node_a3_agenteDeMemoriaLargoPlazo(state: dict) -> dict:
      #Definimos la salida
      output = state
      output["node_a3_agenteDeMemoriaLargoPlazo"] = {}

      #Imprimimos un mensaje para saber en qué nodo estamos
      print("Ejecutando node_a3_agenteDeMemoriaLargoPlazo...")

      #Obtenemos los parámetros
      prompt = state["prompt"]

      #Ejecutamos el agente
      respuesta = self.objetosMultiAgenteChatbot.agenteDeMemoriaLargoPlazo.ejecutar(prompt)

      #Normalizamos estados inesperados para evitar rutas invalidas
      if respuesta.get("estado") not in {"INFORMACION_POR_RECORDAR", "NO_SE_DETECTO_INFORMACION_POR_RECORDAR"}:
        respuesta = {
          "estado": "NO_SE_DETECTO_INFORMACION_POR_RECORDAR",
          "message": respuesta.get("message", "Respuesta invalida del modelo")
        }

      #Construimos la salida
      output["node_a3_agenteDeMemoriaLargoPlazo"] = respuesta

      #Devolvemos la salida
      return output

    #Nodo de información por recordar
    def node_a4_informacionPorRecordar(state: dict) -> dict:
      #Definimos la salida
      output = state
      output["node_a4_informacionPorRecordar"] = {}

      #Imprimimos un mensaje para saber en qué nodo estamos
      print("Ejecutando node_a4_informacionPorRecordar...")

      #Obtenemos la información actual del usuario
      informacionDeUsuario = leerBaseDeConocimientoDeUsuario(
        baseDeConocimientoDeUsuario = self.objetosMultiAgenteChatbot.baseDeConocimientoDeUsuario
      )

      #Obtenemos los parámetros
      informacionPorRecordar = state["node_a3_agenteDeMemoriaLargoPlazo"]["informacion"]

      #Combinamos la información
      informacionCombinada = informacionDeUsuario + "\n" + informacionPorRecordar

      #Damos coherencia a la información
      informacionCoherente = self.objetosMultiAgenteChatbot.agenteDeAnalisis.ejecutar(informacionCombinada)

      #Escribimos la nueva información del usuario en su base de conocimiento
      actualizarBaseDeConocimientoDeUsuario(
        baseDeConocimientoDeUsuario = self.objetosMultiAgenteChatbot.baseDeConocimientoDeUsuario,
        contenido = informacionCoherente["textoCoherente"]
      )

      #Devolvemos la salida
      return output

    #Nodo de Agente de Chatbot
    def node_a5_agenteDeChatbot(state: dict) -> dict:
      #Definimos la salida
      output = state
      output["output"] = {}

      #Imprimimos un mensaje para saber en qué nodo estamos
      print("Ejecutando node_a5_agenteDeChatbot...")

      #Obtenemos los parámetros
      prompt = state["prompt"]

      #Ejecutamos el agente
      respuesta = self.objetosMultiAgenteChatbot.agenteDeChatbot.ejecutar(prompt)

      #Construimos la salida
      output["output"]["respuesta"] = respuesta

      #Devolvemos la salida
      return output

    #Construimos un grafo que recibe JSONs
    self.constructor = StateGraph(dict)

    #Agregamos los nodos dentro del grafo
    self.constructor.add_node("node_a1_agenteDeContexto", node_a1_agenteDeContexto)
    self.constructor.add_node("node_a2_promptNoValido", node_a2_promptNoValido)
    self.constructor.add_node("node_a3_agenteDeMemoriaLargoPlazo", node_a3_agenteDeMemoriaLargoPlazo)
    self.constructor.add_node("node_a4_informacionPorRecordar", node_a4_informacionPorRecordar)
    self.constructor.add_node("node_a5_agenteDeChatbot", node_a5_agenteDeChatbot)