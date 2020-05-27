from flask import Flask

import os
import sys


class FunctionLoaderPlugin(Flask):
    __slots__ = ()

    def __init__(self):
        pass

    def load_function(self, entrypoint: str):
        sys_path, file_func = entrypoint.rsplit(os.sep, 1)
        sys.path.append(sys_path)
        moduleName, funcName = file_func.rsplit(".", 1)
        obj = __import__(moduleName, fromlist=funcName)
        self.config["func"] = getattr(obj, funcName)
