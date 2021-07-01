# -*- coding: utf-8 -*-

import os
import rpyc
from webs.api.exceptions.customs import InvalidAPIRequest, RecordNotFound
from webs.api.models.db_proxy import task_model_proxy, url_model_proxy, task_url_model_proxy, subtask_model_proxy, \
    result_model_proxy, apscheduler_model_proxy, schedule_task_proxy


class TaskBiz(object):

    def __init__(self):
        pass

    def create_task(self, **kwargs):
        """
        创建爬虫任务
        :param kwargs:
        :return:
        """

        if not kwargs.get('urls'):
            raise InvalidAPIRequest('urls字段不允许为空！')

        # 检验回调地址
        callback_type, callback_address = (
            kwargs['crawl_options'].get('callback_type'),
            kwargs['crawl_options'].get('callback_address')
        )
        if callback_type and not callback_address:
            raise InvalidAPIRequest('请输入回调地址！')

        urls = list(set(kwargs.pop('urls')))

        # 创建任务模型
        task_obj = task_model_proxy.create(**kwargs)

        # 创建url模型
        urls_id = url_model_proxy.create(urls)

        # 创建任务与url映射关系
        task_url_model_proxy.create(task_obj.id, urls_id)

        # 调用Apschedule下发任务
        self.apscheduler_client.root.add_task(
            task_id=task_obj.id,
            schedule_type=kwargs.pop('schedule_type'),
            schedule_data=kwargs.pop('schedule_data', {})
        )

        return task_obj.as_dict()

    def delete_task(self, task_id):
        """
        删除爬虫任务
        :param task_id:
        :return:
        """

        # 删除主任务
        task_model_proxy.delete_model(id=task_id)

        # 删除apscheduler调度任务
        self.apscheduler_client.root.delete_task(task_id)

        # 异步删除文件
        from worker import celery_app
        celery_app.send_task(name='delete_task', queue='engine', kwargs={'task_id': task_id})

    def get_task_status(self, task_id):
        """
        查询任务状态和进度
        :param task_id:
        :return:
        """
        task_obj = task_model_proxy.find(id=task_id)

        # 获取此任务所有关联的Url
        total_url_count = task_model_proxy.query_url_count(task_id)
        # 获取当前轮次已爬取的url数
        crawl_url_count = task_model_proxy.query_crawl_url_count(task_id)

        return {
            'total_url_count': total_url_count,
            'crawl_url_count': crawl_url_count,
            'complete_rate': (crawl_url_count / total_url_count) if not task_obj.finished else 1.0,
            'task_finished': task_obj.finished,
            'task_status': task_obj.task_status,
            'loop_count': task_model_proxy.query_task_loop_count(task_id),
            'create_time': task_obj.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'next_run_time': apscheduler_model_proxy.get_next_run_time(task_id),
            'last_loop_finished_at': task_obj.update_time.strftime("%Y-%m-%d %H:%M:%S") if task_obj.finished else None
        }

    def pause_task(self, task_id):
        """
        暂停调度任务
        :param task_id:
        :return:
        """

        task_obj = task_model_proxy.find(id=task_id)
        if task_obj.schedule_options.get('schedule_type') == 'instantly':
            raise InvalidAPIRequest('立即执行任务不允许暂停！')
        self.apscheduler_client.root.pause_task(task_id)
        task_model_proxy.set_attr(task_obj, 'task_status', 'paused')

    def resume_task(self, task_id):
        """
        恢复调度任务
        :param task_id:
        :return:
        """
        task_obj = task_model_proxy.find(id=task_id)
        if task_obj.task_status != 'paused':
            raise InvalidAPIRequest('该任务无需恢复调度！')
        self.apscheduler_client.root.resume_task(task_id)
        task_model_proxy.set_attr(task_obj, 'task_status', 'executing')

    @property
    def apscheduler_client(self):
        """
        Apscheduler RPC客户端
        :return:
        """
        return rpyc.connect(
            host=os.getenv('APSCHEDULE_HOST'),
            port=os.getenv('APSCHEDULE_PORT'),
            config={'allow_public_attrs': True, 'allow_pickle': True}
        )

    def redelivery(self, task_id):
        """重新下发"""
        task_obj = task_model_proxy.find(id=task_id)
        if not task_obj:
            raise RecordNotFound('此任务不存在！')
        task_model_proxy.set_many_attr(obj=task_obj, fields_v={'task_status': 'executing', 'finished': False})

        # 删除apscheduler调度任务
        self.apscheduler_client.root.delete_task(task_id)

        # 查询所有schedule task
        schedule_task_subquery = schedule_task_proxy.db_session.query(schedule_task_proxy.model.id) \
            .filter(schedule_task_proxy.model.task_id == task_id).subquery()

        # 查询所有subtask
        subtask_subquery = subtask_model_proxy.db_session.query(subtask_model_proxy.model.id).filter(
            subtask_model_proxy.model.schedule_task_id.in_(schedule_task_subquery)).subquery()

        # 删除Schedule task
        schedule_task_proxy.delete_models(ids=schedule_task_subquery, fields='id')

        # 删除subtask
        subtask_model_proxy.delete_models(ids=subtask_subquery, fields='id')

        # 调用Apschedule下发任务
        self.apscheduler_client.root.add_task(
            task_id=task_obj.id,
            schedule_type=task_obj.schedule_options.get('schedule_type'),
            schedule_data=task_obj.schedule_options.get('schedule_data')
        )
