from plugin.reqres_handler_chain.reqres_handler import Handler
from flask import request


class Chain:
    c: [Handler] = []

    def appendHandler(self, h: Handler):
        self.c.append(h)
        return self

    def doBefore(self):
        print("chain doBefore")
        # chain(self.c)
        req = request
        print(req.headers)
        for h in self.c:
            req = h.doBefore(req)

    def doAfter(self, response):
        print("chain doAfter")
        for h in reversed(self.c):
            response = h.doAfter(response)
        return response
