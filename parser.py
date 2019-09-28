class Parser:    
    def parseRequest (self, request):
        first_line = request.split('\r')[0]
        url = first_line.split(' ')[1]
        connectionMethod = first_line.split(' ')[0].replace("b'", "")
        connectionMethod = connectionMethod.replace("b''","")

        return url, connectionMethod

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