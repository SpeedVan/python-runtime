import socket

from flask import Flask

class Netcat:

    """ Netcat local client for notify """
    
    def __init__(self, ip="127.0.0.1", port=2018):
        self.buff = b""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))

    def read(self, length = 1024):

        """ Read 1024 bytes off the socket """

        return self.socket.recv(length)
 
    def read_until(self, data):

        """ Read data into the buffer until we have data """

        while not data in self.buff:
            self.buff += self.socket.recv(1024)
 
        pos = self.buff.find(data)
        rval = self.buff[:pos + len(data)]
        self.buff = self.buff[pos + len(data):]
 
        return rval
 
    def write(self, data):
        self.socket.send(data)
        return self
    
    def close(self):
        self.socket.close()
        return self

def done():
    nc = None
    try:
        nc = Netcat()
        nc.write(b"done\n")
    except Exception as e:
        print(str(e))
    finally:
        if nc != None:
            nc.close()

def FlaskExtNetcat(app:Flask)->Flask:
    app.start_notify = done
    return app