# -*- coding: utf-8 -*-

import json
import re

from rpc.client.callback_client import CallbackClient
from wappalyzer import wappalyzer_handler
from webs.api.models.db_proxy import result_model_proxy, task_model_proxy
from webs.core.requests import web_client
from worker import celery_app
from worker.library.helper import extract_text, save_favicon


def callback_http(callback_address, task_obj, result, finished):
    """
    回调方式为http
    :return:
    """
    try:
        response = web_client.request(
            server='callback', method='POST',
            url=callback_address,
            timeout=60, json={
                'customer_id': task_obj.customer_id,
                'extra_data': task_obj.extra_data,
                'task_id': task_obj.id,
                'finished': finished,
                'result': result
            }
        )
        failure_msg = '' if response['status'] is True else response['error']['message']
    except Exception as e:
        failure_msg = e.message
    if failure_msg and result.get('result_id'):
        result_model_proxy.set_attr_by_id(result['result_id'], 'callback_failure_msg', failure_msg)


def callback_grpc(callback_address, task_obj, result):
    """
    回调方式为rpc
    :return:
    """

    callback_client = CallbackClient(rpc_server=callback_address)
    callback_client.callback_save_result(task_obj, result)


@celery_app.task(name='save_base_result')
def save_base_result_by_grpc(**kwargs):
    """
    异步回收相关爬取数据
    :param kwargs:
    :return:
    """

    task_obj = task_model_proxy.query_task_obj_by_subtask(subtask_id=kwargs['subtask_id'])
    if not task_obj:
        return

    # 解析网站编码
    try:
        m = re.compile('<meta .*(http-equiv="?Content-Type"?.*)?charset="?([a-zA-Z0-9_-]+)"?', re.I) \
            .search(kwargs.get('content', ''))
        if m and m.lastindex == 2: kwargs['charset'] = m.group(2).lower()
    except Exception as e:
        pass

    # 解析网站指纹
    if task_obj.crawl_options.get('wappalyzer') is True:
        kwargs['wappalyzer_results'] = wappalyzer_handler.discover_technologies(
            url=kwargs.get('current_url'), html=kwargs.get('content') or '',
            cookies=kwargs.get('cookies', []), headers=json.loads(kwargs.get('response_headers', {}))
        )

    # 提取网站内容
    if task_obj.crawl_options.get('extract_text') is True:
        kwargs['text'] = extract_text(kwargs.get('content', ''))

    # 下载网站图标
    kwargs['favicon_md5'], kwargs['favicon_link'] = None, None
    if task_obj.crawl_options.get('extract_favicon') is True and kwargs.get('http_code') is not None:
        try:
            kwargs['favicon_md5'], kwargs['favicon_link'] = save_favicon(
                kwargs.get('current_url', '') or kwargs['url_address'], kwargs.get('content', ''))
        except Exception as e:
            pass

    # 处理response_headers
    kwargs['response_headers'] = json.loads(kwargs.get('response_headers', {}))

    ###### 回收数据并存储
    result_obj = result_model_proxy.save_model_by_grpc(**kwargs)
    kwargs.update({'result_id': result_obj.id})

    ###### http回调/rpc回调
    if task_obj.crawl_options.get('callback_type'):
        celery_app.send_task(
            name='delay_callback', queue='base_result',
            kwargs={'subtask_id': kwargs.pop('subtask_id'), 'result': kwargs, 'finished': False}
        )


@celery_app.task(name='delay_callback')
def delay_callback(subtask_id, result, finished):
    """
    结果回调
    :param subtask_id:
    :param result:
    :param finished:
    :return:
    """

    task_obj = task_model_proxy.query_task_obj_by_subtask(subtask_id=subtask_id)

    # http回调
    if task_obj.crawl_options.get('callback_type') == 'http':
        callback_http(
            task_obj=task_obj, result=result, finished=finished,
            callback_address=task_obj.crawl_options.get('callback_address'))

    # grpc回调
    if task_obj.crawl_options.get('callback_type') == 'rpc':
        callback_grpc(
            task_obj=task_obj, result=result,
            callback_address=task_obj.crawl_options.get('callback_address'))
