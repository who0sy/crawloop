#!/bin/bash

# 声明proto路径和pb文件生成路径
declare -a proto_path=("protos")
declare -a python_out=("pb")

# 构造pb文件
python -m grpc_tools.protoc \
        --proto_path=$proto_path/ \
        --python_out=$python_out \
        --grpc_python_out=$python_out \
        $proto_path/*.proto

# 替换pb文件的错误引入语句
sed -i '' -E 's/^import (.*pb2)/from . import \1/g' ${python_out}/*pb2*.py