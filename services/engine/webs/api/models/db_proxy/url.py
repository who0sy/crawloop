# -*- coding: utf-8 -*-

from webs.api.models import Url
from webs.api.models.db_proxy.base import BaseModelProxy


class UrlModelProxy(BaseModelProxy):
    def __init__(self):
        super().__init__()
        self.model = Url

    def create(self, urls):
        """
        :return:
        """

        # 检测系统中已存在的url
        exist_url_query = self.db_session.query(Url.id, Url.address).filter(Url.address.in_(urls)).all()
        exist_urls_id = [each[0] for each in exist_url_query]

        # 创建在系统中不存在的url
        not_create_urls = set(urls).difference(set([each[1] for each in exist_url_query]))
        create_url_models = [Url(address=url) for url in not_create_urls]
        self.db_session.add_all(create_url_models)
        self.safe_commit()

        exist_urls_id.extend([each.id for each in create_url_models])
        return exist_urls_id









