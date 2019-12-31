import sys
import copy
import logging
from inspect import signature
from flask import Flask

console_logger = logging.getLogger("__debug__")

def app_init_funcs(app:Flask, sys_path, entrypoint):
    app.config['func']=load(sys_path, entrypoint)
    


def load(sys_path, entrypoint):
    # try: 注释try，达到只要有一个加载失败，外抛异常
        sys.path.append(sys_path)
        moduleName, funcName = entrypoint.rsplit(".", 1)
        obj = __import__(moduleName, fromlist=funcName)
        func = getattr(obj, funcName)

        # 通过函数返回类型来决定是否进入分析
        func_sign = signature(func)
        if type(func_sign.return_annotation) == tuple:
            params_struct = dict(map(lambda kv: (kv[0], str(kv[1].annotation)), func_sign.parameters.items()))
            result_struct = dict(map(lambda v: (v.__name__, str(v.__supertype__)), func_sign.return_annotation))
            func_proxy = lambda **kvargs:dict(zip(result_struct.keys(), func(**kvargs)))
            func_proxy._type = "proxy"
            func_proxy._params_struct=params_struct
            func_proxy._result_struct=result_struct
            return func_proxy
        else:
            func._type = "orginal"
            func._params_struct = {}
            func._result_struct = {}
            return func

    # except Exception as e:
    #     console_logger.error(str(e))
    #     error_msg = str(e)
    #     return lambda in_json:error_msg