import uuid

from plugin.reqres_handler_chain.reqres_handler import Handler
from flask import Request, Response

class TraceIdHandler(Handler):

    def doBefore(self, req:Request)->Request:
        self.trace_id = req.headers.get("X-Trace-Id", req.headers.get("Trace-Id", uuid.uuid4()))
        req.X_Trace_Id = self.trace_id
        return req

    def doAfter(self, res:Response)->Response:
        # res.headers.remove("Trace-Id")
        # res.headers.remove("X-Trace-Id")
        # res.headers.add("Trace-Id", self.trace_id)
        res.headers.add("X-Trace-Id", self.trace_id)
        return res