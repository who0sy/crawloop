# -*- coding: utf-8 -*-

import os
import time
from concurrent import futures

import grpc

from rpc.pb import result_pb2_grpc
from rpc.server.result import ResultServicer


# 运行函数
def run():
    # 以线程池运行rpc服务
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=os.getenv('GRPC_SERVER_MAX_WORKER_COUNT', 10)),
        options=[
            (
                'grpc.max_send_message_length',
                os.getenv('GRPC_MAX_SEND_MESSAGE_LENGTH', 200) * 1024 * 1024
            ),
            (
                'grpc.max_receive_message_length',
                os.getenv('GRPC_MAX_RECEIVE_MESSAGE_LENGTH', 200) * 1024 * 1024
            ),
        ]
    )

    ###### 注册服务
    # 保存爬虫基本信息
    result_pb2_grpc.add_ResultServicer_to_server(ResultServicer(), server)

    # 设置服务器监听地址
    server.add_insecure_port(address='0.0.0.0:15002')

    # 启动服务
    server.start()

    # 阻塞rpc服务
    try:
        while True:
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    run()
