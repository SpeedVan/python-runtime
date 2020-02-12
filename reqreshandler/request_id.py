import uuid

from plugin.reqres_handler_chain.reqres_handler import Handler
from flask import Request, Response


class RequestIdHandler(Handler):

    def doBefore(self, req: Request) -> Request:
        if hasattr(self, "request_id"):
            print("old RequestIdHandler.request_id:"+str(self.request_id))
        if hasattr(req, "X_Faas_Request_Id"):
            print(req.X_Faas_Request_Id)
        self.request_id = req.headers.get("X-Faas-Request-Id", uuid.uuid4())
        # request.headers.remove("X-Request-Id")
        req.X_Faas_Request_Id = self.request_id
        return req

    def doAfter(self, res: Response) -> Response:
        res.headers.remove("X-Faas-Request-Id")
        res.headers.add("X-Faas-Request-Id", self.request_id)
        return res
