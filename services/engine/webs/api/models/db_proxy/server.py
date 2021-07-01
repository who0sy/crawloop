# -*- coding: utf-8 -*-
from sqlalchemy import desc, asc

from webs.api.models import Server
from webs.api.models.db_proxy.base import BaseModelProxy


class ServerModelProxy(BaseModelProxy):
    def __init__(self):
        super().__init__()
        self.model = Server

    def query_servers_by_score(self, sort='desc'):
        """
        根据权重和负载计算服务器得分
        :return:
        """

        query = self.self_session.filter(self.model.enabled.is_(True), self.model.status.is_(True)).all()
        results = [{
            'server_id': each_obj.id,
            'server_name': each_obj.server_name,
            'server_address': each_obj.server_address,
            'score': int((1 - float(each_obj.load)) * each_obj.weight * 10)
        } for each_obj in query]
        return sorted(results, key=lambda x: x['score'], reverse=True if sort == 'desc' else False)

    def add_server(self, address):
        """新增爬虫服务器节点"""
        obj = Server(server_name=address, server_address=address)
        self.db_session.add(obj)
        self.safe_commit()
        return
