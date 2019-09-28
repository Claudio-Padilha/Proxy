import time

class BufferData():                         # Objeto valor do dicionario. Precisamos da hora de entrada na cache    
    def __init__(self, time, data):
        self.time = time                    # Hora de entrada na cache
        self.data  = data                   # Dados de resposta

    def getHora(self):
        return self.time

    def getData(self):
        return self.data

class Cache():
    def __init__ (self, lock):
        self.buffer = {}                            # Dicionario representando a cache. Tem como chave a url e como valor uma instancia da classe bufferData
        self.size = 20000000                        # Capacidade total medida em bytes
        self.currentCapacity = 20000000             # Espaco disponivel atual
        self.lock = lock

    def getLock(self):
        return self.lock

    def addToCache(self, url, dictData):                  # dicData eh instancia de bufferData
        if (len(dictData.getData()) <= self.currentCapacity):
            self.buffer[url] = dictData
            self.currentCapacity -= len(dictData.getData())
        else:
            max = 0
            elem = ''

            while (len(dictData.getData()) <= self.currentCapacity):

                for e in self.buffer:
                    if self.buffer[e].getHora() > max:
                        max = self.buffer[e].getHora()
                        elem = e

                del(self.buffer[elem])

            self.buffer[url] = dictData
            self.currentCapacity -= len(dictData.getData())

    def removeFromCache(self, url):
        if url in self.buffer:
            self.currentCapacity += len(self.buffer[url].getData())
            del(self.buffer[url])

    def varrerCache(self, lock):
        
        while True:
            time.sleep(300)                             # Espera 5 min

            print("Varrendo cache.")

            hora = time.localtime()                     # Pega a hora local como int
            hora = time.strftime("%I:%M:%S %p", hora)
            hora = hora.replace(':', '')
            hora = hora.replace(' AM', '')
            hora = int(hora.replace(' PM', ''))
            
            lock.aquire()

            for e in self.buffer:
                if (hora - self.buffer[e].getHora()) > 299:
                    self.removeFromCache(e)

            lock.release()