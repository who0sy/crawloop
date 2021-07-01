# -*- coding: utf-8 -*-

from webs.api.models import TaskUrl, Url
from webs.api.models.db_proxy.base import BaseModelProxy


class TaskUrlModelProxy(BaseModelProxy):
    def __init__(self):
        super().__init__()
        self.model = TaskUrl

    def create(self, task_id, urls_id):
        """
        :return:
        """
        self.db_session.add_all(
            [TaskUrl(task_id=task_id, url_id=url_id) for url_id in urls_id])
        self.safe_commit()

    def create_subtask_url_mapping(self, chunk_url, subtask_id):
        """
        创建子任务与url映射关系
        :param chunk_url:
        :param subtask_id:
        :return:
        """
        urls_query = self.db_session.query(Url.id, Url.address).filter(Url.address.in_(chunk_url)).all()
        self.self_session.filter(self.model.url_id.in_([each[0] for each in urls_query])).update(
            {self.model.sub_task_id: subtask_id}, synchronize_session='fetch')
        self.safe_commit()
        return [{'url_id': each[0], 'url_address': each[1]} for each in urls_query]

    def query_urls_by_task_id(self, task_id):
        """
        根据task id查询关联的url
        :param task_id:
        :return:
        """

        query = self.db_session.query(self.model.url_id, Url.address) \
            .join(Url, Url.id == self.model.url_id) \
            .filter(self.model.task_id == task_id) \
            .all()
        return [{
            'url_id': each_obj[0], 'url_address': each_obj[1]}
            for each_obj in query
        ]
