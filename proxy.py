import socket
import _thread
import sys
import datetime
import time
from cache import *
from threading import Lock
from log import *

class ProxyServer():
   def __init__ (self, porta, blacklist, cache, log):
      self.porta = porta
      self.blacklist = blacklist
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.sock.bind(('', self.porta))
      self.cache = cache
      self.log = log
      self.log.inicializarLog()

   def escutar(self):
      self.sock.listen(50)

      _thread.start_new_thread(self.cache.varrerCache, (self.cache.getLock(),))               # thread para varrer a cache de 5 em 5 minutos

      while True:
         clientSocket, endereco = self.sock.accept()
         self.log.escreverNoLog("Conexao com %s foi estabelecida!" % str(tuple(endereco)))

         _thread.start_new_thread(self.executarProxy, (clientSocket, endereco, self.blacklist))

      self.sock.close()

   def executarProxy(self, clientSocket, endereco, blacklist):
      # Requisicao do servidor
      data = clientSocket.recv(999999)
      request = str(data)

      if (request == ""):
         self.log.escreverNoLog("Requisicao Invalida! Fechando socket com cliente...")
         clientSocket.close()
         sys.exit(1)

      # Parse request
      first_line = request.split('\n')[0]
      url = first_line.split(' ')[1]
      connectionMethod = first_line.split(' ')[0].replace("b'", "")
      connectionMethod = connectionMethod.replace("b''","")

      if (connectionMethod == "GET" or connectionMethod == "CONNECT"):
         webserver, port = self.getAddress(url)

         # Procurar se url esta na blacklist
         if webserver in blacklist:
            self.log.escreverNoLog("%s - URL não pode ser acessada!" % webserver)
            clientSocket.close()
            sys.exit(1)
         # Procurar dados na cache
         elif webserver in self.cache.buffer:
            self.log.escreverNoLog("%s - Dados sem autoridade (Recebido da cache)!" % webserver)
            clientSocket.send(self.cache.buffer[webserver].getData())
         # Necessario buscar no servidor
         else:
            serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverSock.connect((webserver, port))

            try:
               serverSock.send(data)               # Envia a requisicao ao servidor
            except socket.error as ex:
               print (ex)

            hora = time.localtime()                     # Pega a hora local como int
            hora = time.strftime("%I:%M:%S %p", hora)
            hora = hora.replace(':', '')
            hora = hora.replace(' AM', '')
            hora = int(hora.replace(' PM', ''))

            dicData = BufferData(hora, data)
            self.cache.addToCache(webserver, dicData)

            while True:                         # Recebe a resposta em "pedacos" de 8192 bytes
               reply = serverSock.recv(8192)
               if len(reply) > 0:
                  clientSocket.send(reply)     
               else:
                  break

            serverSock.close()

      else:
         self.log.escreverNoLog("SERVER ERROR - NOT IMPLEMENTED (502): %s" % connectionMethod)
         clientSocket.close()
         sys.exit(1)
   
   def getWebserver(self, url):
      # Remover http:// se existir
      httpPos = url.find("://")
      if (httpPos == -1):
         webserver = url
      else:
         webserver = url[(httpPos + 3):]

      # Remover caminho do servidor se existir (google.com/fotos)
      webserverEnd = webserver.find("/")
      if (webserverEnd == -1):
         webserverEnd = len(webserver)

      return webserver[:webserverEnd]

   def getPort(self, url):
      portBegin = url.find(":")

      port = -1
      if (portBegin == -1):
         port = 80
      else:
         temp = url[portBegin + 1:]
         port = int(temp)
      
      return port

   def getAddress(self, url):
      webserver = self.getWebserver(url)
      port = self.getPort(webserver)

      portString = ":" + str(port)

      webserver = webserver.replace(portString, "")

      return (webserver, port)     

def atribuirPorta():
   if (len(sys.argv) >= 2):
      argumentos = sys.argv[1]
      nomeArg = argumentos[:3]

      if (nomeArg == '-p='): 
         porta = argumentos
         porta = int(porta[-4:])
         return porta
   
   print("Nenhuma porta selecionada. Escolhendo :8080")
   return 8080

if __name__ == "__main__":


   arq = open(sys.argv[2], 'r')

   blacklist = arq.readlines()

   porta = atribuirPorta()

   lock = Lock()
   cache = Cache(lock)

   LOG = "log.txt"
   log = Log(LOG, porta)
   proxyServer = ProxyServer(porta, blacklist, cache, log)

   proxyServer.escutar()