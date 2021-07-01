# -*- coding: utf-8 -*-


"""
动态爬虫扫描任务模型
"""
from datetime import datetime

from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func, Integer, ARRAY, Boolean, Text
from sqlalchemy.dialects.postgresql import JSONB

from webs.api.models import db


class Task(db.Model):
    __tablename__ = 'tasks'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    customer_id = Column(String(255), index=True)  # 纯粹用来作为API调用标识，API 返回时被原样返回，以方便 API 调用方匹配请求与返回。
    task_name = Column(String(255))  # 任务名称
    task_status = Column(String(255))  # task任务状态
    finished = Column(Boolean, server_default='f')  # 任务是否已完成
    schedule_options = Column(JSONB)  # 周期调度相关参数
    crawl_options = Column(JSONB)  # 爬取相关参数
    extra_data = Column(Text)  # 客户端额外数据

    create_time = Column(TIMESTAMP, server_default=func.now(), index=True)
    update_time = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), index=True)

    def __repr__(self):
        return f'<Task-{self.id}-{self.task_name}>'

    def as_dict(self, **kwargs):
        return {
            'task_id': self.id,
            'customer_id': self.customer_id,
            'task_name': self.task_name,
            'task_status': self.task_status,
            'finished': self.finished,
            'crawl_options': self.crawl_options,
            'schedule_options': self.schedule_options,
            'extra_data': self.extra_data,
            'create_time': self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'update_time': self.update_time.strftime("%Y-%m-%d %H:%M:%S")
        } if not kwargs.get('fields') else {
            f: getattr(self, f, None) if not isinstance(getattr(self, f), datetime)
            else getattr(self, f).strftime("%Y-%m-%d %H:%M:%S")
            for f in kwargs['fields'] if f in self.__table__.columns
        }


class SubTask(db.Model):
    __tablename__ = 'sub_tasks'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    schedule_task_id = Column(Integer, nullable=False, index=True)  # 所属某次调度任务id
    server_id = Column(Integer, nullable=False)  # 此子任务关联的服务器节点
    assigned_urls = Column(ARRAY(String))  # 此子任务所分配的url
    delivery_failure_msg = Column(Text)  # 发送失败原因
    finished = Column(Boolean, server_default='f')  # 是否已完成
    finished_at = Column(TIMESTAMP)  # 完成时间

    create_time = Column(TIMESTAMP, server_default=func.now(), index=True)
    update_time = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), index=True)

    def __repr__(self):
        return f'<SubTask-{self.id}>'


class ScheduleTaskRecord(db.Model):
    __tablename__ = 'schedule_task_records'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    task_id = Column(Integer, nullable=False, index=True)  # 所属任务id
    schedule_task_status = Column(String(255))  # task任务状态
    finished = Column(Boolean, server_default='f')  # 此次任务是否已完成
    crawl_options = Column(JSONB)  # 此次任务所使用的爬取参数

    create_time = Column(TIMESTAMP, server_default=func.now(), index=True)  # 调度任务创建时间
    start_time = Column(TIMESTAMP)  # 此次调度任务真正开始执行时间
    finished_time = Column(TIMESTAMP)  # 任务完成时间

    def __repr__(self):
        return f'<ScheduleTask-{self.id}>'
