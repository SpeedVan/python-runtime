import uuid

from plugin.reqres_handler_chain.reqres_handler import Handler
from flask import Request, Response


class TraceIdHandler(Handler):

    def doBefore(self, req: Request) -> Request:
        self.X_System_Trace_Id = req.headers.get(
            "X-System-Trace-Id", uuid.uuid4())
        req.X_System_Trace_Id = self.X_System_Trace_Id
        return req

    def doAfter(self, res: Response) -> Response:
        # res.headers.remove("Trace-Id")
        # res.headers.remove("X-Trace-Id")
        # res.headers.add("Trace-Id", self.trace_id)
        res.headers.add("X-System-Trace-Id", self.X_System_Trace_Id)
        return res
