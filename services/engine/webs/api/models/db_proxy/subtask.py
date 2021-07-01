# -*- coding: utf-8 -*-

from webs.api.models import SubTask
from webs.api.models.db_proxy.base import BaseModelProxy


class SubTaskModelProxy(BaseModelProxy):
    def __init__(self):
        super().__init__()
        self.model = SubTask

    def create(self, schedule_task_id, server_id):
        """
        创建子任务
        :param schedule_task_id:
        :param server_id:
        :return:
        """

        obj = SubTask(schedule_task_id=schedule_task_id, server_id=server_id)
        self.db_session.add(obj)
        self.safe_commit()
        return obj

    def query_delivery_failure_count(self, schedule_task_id):
        """
        查询下发失败的子任务
        :return:
        """
        return self.self_session.filter(
            self.model.schedule_task_id == schedule_task_id,
            self.model.delivery_failure_msg.isnot(None)
        ).count()

    def query_unfinished_subtask_count(self, schedule_task_id):
        """
        根据子任务id查询当前调度任务未完成的子任务数量
        :param schedule_task_id:
        :return:
        """
        return self.self_session.filter(
            self.model.schedule_task_id == schedule_task_id, self.model.finished.is_(False)
        ).count()
