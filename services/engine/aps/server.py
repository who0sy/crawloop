# -*- coding: utf-8 -*-

import os

import rpyc
from apscheduler.jobstores.base import JobLookupError
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers import SchedulerAlreadyRunningError, SchedulerNotRunningError
from apscheduler.schedulers.background import BackgroundScheduler

from aps.func import send_task_func
from aps.logger import scheduler_logger


##################
# APScheduler配置


class APSchedulerConfig(object):
    # 时区
    timezone = 'Asia/Shanghai'

    # 后端存储器
    jobstores = {
        'default': SQLAlchemyJobStore(url=os.getenv('DATABASE_URL'), tablename='apscheduler_jobs')
    }

    # 执行器
    executors = {
        'default': {'type': 'threadpool', 'max_workers': 10}
    }

    # 调度器设置
    job_defaults = {
        'coalesce': True,  # 是否启用合并运行（在几个运行时间同时到期时只运行一次）
        'misfire_grace_time': 3600,  # 任务的执行时间可以延迟多少秒 用于任务时间到达到时，执行器未启动下次重启时任务可以延迟时间
        'max_instances': 1  # 最大实例数
    }


##################
# APScheduler调度器
class APSchedulerService(rpyc.Service):
    @staticmethod
    def start():
        try:
            apscheduler.start(paused=False)
            scheduler_logger.info('Started APScheduler Success!')
        except SchedulerAlreadyRunningError:
            scheduler_logger.info('APScheduler Already Running!')

    @staticmethod
    def shutdown():
        try:
            apscheduler.shutdown()
        except SchedulerNotRunningError:
            scheduler_logger.info('Scheduler has been shut down!')

    @staticmethod
    def exposed_add_task(task_id, schedule_type, schedule_data):
        """
        添加调度任务
        :param task_id:
        :param schedule_type:
        :param schedule_data:
        :return:
        """
        trigger_map = {'instantly': None, 'datetime': 'date'}
        apscheduler.add_job(
            func=send_task_func, id=str(task_id), kwargs={'task_id': task_id},
            trigger=trigger_map.get(schedule_type, schedule_type),
            **schedule_data
        )

    @staticmethod
    def exposed_delete_task(task_id, jobstore=None):
        """
        删除调度任务
        :param task_id:
        :param jobstore:
        :return:
        """
        try:
            apscheduler.remove_job(job_id=str(task_id), jobstore=jobstore)
        except JobLookupError:
            scheduler_logger.warning('Job was not found or this job has ended!')

    @staticmethod
    def exposed_pause_task(task_id, jobstore=None):
        """
        暂停调度任务
        :param task_id:
        :param jobstore:
        :return:
        """

        try:
            apscheduler.pause_job(job_id=str(task_id), jobstore=jobstore)
        except JobLookupError:
            scheduler_logger.warning('Job was not found or this job has ended!')

    @staticmethod
    def exposed_resume_task(task_id, jobstore=None):
        """
        恢复调度任务
        :param task_id:
        :param jobstore:
        :return:
        """

        try:
            apscheduler.resume_job(job_id=str(task_id), jobstore=jobstore)
        except JobLookupError:
            scheduler_logger.warning('Job was not found or this job has ended!')


###### 创建APScheduler
apscheduler = BackgroundScheduler(
    jobstores=APSchedulerConfig.jobstores, executors=APSchedulerConfig.executors,
    job_defaults=APSchedulerConfig.job_defaults, timezone=APSchedulerConfig.timezone)

###### 创建APScheduler调度对象，供业务方调用
apscheduler_server = APSchedulerService()
