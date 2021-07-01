# -*- coding: utf-8 -*-

"""
任务与url映射关系
"""

from sqlalchemy import Column, BigInteger, TIMESTAMP, func

from webs.api.models import db


class TaskUrl(db.Model):
    __tablename__ = 'task_url'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    task_id = Column(BigInteger, nullable=True, index=True)
    # sub_task_id = Column(BigInteger, index=True)  # 子任务id
    url_id = Column(BigInteger, nullable=True, index=True)

    create_time = Column(TIMESTAMP, server_default=func.now(), index=True)
    update_time = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), index=True)

    def __repr__(self):
        return f'<TaskUrl-{self.task_id}-{self.url_id}>'
