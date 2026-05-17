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

class AgenteDeChatbot:

  #Definimos el constructor
  def __init__(
      self,
      llm = None,
      contexto = None,
      nombreBaseDeConocimiento = None,
      rutaBaseDeConocimiento = None
  ):
    #ATRIBUTOS
    self.llm = llm
    self.contexto = contexto
    self.nombreBaseDeConocimiento = nombreBaseDeConocimiento
    self.rutaBaseDeConocimiento = rutaBaseDeConocimiento

    #OBJETOS NECESARIOS
    self.memoriaCortoPlazo = crearMemoriaCortoPlazo(
        contexto = contexto
    )

  #Ejecutar el agente
  def ejecutar(self, prompt):
    respuesta = None

    #Si hay base de conocimiento
    if (
      (self.nombreBaseDeConocimiento is not None) and
      (self.nombreBaseDeConocimiento is not None)
    ):
      #Enviamos el mensaje agregandole contexto desde la base de conocimiento
      respuesta = enviarMensajeAlModeloConContextoDeBaseDeConocimiento(
        llm = self.llm,
        memoriaCortoPlazo = self.memoriaCortoPlazo,
        mensaje = prompt,
        nombreBaseDeConocimiento = self.nombreBaseDeConocimiento,
        rutaBaseDeConocimiento = self.nombreBaseDeConocimiento
      )
    else:
      #Enviamos el mensaje sin contexto de base de conocimiento
      respuesta = enviarMensajeAlModelo(
        llm = self.llm,
        memoriaCortoPlazo = self.memoriaCortoPlazo,
        mensaje = prompt
      )

    #Devolvemos la respuesta
    return respuesta