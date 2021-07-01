# -*- coding: utf-8 -*-

from webs.api.models.db_proxy import crawl_task_model_proxy


class CrawlTaskBiz(object):

    def __init__(self):
        pass

    def create_crawl_task(self, subtask_id, url_nested_list, options={}):
        """
        调度爬虫
        :param subtask_id:
        :param url_nested_list:
        :param options:
        :return:
        """

        # 创建CrawlTask对象
        crawl_task_obj = crawl_task_model_proxy.create(
            subtask_id=subtask_id, url_nested_list=url_nested_list,
            process_state='readying', options=options)

        # 异步抓取
        from worker import celery_app
        celery_app.send_task(
            name='fetch_tasks', queue='priority_fetch', priority=options['priority'],
            kwargs={'crawl_task_id': crawl_task_obj.id})
