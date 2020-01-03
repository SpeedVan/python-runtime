from plugin.reqres_handler_chain.chain import Chain
from plugin.reqres_handler_chain.reqres_handler import Handler
from flask import Flask

class RequestResponseHandlerChainPlugin(Flask):
    __slots__ = ()

    reqres_handler_chain = Chain()

    def __init__(self):
        self.before_request_funcs.setdefault(None, []).append(self.reqres_handler_chain.doBefore)
        self.after_request_funcs.setdefault(None, []).append(self.reqres_handler_chain.doAfter)
