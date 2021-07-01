# -*- coding: utf-8 -*-

from aps.logger import scheduler_logger
from webs.api.models.db_proxy import task_model_proxy, schedule_task_proxy
from manage import app


def send_task_func(task_id):
    """下发爬取任务"""
    with app.app_context():
        scheduler_logger.info(f'开始调度任务：【task-id：{task_id}】')
        task_obj = task_model_proxy.find(id=task_id)
        if not task_obj:
            scheduler_logger.info(f'该任务已完成或已删除！：【task-id：{task_id}】')
            return

        # 判断当前主任务下的调度任务是否大于最大实例数
        running_schedule_tasks = schedule_task_proxy.query_running_schedule_tasks(task_id)
        max_instances = task_obj.schedule_options.get('schedule_data', {}).get('max_instances', 1)
        if len(running_schedule_tasks) >= max_instances:
            scheduler_logger.info(f'该任务已超过最大实例数，此次调度已忽略！：【task-id：{task_id}】')
            return

    # 异步切割任务下发
    from worker import celery_app
    celery_app.send_task(
        name='delivery_task', queue='engine',
        kwargs={'task_id': task_id}
    )
