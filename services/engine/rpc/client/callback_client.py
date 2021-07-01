# -*- coding: utf-8 -*-
import json
import os

import grpc

from rpc.pb import callback_pb2
from rpc.pb.callback_pb2_grpc import ResultStub

CHUNK_SIZE = 10 * 1024


class CallbackClient(object):

    def __init__(self, rpc_server):
        # RPC服务器信道
        channel = grpc.insecure_channel(target=f'{rpc_server}', options=[
            ('grpc.max_send_message_length', int(os.getenv('GRPC_MAX_SEND_MESSAGE_LENGTH', 200)) * 1024 * 1024),
            ('grpc.max_receive_message_length', int(os.getenv('GRPC_MAX_RECEIVE_MESSAGE_LENGTH', 200)) * 1024 * 1024),
        ])

        # 获取Result grpc服务对象
        self.stub = ResultStub(channel)

    def callback_save_result(self, task_obj, result):
        """
        回调爬虫信息
        :return:
        """
        result['extra_data'] = task_obj.extra_data
        self.stub.SaveResult(
            callback_pb2.SaveResultRequest(
                customer_id=task_obj.customer_id,
                task_id=task_obj.id,
                task_status='executing',
                finished=False,
                crawl_results=json.dumps(result, ensure_ascii=False)
            ),
            timeout=30
        )

    def callback_task_finished(self, customer_id, task_id):
        """回调任务完成"""

        self.stub.SaveResult(
            callback_pb2.SaveResultRequest(
                customer_id=customer_id, task_id=task_id,
                finished=True, task_status='finished'),
            timeout=30
        )
