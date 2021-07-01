# -*- coding: utf-8 -*-

from webs.api.models import Task, SubTask, TaskUrl, Result, ScheduleTaskRecord
from webs.api.models.db_proxy.base import BaseModelProxy


class TaskModelProxy(BaseModelProxy):
    def __init__(self):
        super().__init__()
        self.model = Task

    def create(self,
               customer_id=None,
               task_name=None,
               extra_data=None,
               task_status='executing',
               crawl_options={},
               **kwargs):
        """
        :return:
        """
        obj = Task(
            customer_id=customer_id, task_name=task_name,
            task_status=task_status, crawl_options=crawl_options, extra_data=extra_data,
            schedule_options={'schedule_type': kwargs['schedule_type'], 'schedule_data': kwargs['schedule_data']})
        self.db_session.add(obj)
        self.db_session.flush()
        self.safe_commit()

        return obj

    def query_task_obj_by_subtask(self, subtask_id):
        """
        通过子任务获取主任务模型对象
        :param subtask_id:
        :return:
        """

        task_obj = self.db_session.query(self.model).select_from(self.model) \
            .join(ScheduleTaskRecord, ScheduleTaskRecord.task_id == self.model.id) \
            .join(SubTask, SubTask.schedule_task_id == ScheduleTaskRecord.id) \
            .filter(SubTask.id == subtask_id) \
            .first()

        return task_obj

    def query_url_count(self, task_id):
        """
        获取url总数
        :param task_id:
        :return:
        """

        return self.db_session.query(TaskUrl).filter(TaskUrl.task_id == task_id).count()

    def query_crawl_url_count(self, task_id):
        """
        获取已爬取的url总数
        :param task_id:
        :return:
        """

        return self.db_session.query(Result) \
            .join(SubTask, Result.subtask_id == SubTask.id) \
            .join(ScheduleTaskRecord, ScheduleTaskRecord.id == SubTask.schedule_task_id) \
            .filter(ScheduleTaskRecord.task_id == task_id).count()

    def add_schedule_record(self, task_id, schedule_task_status, crawl_options):
        """
        增加调度记录
        :param task_id:
        :param schedule_task_status:
        :param crawl_options:
        :return:
        """
        obj = ScheduleTaskRecord(
            task_id=task_id,
            crawl_options=crawl_options,
            schedule_task_status=schedule_task_status
        )
        self.db_session.add(obj)
        self.safe_commit()
        return obj

    def query_task_loop_count(self, task_id):
        """
        获取任务已跑轮次
        :param task_id:
        :return:
        """

        return self.db_session.query(ScheduleTaskRecord).filter(ScheduleTaskRecord.task_id == task_id).count()
