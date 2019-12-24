import logging
from logging import handlers
from logging import StreamHandler
import pytz
import datetime
import sys
import json

exec_logger = logging.getLogger("__main_exec__")
func_logger = logging.getLogger("logger")

log_content_max_size = 9*1024  # unit byte


def try_if_else(key, try_if, try_else):
    print("try_if_else:" + key)
    try:
        print("try")
        result = try_if()
    except Exception as e:
        print("except:" + str(e))
        result = try_else()
    print("result(" + key + "):" + str(result))
    return result


def dict_map_array(_dict, map_f):
    result = []
    for key in _dict:
        result.append(map_f(key, _dict[key]))
    return result


def dict_for_each(_dict, for_each_f):
    for key in _dict:
        for_each_f(key, _dict[key])


# 因为大于20*1024才执行清楚，所以必然有4个以上的字节
def clear_dirty_code(_bytes: bytes):
    last3 = _bytes[-3:]
    for i in range(3):
        if ((0b11000000 < last3[2-i] < 0b11011111) and i < 1) \
                or ((0b11100000 < last3[2-i] < 0b11101111) and i < 2) \
                or ((0b11110000 < last3[2-i] < 0b11110111) and i < 3):
            return _bytes[:-i-1]
    return _bytes


def cut_msg(msg_str):
    msg_bytes = msg_str.encode("utf-8")
    if len(msg_bytes) > log_content_max_size:
        cleared_bytes = clear_dirty_code(msg_bytes[:log_content_max_size])
        return cleared_bytes.decode("utf-8")+"..."
    return msg_str


class ExtEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Exception):
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%a, %d %b %Y %H:%M:%S GMT')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%a, %d %b %Y %H:%M:%S GMT')
        return json.JSONEncoder.default(self, obj)


class HandlerMixin:
    __slots__ = ()

    alias = {
        "@level": "levelname",
        "@filename": "filename",
        "@lineno": "lineno",
        "@func": "funcName"
    }

    def alias_record_item(self, record, key1, key2):
        record.__dict__[key1] = record.__dict__[key2]

    def handle(self, record):
        extra = self.extra_data
        for key in extra:
            if key not in record.__dict__:
                record.__dict__[key] = extra[key]
        record.__dict__["@time"] = (lambda utc_time: utc_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+utc_time.strftime("%z"))(datetime.datetime.now(pytz.timezone("Asia/Shanghai")))

        if "@traceback" in record.__dict__ and len(record.__dict__["@traceback"]) > 10:
            record.__dict__["@traceback"] = record.__dict__["@traceback"][:10]

        dict_for_each(self.alias, lambda k, v: self.alias_record_item(record, k, v))
        super().handle(record)

    def format(self, record):
        # original_msg = super().format(record) # 先处理原生的format
        # original_msg = json.dumps(record.msg, cls=ExtEncoder)
        # print("original_msg:"+original_msg)
        # 因为原format未必能形成想要的json格式，所以在这一层加工
        if isinstance(record.msg, dict):
            original_dict = {"msg": cut_msg(json.dumps(record.msg, ensure_ascii=False, cls=ExtEncoder))}
        else:
            original_dict = {"msg": cut_msg(super().format(record))}  # 兼容那些用户日志内容因引号等原因导致无法json格式化的情况

        record_dict = record.__dict__
        sys_dict = {}
        for key in self.json_format:
            if not key == "msg":
                sys_dict[key] = record_dict[key] if key in record_dict else self.json_format[key]

        return json.dumps({**original_dict, **sys_dict}, ensure_ascii=False, cls=ExtEncoder)


class StreamHandlerAdapter(HandlerMixin, StreamHandler):
    def __init__(self, json_format, extra_data):
        super().__init__(sys.stdout)
        self.extra_data = extra_data
        self.json_format = json_format


class TimedRotatingFileHandlerAdapter(HandlerMixin, handlers.TimedRotatingFileHandler):
    def __init__(self, file, when, interval, backupCount, json_format, extra_data):
        super().__init__(file, when=when, interval=interval, backupCount=backupCount)
        self.extra_data = extra_data
        self.json_format = json_format


