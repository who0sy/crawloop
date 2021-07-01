# -*- coding: utf-8 -*-

"""
存储结果
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
    text = Column(Text)  # 网页正文
    current_url = Column(String(1024))  # 网站最后相应的地址
    redirect_chain = Column(JSONB)  # 重定向链接
    response_headers = Column(JSONB)  # response headers
    har_uuid = Column(String(128))  # 网站交互过程
    screenshot_id = Column(String(128))  # 截图Id
    cookies = Column(JSONB)  # cookies
    finished_at = Column(TIMESTAMP)  # 完成时间
    wappalyzer_results = Column(JSONB)  # 网站指纹
    callback_failure_msg = Column(Text)  # 回调错误信息
    favicon_md5 = Column(String(50))  # 网站图标hash值
    favicon_link = Column(String(1024))  # 网站图标链接
    response_time = Column(Integer)  # 网站响应时间
    load_complete_time = Column(Integer)  # 页面加载完成时间
    charset = Column(String(256))  # 网站编码

    create_time = Column(TIMESTAMP, server_default=func.now(), index=True)
    update_time = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), index=True)

    def __repr__(self):
        return f'<Result-{self.id}>'

    def as_dict(self):
        from webs.api.models.db_proxy import task_model_proxy
        task_obj = task_model_proxy.query_task_obj_by_subtask(self.subtask_id)

        return {
            'result_id': self.id,
            'subtask_id': self.subtask_id,
            'task_id': task_obj.id if task_obj else None,
            'customer_id': task_obj.customer_id if task_obj else None,
            'url_id': self.url_id,
            'url_address': self.url_address,
            'http_code': self.http_code,
            'title': self.title,
            'content': self.content,
            'text': self.text,
            'current_url': self.current_url,
            'redirect_chain': self.redirect_chain,
            'response_headers': self.response_headers,
            'har_uuid': self.har_uuid,
            'screenshot_id': self.screenshot_id,
            'cookies': self.cookies,
            'favicon_md5': self.favicon_md5,
            'favicon_link': self.favicon_link,
            'wappalyzer_results': self.wappalyzer_results,
            'response_time': self.response_time,
            'load_complete_time': self.load_complete_time,
            'charset': self.charset,
            'finished_at': self.finished_at.strftime("%Y-%m-%d %H:%M:%S")
        }
