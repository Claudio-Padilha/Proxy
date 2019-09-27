def inicializarLog(self):
      self.log = open(LOG, "w")     # w cria ficheiro caso nao exista e sobrescreve caso exista (apaga o conteudo)
      self.log.write("Proxy Iniciado em: localhost - %d" % self.porta)
      self.log.write("\n")
      self.log.write("Server Time: %s" % datetime.datetime.now())
      self.log.write("\n")
      self.log.write("------------------------------------------------------")
      self.log.write("\n")
      self.log.write("\n")
      self.log.close()

   def escreverNoLog(self, string):
      self.log = open(LOG, "a")     # Apende texto no final do arquivo
      self.log.write(string)
      self.log.write("\n")
      self.log.close()