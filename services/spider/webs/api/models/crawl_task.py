# -*- coding: utf-8 -*-


"""
底层爬虫子任务与Url映射关系
"""

from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func, Integer, ARRAY
from sqlalchemy.dialects.postgresql import JSONB

from webs.api.models import db


class CrawlTask(db.Model):
    __tablename__ = 'crawl_tasks'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    subtask_id = Column(Integer, nullable=False, index=True)  # 所属子任务任务id
    url_nested_list = Column(JSONB)  # [{"url_id": xxx, "url_address": xxx, 'url_options': {}}]
    process_state = Column(String(30), server_default='readying')  # readying Started finished
    failure_url_ids = Column(ARRAY(Integer), server_default='{}')  # 爬取失败url
    finished_at = Column(TIMESTAMP)  # 完成时间
    options = Column(JSONB)  # 爬取参数

    # success_count = Column(Integer)  # 爬取成功数
    # failure_count = Column(Integer)  # 爬取失败数

    create_time = Column(TIMESTAMP, server_default=func.now(), index=True)
    update_time = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), index=True)

    def __repr__(self):
        return f'<CrawlTask-{self.id}>'
