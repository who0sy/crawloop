# -*- coding: utf-8 -*-
import time
from datetime import datetime

from webs.api.models import APSchedulerJobs
from webs.api.models.db_proxy.base import BaseModelProxy


class ApschedulerModelProxy(BaseModelProxy):
    def __init__(self):
        super().__init__()
        self.model = APSchedulerJobs

    def get_next_run_time(self, apschedule_id):
        """
        获取下一次任务执行时间
        :param apschedule_id:
        :return:
        """
        schedule_obj = self.find(id=str(apschedule_id))
        if schedule_obj and schedule_obj.next_run_time:
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(schedule_obj.next_run_time))
        return
