from plugin.netcat_notify.netcat import Client
from flask import Flask

class NCFeedbackPlugin(Flask):
    __slots__ = ()

    initailized = False

    def __init__(self):
        try:
            self.nc = Client()
            self.initailized = True
        except Exception:
            print("NCFeedbackPlugin initail fail, will skip notify.")


    def notify_done(self, msg):
        if self.initailized == True:    
            try:
                self.nc.write(msg+"\n")
            except Exception as e:
                print(str(e))
            finally:
                if self.nc != None:
                    self.nc.close()