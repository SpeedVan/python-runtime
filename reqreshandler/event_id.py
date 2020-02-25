import uuid

from plugin.reqres_handler_chain.reqres_handler import Handler
from flask import Request, Response


class EventIdHandler(Handler):

    def doBefore(self, req: Request) -> Request:
        self.X_System_Event_Id = req.headers.get(
            "X-System-Event-Id", uuid.uuid4())
        req.X_System_Event_Id = self.X_System_Event_Id
        return req

    def doAfter(self, res: Response) -> Response:
        res.headers.remove("X-System-Event-Id")
        res.headers.add("X-System-Event-Id", self.X_System_Event_Id)
        return res
