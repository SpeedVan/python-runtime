import json
import os
import sys
import logging
import copy
import uuid
from functools import wraps
from inspect import signature
from typing import NewType

from flask_restful import Api
from flask import Flask, request, jsonify, abort, g
from loggerconfig import setup_main_logger, setup_logger

from plugin.reqres_handler_chain import RequestResponseHandlerChainPlugin
from plugin.netcat_notify import NCFeedbackPlugin
from plugin.function_loader import FunctionLoaderPlugin
from reqreshandler.request_id import RequestIdHandler
from reqreshandler.trace_id import TraceIdHandler

logging.getLogger().setLevel(logging.DEBUG)
console_logger = logging.getLogger("__debug__")
# exec_logger = logging.getLogger("__main_exec__")
# func_logger = logging.getLogger("logger")
extra_data = {}

env_name = os.getenv("ENV_NAME", "")

class MyFlask(NCFeedbackPlugin, RequestResponseHandlerChainPlugin, FunctionLoaderPlugin, Flask):
    def __init__(self, module, config):
        Flask.__init__(self, module)
        NCFeedbackPlugin.__init__(self)
        FunctionLoaderPlugin.__init__(self)
        RequestResponseHandlerChainPlugin.__init__(self)
        # func_config = os.getenv("FUNC_CONFIG", "{}")
        # try:
        #     func_json = json.loads(func_config)
        # except json.JSONDecodeError:
        #     func_json = {}

        # self.config['func_json'] = func_json
        # app_init_funcs(a)
        # for k, v in config.items():
        #     self.config[k] = v
        self.load_function(config["ENTRYPOINT"])
        self.route("/", methods=["POST"])(self.execute)
        self.route("/test", methods=["POST"])(self.test)
        self.reqres_handler_chain.appendHandler(RequestIdHandler()).appendHandler(TraceIdHandler())
        self.notify_done(config["FREEBACK_CODE"])

    def execute(self):
        try:
            func = self.config["func"]
            args = request.get_json()
            # if func._type == "orginal":
                # result = func(args)
            # else:
            result = func(**args)
            return str(result), 200, {"Content-Type": "application/json; charset=utf-8"}
        except TypeError as e:
            console_logger.error(str(e))
            return str(result), 400, {"Content-Type": "application/json; charset=utf-8"}
        except Exception as e:
            console_logger.error(str(e))
            return str(result), 500, {"Content-Type": "application/json; charset=utf-8"}

    def test(self):
        header = dict(map(lambda i:(i[0],i[1]), request.headers.items()))
        body_text = request.data.decode('utf-8')
        console_logger.debug(str(header))
        console_logger.debug(body_text)
        return body_text, 200, header

if __name__ == '__main__':
    config = {
        "ENTRYPOINT": "/Users/admin/projects/go/src/github.com/SpeedVan/python-runtime/test_func/func_1.func",

        "FREEBACK_CODE": str(uuid.uuid4())
    }
    app = MyFlask(__name__, config)
    app.config["SERVER_NAME"]="0.0.0.0:8888"
    print(app.config)
    app.run(host='0.0.0.0', port='8888')