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

env_name = os.getenv("ENV_NAME", "")

def init(a:Flask):
    # env_name = os.getenv("ENV_NAME", "__no_function_name__")
    func_config = os.getenv("FUNC_CONFIG", "{}")
    try:
        func_json = json.loads(func_config)
    except json.JSONDecodeError:
        func_json = {}

    a.config['func_json'] = func_json
    
    app_init_funcs(a)
    a.reqres_handler_chain.appendHandler(RequestIdHandler()).appendHandler(TraceIdHandler())
    a.start_notify()

# =================构建app===================

app = FlaskExtNetcat(FlaskExt(Flask(__name__)))

@app.route('/<env_name>/<func_name>', methods=['POST'])
def execute(env_name, func_name):
    try:
        args = request.get_json()
        func = app.config['func_cache'][func_name]
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

@app.route('/<env_name>/<func_name>/params_struct', methods=['GET'])
def params_struct(env_name, func_name):
    func = app.config['func_cache'][func_name]
    return func._params_struct

@app.route('/<env_name>/<func_name>/result_struct', methods=['GET'])
def result_struct(env_name, func_name):
    func = app.config['func_cache'][func_name]
    return func._result_struct

# ================在没有支持多环境前使用的接口=================

@app.route('/<func_name>', methods=['POST'])
def default_env_execute(func_name):
    return execute(env_name, func_name)

@app.route('/<func_name>/params_struct', methods=['GET'])
def default_env_params_struct(func_name):
    return params_struct(env_name, func_name)

@app.route('/<func_name>/result_struct', methods=['GET'])
def default_env_result_struct(func_name):
    return result_struct(env_name, func_name)

# =================兼容旧router下通常接口==================

@app.route('/', methods=['POST'])
def old_execute():
    func_name = request.headers.get("Function-Name", "")
    return execute(env_name, func_name)

@app.route('/params_struct', methods=['GET'])
def old_params_struct(func_name):
    func_name = request.headers.get("Function-Name", "")
    return params_struct(env_name, func_name)

@app.route('/result_struct', methods=['GET'])
def old_result_struct(func_name):
    func_name = request.headers.get("Function-Name", "")
    return result_struct(env_name, func_name)

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