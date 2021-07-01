# -*- coding: utf-8 -*-

from webs.api.models import ScheduleTaskRecord, SubTask
from webs.api.models.db_proxy.base import BaseModelProxy


class ScheduleTaskProxy(BaseModelProxy):
    def __init__(self):
        super().__init__()
        self.model = ScheduleTaskRecord

    def query_schedule_task_obj_by_subtask_id(self, subtask_id):
        """
        基于子任务查询调度任务
        :return:
        """

        return self.self_session \
            .join(SubTask, SubTask.schedule_task_id == self.model.id) \
            .filter(SubTask.id == subtask_id).first()

    def query_running_schedule_tasks(self, task_id):
        """
        查询正在执行中的调度任务
        :param task_id:
        :return:
        """
        return self.self_session.filter(
            self.model.task_id == task_id,
            self.model.finished.is_(False)
        ).all()

    def query_running_task_and_task_id(self, schedule_task_id):
        """
        查询主任务下正在执行调度任务
        :param schedule_task_id:
        :return:
        """
        schedule_task_obj = self.find(id=schedule_task_id)
        return schedule_task_obj.task_id, self.query_running_schedule_tasks(schedule_task_obj.task_id)
