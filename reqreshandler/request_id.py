import uuid

from plugin.reqres_handler_chain.reqres_handler import Handler
from flask import Request, Response


class RequestIdHandler(Handler):

    def doBefore(self, req: Request) -> Request:
        self.X_System_Request_Id = req.headers.get(
            "X-System-Request-Id", uuid.uuid4())
        # request.headers.remove("X-Request-Id")
        req.X_System_Request_Id = self.X_System_Request_Id
        return req

    def doAfter(self, res: Response) -> Response:
        res.headers.remove("X-System-Request-Id")
        res.headers.add("X-System-Request-Id", self.X_System_Request_Id)
        return res
