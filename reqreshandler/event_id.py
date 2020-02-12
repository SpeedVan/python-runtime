import uuid

from plugin.reqres_handler_chain.reqres_handler import Handler
from flask import Request, Response


class EventIdHandler(Handler):

    def doBefore(self, req: Request) -> Request:
        self.event_id = req.headers.get("X-Faas-Event-Id", uuid.uuid4())
        req.X_Faas_Event_Id = self.event_id
        return req

    def doAfter(self, res: Response) -> Response:
        res.headers.remove("X-Faas-Event-Id")
        res.headers.add("X-Faas-Event-Id", self.event_id)
        return res
