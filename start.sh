#!/bin/sh

CUR_DIR=$(cd "$(dirname "${BASH_SOURCE-$0}")"; pwd)

args=$1
python3 ${CUR_DIR}/app.py ${args}
# export PROXY_BUFFERSIZE=50
# args="{\"bind\":\"0.0.0.0:5000\",\"ENTRYPOINT\":\"/Users/admin/projects/go/src/github.com/SpeedVan/python-runtime/test_func/func_1.func\",\"FREEBACK_CODE\":\"aaaaa\"}"

# /Users/admin/projects/go/src/github.com/SpeedVan/python-runtime/bin/python3 ${CUR_DIR}/app.py ${args}