# logger这样设计，用户自定义logger打印到日志文件和控制台，使用print时只打印到控制台，这样print的内容不会被收集
# 给用户的logger，注入滚动日志文件handler
def setup_logger(env, namespace, function_name, extra_data, pod_name):
    # log_dir = "/var/log/functions/"

    # log_dir = "./log/functions/"

    def to_file_handler(handler, json_format):
        jf = json_format if not hasattr(handler, "json_format") else {**json_format, **handler.json_format}
        fh = TimedRotatingFileHandlerAdapter(log_dir + function_name + ".log", "D", 1, 2, jf, extra_data)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(handler.formatter)
        return fh

    def to_base_stream_handler(handler, json_format):
        # return handler
        jf = json_format if not hasattr(handler, "json_format") else {**json_format, **handler.json_format}
        fh = StreamHandlerAdapter(jf, extra_data)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(handler.formatter)
        return fh

    def if_stdout_stream_handler_remove(logger, handler):
        if type(handler) is logging.StreamHandler and handler.stream == sys.stdout:
            logger.removeHandler(handler)
            return True
        else:
            return False

    def add_logger_adapter_handler(logger, handler, json_format):
        logger.addHandler(to_base_stream_handler(handler, json_format))
        logger.addHandler(to_file_handler(handler, json_format))

    # _dir = os.path.dirname(log_dir)
    # if not os.path.exists(_dir):
    #     os.makedirs(_dir)

    exec_format = {
        "@env": env,
        "@log_type": "web_container",
        "@pod_name": pod_name,
        "@msg_type": "",
        "@namespace": namespace,
        "@function_name": function_name,
        "@trace_id": "",
        "@client_id": "",
        "@target": "",
        "@time": "",
        "@level": "",
        "@filename": "",
        "@lineno": "",
        "@func": "",
        "@traceback": [],
        "@exec_cost": -1.0,
        "msg": "",
    }

    func_format = {
        "@env": env,
        "@log_type": "function",
        "@pod_name": pod_name,
        "@namespace": namespace,
        "@function_name": function_name,
        "@trace_id": "",
        "@client_id": "",
        "@time": "",
        "@level": "",
        "@filename": "",
        "@lineno": "",
        "@func": "",
        "@traceback": [],
        "msg": "",
    }

    base_handler = logging.StreamHandler(sys.stdout)
    base_handler.setLevel(logging.DEBUG)

    print("执行logger初始化开始")
    exec_logger.addHandler(to_base_stream_handler(base_handler, exec_format))
    # exec_logger.addHandler(to_file_handler(base_handler, exec_format))
    print("执行logger初始化结束")

    print("函数logger初始化开始")
    stdout_stream_handler = list(
        filter(lambda h: if_stdout_stream_handler_remove(func_logger, h), func_logger.handlers))
    print("函数logger可注入handler个数:" + str(len(stdout_stream_handler)))
    if len(stdout_stream_handler) < 1:
        print("函数logger无可注入handler，补充默认handler")
        func_logger.addHandler(base_handler)
        func_logger.addHandler(to_base_stream_handler(base_handler, func_format))
        print("函数logger补充默认handler完成")
    else:
        print("函数logger注入文件handler开始")
        for h in stdout_stream_handler:
            func_logger.addHandler(h)
            func_logger.addHandler(to_base_stream_handler(h, func_format))
        print("函数logger注入文件handler完成")
    print("函数logger初始化完成")


# 主logger，输出到控制台，只要是stdout的会打印到控制台，rootLogger决定print可以打印到控制台
def setup_main_logger(console_logger, namespace, function_name, extra_data, pod_name):
    console_logger.setLevel(level=logging.DEBUG)
    console_logger.setLevel(logging.DEBUG)

    format_dict = {
        "@log_type": "web_container_root",
        "@pod_name": pod_name,
        "@namespace": namespace,
        "@function_name": function_name,
        "@time": "",
        "@level": "",
        "@filename": "",
        "@lineno": "",
        "@func": "",
        "msg": "",
    }
    fh = StreamHandlerAdapter(format_dict, extra_data)
    fh.setLevel(logging.DEBUG)
    console_logger.addHandler(fh)
    # app_logger.addHandler(HandlerAdapter(ch, "web_container", function_name, extra_data))
