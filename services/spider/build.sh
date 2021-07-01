#!/bin/bash

# 清除缓存目录
find . -type d -name __pycache__ | xargs rm -rf

# 编译代码
python3 compile.py build_ext --inplace
if [ $? -ne 0 ]; then
  exit 1
fi

# 将.so文件改名
find ./rpc -name '*.so' | awk -F '.cpython-37m-x86_64-linux-gnu' '{print "mv "$0" "$1$2}' | sh
find ./webs -name '*.so' | awk -F '.cpython-37m-x86_64-linux-gnu' '{print "mv "$0" "$1$2}' | sh
find ./worker -name '*.so' | awk -F '.cpython-37m-x86_64-linux-gnu' '{print "mv "$0" "$1$2}' | sh

# 删除.py文件
find ./rpc -name '*.py' | xargs rm -f
find ./webs -name '*.py' | xargs rm -f
find ./worker -name '*.py' | xargs rm -f

# 清除不需要的文件
rm -rf build
rm -f .gitignore
rm -f compile.py
rm -f build.sh
