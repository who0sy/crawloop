# -*- coding: utf-8 -*-


"""
底层存储结果值 作为备份使用
"""

from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB

from webs.api.models import db


class Result(db.Model):
    __tablename__ = 'results'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    subtask_id = Column(Integer, nullable=False, index=True)  # 所属子任务任务id
    url_id = Column(Integer, nullable=False, index=True)  # url id
    url_address = Column(String(1024), nullable=False)  # url 地址
    http_code = Column(Integer)  # 网站状态码
    title = Column(Text)  # 网站标题
    content = Column(Text)  # 网站内容
    current_url = Column(String(1024))  # 网站最后相应的地址
    redirect_chain = Column(JSONB)  # 重定向链接
    response_headers = Column(JSONB)  # response headers
    har_uuid = Column(String(128))  # 网站交互过程存储文件
    screenshot_id = Column(String(128))  # 截图Id
    cookies = Column(JSONB)  # cookies

    create_time = Column(TIMESTAMP, server_default=func.now(), index=True)
    update_time = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), index=True)

    def __repr__(self):
        return f'<Result-{self.id}>'
