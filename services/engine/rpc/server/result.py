# -*- coding: utf-8 -*-

import os

from google.protobuf.json_format import MessageToDict

from manage import app
from rpc.pb import result_pb2, result_pb2_grpc
from webs.api.models.db_proxy import subtask_model_proxy, task_model_proxy, schedule_task_proxy, apscheduler_model_proxy
from worker import celery_app


def save_chunks_to_file(request_streams, folder_path):
    filename, file_chunks = None, []
    for yield_obj in request_streams:
        if getattr(yield_obj, 'filename'):
            filename = yield_obj.filename
        else:
            file_chunks.append(yield_obj.file_data)
    with open(f'/usr/src/app/{folder_path}/{filename}', 'wb') as f:
        for chunk in file_chunks:
            f.write(chunk.buffer)
    return os.path.getsize(f'/usr/src/app/{folder_path}/{filename}')


class ResultServicer(result_pb2_grpc.ResultServicer):
    # 创建截图目录
    if not os.path.exists('/usr/src/app/screenshots'):
        os.mkdir('/usr/src/app/screenshots')

    # 实现SaveBaseResult方法的rpc调用
    def SaveBaseResult(self, request, context):
        # proto消息体参数转为字典
        request_dict = MessageToDict(request, preserving_proto_field_name=True)

        # 异步处理相关爬取数据
        celery_app.send_task('save_base_result', queue='base_result', kwargs=request_dict)

        return result_pb2.SaveBaseResultResponse(status=True)

    # 实现StreamUploadPicture流式处理传输图片的rpc调用
    def StreamUploadPicture(self, request_iterator, context):
        try:
            file_length = save_chunks_to_file(request_iterator, folder_path='screenshots')
        except FileNotFoundError:
            file_length = 0
        return result_pb2.StreamUploadPictureResponse(length=file_length)

    # 实现SetSubTaskStatus标记子任务处理状态
    def SetSubTaskStatus(self, request, context):
        # 在flask上下文中设置子任务状态
        with app.app_context():
            ###### 设置子任务状态
            subtask_obj = subtask_model_proxy.set_many_attr(
                obj_id=request.subtask_id,
                fields_v={'finished': request.status, 'finished_at': request.finished_at}
            )
            ###### 设置调度任务状态
            unfinished_count = subtask_model_proxy.query_unfinished_subtask_count(subtask_obj.schedule_task_id)
            if unfinished_count == 0:
                schedule_task_obj = schedule_task_proxy.query_schedule_task_obj_by_subtask_id(subtask_obj.id)
                schedule_task_proxy.set_many_attr(
                    obj=schedule_task_obj, fields_v={'schedule_task_status': 'finished', 'finished': True}
                )

                # 查询主任务
                task_id, running_schedule_tasks = schedule_task_proxy.query_running_task_and_task_id(
                    subtask_obj.schedule_task_id)
                task_obj = task_model_proxy.find(id=task_id)

                # 回调当前调度任务完成
                if schedule_task_obj.crawl_options.get('callback_type'):
                    from rpc.client.callback_client import CallbackClient
                    try:
                        callback_client = CallbackClient(rpc_server=task_obj.crawl_options.get('callback_address'))
                        callback_client.callback_task_finished(customer_id=task_obj.customer_id, task_id=task_id)
                    except Exception as e:
                        print(e)
                        print(f"回调任务完成失败：ID-{task_id}")

                # 设置主任务为完结状态
                next_run_time = apscheduler_model_proxy.get_next_run_time(apschedule_id=task_id)
                if not running_schedule_tasks and not next_run_time:
                    task_model_proxy.set_many_attr(
                        obj=task_obj, fields_v={'task_status': 'finished', 'finished': True}
                    )

        return result_pb2.SetSubTaskStatusResponse(set_success=True)

    # 实现StreamUploadHarFile流式处理传输文件的rpc调用
    def StreamUploadHarFile(self, request_iterator, context):
        try:
            file_length = save_chunks_to_file(request_iterator, folder_path='hars')
        except FileNotFoundError:
            file_length = 0
        return result_pb2.StreamUploadPictureResponse(length=file_length)
