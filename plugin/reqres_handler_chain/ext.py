from plugin.reqres_handler_chain.chain import Chain
from plugin.reqres_handler_chain.reqres_handler import Handler
from flask import Flask

def FlaskExt(app:Flask)->Flask:

    app.reqres_handler_chain:Chain = Chain()
    # def __init__(self, **kvargs):
    print("setup chain")
    app.before_request_funcs.setdefault(None, []).append(app.reqres_handler_chain.doBefore)
    app.after_request_funcs.setdefault(None, []).append(app.reqres_handler_chain.doAfter)
        # super.__init__(**kvargs)
    return app

        

# def appendReqresHander(self, h:Hander):
#     self.reqres_handler_chain.appendHandler(h)
#     return self