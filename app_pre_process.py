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

from plugin.reqres_handler_chain.ext import FlaskExt
from plugin.netcat_notify.ext import FlaskExtNetcat
from reqreshandler.request_id import RequestIdHandler
from reqreshandler.trace_id import TraceIdHandler
from funcloader.loader import app_init_funcs

# logging.getLogger().setLevel(logging.DEBUG)
console_logger = logging.getLogger("__debug__")
# exec_logger = logging.getLogger("__main_exec__")
# func_logger = logging.getLogger("logger")
extra_data = {}

# env_name = os.getenv("ENV_NAME", "")

def init(a:Flask):
    
    app_init_funcs(a)
    a.reqres_handler_chain.appendHandler(RequestIdHandler()).appendHandler(TraceIdHandler())
    # a.start_notify()

# =================构建app===================

app = FlaskExtNetcat(FlaskExt(Flask(__name__)))

@app.route('/', methods=['POST'])
def execute():
    try:
        args = request.get_json()
        func = app.config['func']
        if func._type == "orginal":
            result = func(args)
        else:
            result = func(**args)
        return json.dumps({"code":"00000", "index":result, "msg":"ok"}), 200, {"Content-Type": "application/json; charset=utf-8"}
    except TypeError as e:
        console_logger.error(str(e))
        return json.dumps({"code":"error", "index":None, "msg":str(e)}), 400, {"Content-Type": "application/json; charset=utf-8"}
    except Exception as e:
        console_logger.error(str(e))
        return json.dumps({"code":"error", "index":None, "msg":str(e)}), 500, {"Content-Type": "application/json; charset=utf-8"}

@app.route('/params_struct', methods=['GET'])
def params_struct():
    try:
        func = app.config['func']
        if func._type == "orginal":
            result = {}
        else:
            result = func._params_struct
        return result, 200, {"Content-Type": "application/json; charset=utf-8"}
    except TypeError as e:
        console_logger.error(str(e))
        return str(e), 400, {"Content-Type": "application/json; charset=utf-8"}
    except Exception as e:
        console_logger.error(str(e))
        return str(e), 500, {"Content-Type": "application/json; charset=utf-8"}

@app.route('/result_struct', methods=['GET'])
def result_struct():
    try:
        func = app.config['func']
        if func._type == "orginal":
            result = {}
        else:
            result = func._result_struct
        return result, 200, {"Content-Type": "application/json; charset=utf-8"}
    except TypeError as e:
        console_logger.error(str(e))
        return str(e), 400, {"Content-Type": "application/json; charset=utf-8"}
    except Exception as e:
        console_logger.error(str(e))
        return str(e), 500, {"Content-Type": "application/json; charset=utf-8"}

# =================测试连通性及数据传达情况接口==============

@app.route('/test', methods=['POST'])
def test():
    header = dict(map(lambda i:(i[0],i[1]), request.headers.items()))
    body_text = request.data.decode('utf-8')
    console_logger.debug(str(header))
    console_logger.debug(body_text)
    return body_text, 200, header

init(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv("PROXY_PORT", '8888'))