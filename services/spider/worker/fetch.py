# -*- coding: utf-8 -*-

from datetime import datetime

from billiard.exceptions import SoftTimeLimitExceeded

from rpc.client.result import ResultClient
from webs.api.models.db_proxy import crawl_task_model_proxy, result_model_proxy
from worker import celery_app
from worker.library.playwright import PlayWrightHandler


@celery_app.task(
    name='fetch_tasks', queue='priority_fetch', acks_late=True, soft_time_limit=1000, max_retries=1,
    default_retry_delay=30, autoretry_for=(Exception,))
def fetch_tasks(crawl_task_id):
    """
    通过优先级队列取得任务进行抓取
    """

    crawl_task_obj = crawl_task_model_proxy.find_one_with_condition(
        crawl_task_model_proxy.model.id == crawl_task_id,
        crawl_task_model_proxy.model.process_state != 'finished'
    )
    if not crawl_task_obj:
        return

    # 设置爬取任务开始
    if crawl_task_obj.process_state == 'readying':
        crawl_task_model_proxy.set_attr(crawl_task_obj, 'process_state', 'running')
        url_nested_list = crawl_task_obj.url_nested_list

    # 导致此情况原因为worker进程异常退出，rabbitmq未确认此消息，worker重启此任务再次被投递
    else:  # crawl_task_obj.process_state == 'running'
        already_url_ids = result_model_proxy.query_already_crawl_url_ids(subtask_id=crawl_task_obj.subtask_id)
        url_nested_list = [
            url_info for url_info in crawl_task_obj.url_nested_list
            if url_info['url_id'] not in already_url_ids
        ]
    undone_url_ids = []
    if url_nested_list:
        # 执行抓取
        playwright_handler = PlayWrightHandler(
            subtask_id=crawl_task_obj.subtask_id,
            url_nested_list=url_nested_list,
            options=crawl_task_obj.options)
        undone_url_ids = playwright_handler.run()

    # 设置爬取状态、结束时间、抓取失败的urls
    crawl_task_model_proxy.set_many_attr(
        obj=crawl_task_obj,
        fields_v={
            'process_state': 'finished',
            'finished_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'failure_url_ids': undone_url_ids
        }
    )

    ####### 调用engine端rpc服务设置subtask爬取状态
    # 连接grpc服务
    grpc_result_client = ResultClient(crawl_task_obj.options.get('rpc_server'))

    # 设置Subtask爬取状态
    grpc_result_client.set_subtask_status(
        subtask_id=crawl_task_obj.subtask_id, status=True, finished_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
