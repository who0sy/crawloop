# -*- coding: utf-8 -*-

from datetime import datetime


def now():
    return datetime.now()


def nowstr():
    return now().strftime('%Y-%m-%d %H:%M:%S')


def today():
    return now().strftime('%Y-%m-%d')


def add_spider_server(address):
    """添加爬虫服务地址"""
    from webs.api.models.db_proxy import server_model_proxy
    server_model_proxy.add_server(address)
