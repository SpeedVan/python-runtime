import json
import os
import sys
import logging
import copy
import uuid
import datetime
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
from reqreshandler.event_id import EventIdHandler

logging.getLogger().setLevel(logging.DEBUG)
console_logger = logging.getLogger("__debug__")
# exec_logger = logging.getLogger("__main_exec__")
# func_logger = logging.getLogger("logger")
extra_data = {}

env_name = os.getenv("ENV_NAME", "")


class ExtEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Exception):
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%a, %d %b %Y %H:%M:%S GMT')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%a, %d %b %Y %H:%M:%S GMT')
        return json.JSONEncoder.default(self, obj)


class MyFlask(NCFeedbackPlugin, RequestResponseHandlerChainPlugin, FunctionLoaderPlugin, Flask):
    def __init__(self, module, config):
        # static_folder="/Users/admin/projects/github.com/SpeedVan/online-editor/build"
        static_folder="/userfunc/user/static"
        Flask.__init__(self, module, static_url_path = "", static_folder =static_folder)
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
        self.route("/", methods=["GET"])(lambda:self.send_static_file("index.html"))
        self.config["func"](self)
        self.reqres_handler_chain.appendHandler(RequestIdHandler()).appendHandler(
            TraceIdHandler()).appendHandler(EventIdHandler())
        self.notify_done(config["FREEBACK_CODE"])

    # def execute(self):
    #     try:
    #         func = self.config["func"]
    #         args = request.get_json()
    #         # if func._type == "orginal":
    #         # result = func(args)
    #         # else:
    #         result = func(**args)
    #         if isinstance(result, dict):
    #             return json.dumps(result, cls=ExtEncoder), 200, {"Content-Type": "application/json; charset=utf-8"}
    #         else:
    #             return str(result), 200, {"Content-Type": "application/text; charset=utf-8"}
    #     except TypeError as e:
    #         console_logger.error(str(e))
    #         return str(e), 400, {"Content-Type": "application/json; charset=utf-8"}
    #     except Exception as e:
    #         console_logger.error(str(e))
    #         return str(e), 500, {"Content-Type": "application/json; charset=utf-8"}

    def test(self):
        header = dict(map(lambda i: (i[0], i[1]), request.headers.items()))
        body_text = request.data.decode('utf-8')
        console_logger.debug(str(header))
        console_logger.debug(body_text)
        return body_text, 200, header


if __name__ == '__main__':
    config = {
        "BIND": "0.0.0.0:8888",
        "ENTRYPOINT": "/Users/admin/projects/go/src/github.com/SpeedVan/python-runtime/test_func/func_1.func",

        "FREEBACK_CODE": str(uuid.uuid4())
    }
    app = MyFlask(__name__, config)
    app.config["SERVER_NAME"] = config["BIND"]
    print(app.config)
    app.run(host='0.0.0.0', port='8888')
