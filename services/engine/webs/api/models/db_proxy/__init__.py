# -*- coding: utf-8 -*-
from .apschedule import ApschedulerModelProxy
from .result import ResultModelProxy
from .schedule_task import ScheduleTaskProxy
from .server import ServerModelProxy
from .task import TaskModelProxy
from .task_url import TaskUrlModelProxy
from .url import UrlModelProxy
from .subtask import SubTaskModelProxy

task_model_proxy = TaskModelProxy()
schedule_task_proxy = ScheduleTaskProxy()
url_model_proxy = UrlModelProxy()
task_url_model_proxy = TaskUrlModelProxy()
server_model_proxy = ServerModelProxy()
subtask_model_proxy = SubTaskModelProxy()
result_model_proxy = ResultModelProxy()
apscheduler_model_proxy = ApschedulerModelProxy()
