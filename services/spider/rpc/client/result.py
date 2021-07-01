# -*- coding: utf-8 -*-
import json
import os

import grpc

from rpc.pb import result_pb2
from rpc.pb.result_pb2_grpc import ResultStub

CHUNK_SIZE = 10 * 1024


def get_file_chunks(filename, folder_path):
    yield result_pb2.StreamUploadPictureRequest(filename=filename)
    with open(f'/usr/src/app/{folder_path}/' + filename, 'rb') as f:
        while True:
            piece = f.read(CHUNK_SIZE)
            if len(piece) == 0:
                return
            yield result_pb2.StreamUploadPictureRequest(file_data={"buffer": piece})


def remove_file(file_path):
    """
    删除文件
    :param file_path:
    :return:
    """

    try:
        os.remove(file_path)
    except (NotImplementedError, FileNotFoundError):
        pass


class ResultClient(object):

    def __init__(self, rpc_server):
        # RPC服务器信道
        channel = grpc.insecure_channel(target=f'{rpc_server}', options=[
            ('grpc.max_send_message_length', int(os.getenv('GRPC_MAX_SEND_MESSAGE_LENGTH', 200)) * 1024 * 1024),
            ('grpc.max_receive_message_length', int(os.getenv('GRPC_MAX_RECEIVE_MESSAGE_LENGTH', 200)) * 1024 * 1024),
        ])

        # 获取Result grpc服务对象
        self.stub = ResultStub(channel)

    def save_base_result(self, subtask_id, url_id, url_address, finished_at, **kwargs):
        """保存爬虫基本信息"""

        # 返回头部序列化
        kwargs['response_headers'] = self.dic2json(kwargs.pop('response_headers', {}))

        # 生成状态码
        kwargs['http_code'] = kwargs['redirect_chain'][-1]['redirect_http_code'] if kwargs['redirect_chain'] else None

        # 去除firefox和chrome默认content
        if kwargs['content'] and (kwargs['content'].startswith(
                '<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" dir="ltr" lang="en-US">')
                                  or kwargs['content'] == '<html><head></head><body></body></html>'):
            kwargs['content'] = None

        # # http交互过程序列化
        # kwargs['http_archive'] = self.dic2json(kwargs.pop('http_archive', []))
        self.stub.SaveBaseResult(
            result_pb2.SaveBaseResultRequest(
                subtask_id=subtask_id, url_id=url_id, url_address=url_address,
                finished_at=finished_at, **kwargs),
            timeout=30
        )

    def upload_screenshot(self, screenshot_name):
        """上传截图"""
        chunks_generator = get_file_chunks(screenshot_name, folder_path='screenshots')
        response = self.stub.StreamUploadPicture(chunks_generator)
        file_path = f'/usr/src/app/screenshots/{screenshot_name}'
        assert response.length == os.path.getsize(file_path)
        remove_file(file_path)

    def set_subtask_status(self, subtask_id, status, finished_at):
        """标记子任务爬取状态"""
        self.stub.SetSubTaskStatus(
            result_pb2.SetSubTaskStatusRequest(
                subtask_id=subtask_id,
                status=status,
                finished_at=finished_at
            ),
            timeout=30
        )

    def upload_har_file(self, har_file_name):
        """上传har文件"""
        chunks_generator = get_file_chunks(har_file_name, folder_path='hars')
        response = self.stub.StreamUploadHarFile(chunks_generator)
        file_path = f'/usr/src/app/hars/{har_file_name}'
        assert response.length == os.path.getsize(file_path)
        remove_file(file_path)

    @staticmethod
    def dic2json(dic):
        """某些字段转换为json"""
        return json.dumps(dic, ensure_ascii=False)
