#!/bin/sh

CUR_DIR=$(cd "$(dirname "${BASH_SOURCE-$0}")"; pwd)

PROXY_BUFFERSIZE=50python ${CUR_DIR}/app.py "{\"bind\":\"0.0.0.0:5000\", \"ENTRYPOINT\": \"/Users/admin/projects/go/src/github.com/SpeedVan/python-runtime/test_func/func_1.func\", \"FREEBACK_CODE\":\"aaaaa\"}"