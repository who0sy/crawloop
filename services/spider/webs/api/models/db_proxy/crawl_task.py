# -*- coding: utf-8 -*-

from webs.api.models import CrawlTask
from webs.api.models.db_proxy.base import BaseModelProxy


class CrawlTaskModelProxy(BaseModelProxy):
    def __init__(self):
        super().__init__()
        self.model = CrawlTask

    def create(self, **kwargs):
        """
        创建CrawlTask对象
        """

        crawl_task_obj = CrawlTask(
            subtask_id=kwargs['subtask_id'], url_nested_list=kwargs['url_nested_list'],
            process_state=kwargs['process_state'], options=kwargs['options'])
        self.db_session.add(crawl_task_obj)
        self.safe_commit()
        return crawl_task_obj
