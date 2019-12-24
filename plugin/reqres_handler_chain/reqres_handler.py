from abc import ABCMeta,abstractmethod
from flask import Request, Response

class Handler(metaclass=ABCMeta):
    @abstractmethod
    def doBefore(self, request:Request)->Request:
        pass

    @abstractmethod
    def doAfter(self, response:Response)->Response:
        pass

