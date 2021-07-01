# -*- coding: utf-8 -*-


from sqlalchemy import Column, types
from sqlalchemy.dialects import postgresql

from webs.api.models import db

"""
APScheduler任务存储表
"""


class APSchedulerJobs(db.Model):
    __tablename__ = 'apscheduler_jobs'

    id = Column(types.String(length=191), primary_key=True)
    next_run_time = Column(postgresql.DOUBLE_PRECISION(precision=53), index=True)
    job_state = Column(postgresql.BYTEA(), nullable=False)
