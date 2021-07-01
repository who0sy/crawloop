# -*- coding: utf-8 -*-


"""
爬虫节点
"""

from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func, Boolean, Integer, Float

from webs.api.models import db


class Server(db.Model):
    __tablename__ = 'servers'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    server_name = Column(String(128))  # 爬虫节点服务器名称
    server_address = Column(String(255), unique=True, nullable=True)  # 服务器地址 ip:port
    enabled = Column(Boolean, server_default='t')  # 是否启用 默认是
    status = Column(Boolean, server_default='t')  # 服务器状态是否正常 默认是
    weight = Column(Integer, server_default='3')  # 服务器权重 1，2，3，4，5 默认为3
    # load = Column(Integer, server_default='0')  # 服务器负载，子服务器定时向主节点发送
    load = Column(String(20), server_default='0.1')  # 服务器负载，子服务器定时向主节点发送
    spider_type = Column(String(20), server_default='splash')  # 爬虫节点类型 splash/pyppeteer

    create_time = Column(TIMESTAMP, server_default=func.now(), index=True)
    update_time = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), index=True)

    def __repr__(self):
        return f'<Server-{self.server_name}-{self.server_address}>'
