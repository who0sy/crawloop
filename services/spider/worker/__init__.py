# -*- coding: utf-8 -*-

import os
from celery import Celery

##################
# Celery配置
from kombu import Queue

from webs import create_app


class CeleryConfig(object):
    # 任务与劣化为json，从Celery4.0开始，默认序列化器将为json
    task_serializer = 'json'

    # 结果序列化为json
    result_serializer = 'json'

    # 定时任务过期时间
    result_expires = 60 * 60 * 24

    # 关闭worker事件监听 防止队列溢出
    worker_send_task_events = False

    # 允许接收的任务类型
    accept_content = ["json"]

    # 每个进程预取任务数，启动参数进行覆盖设置，此处仅作为标记使用
    worker_prefetch_multiplier = 4

    # 每个worker执行1个任务就销毁重启，启动参数进行覆盖设置，此处仅作为标记使用
    worker_max_tasks_per_child = 1

    # 时区设置
    timezone = 'Asia/Shanghai'
    enable_utc = True


##################
# 初始化celery worker
def init_celery(app=None, celery_type='usual'):
    app = app or create_app()
    celery_app = Celery(__name__, broker=os.environ.get('CRAWL_CELERY_BROKER_URL'))
    celery_app.config_from_object(CeleryConfig)

    # 导入相关任务模块
    if celery_type == 'usual':
        celery_app.conf.update(imports=['worker.fetch', 'worker.results'])
        celery_app.conf.task_queues = (
            Queue("priority_fetch", queue_arguments={'x-max-priority': 5}),
            Queue("results"),
        )
    elif celery_type == 'beat':
        pass
        # celery_app.conf.update(
        #     imports=['project.api.tasks.cron', 'project.api.tasks.event_cron', 'project.api.tasks.visual_cron'])
        # celery_app.conf.update(
        #     CELERYBEAT_SCHEDULE={
        #     }
        # )

    # 在flask上下文中执行
    class ContextTask(celery_app.Task):
        """Make celery tasks work with Flask app context"""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask
    return celery_app


celery_app = init_celery()
# beat_app = init_celery(celery_type='beat')
