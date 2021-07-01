#!/bin/bash
set -e
# 登录harbor
echo "正在登录赛欧思harbor镜像仓库，请输入用户名和密码"
docker login harbor.socmap.net

echo -n "请输入这次构建镜像的版本，例如(v1.0.1) ->"
read TAG

# 构建镜像
docker-compose -f docker-compose-build.yml build
# 如果此阶段报错失败，重新执行这条命令即可，不必重新执行此脚本。

echo "镜像构建完成！"

echo "开始推送镜像到Harbor..."

# 推送镜像到仓库
docker push harbor.socmap.net/crawloop/crawloop-spider:$TAG
echo "镜像已成功推送到赛欧思镜像仓库!"
