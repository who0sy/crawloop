# -*- coding: utf-8 -*-

from webs.api.models import Result
from webs.api.models.db_proxy.base import BaseModelProxy


class ResultModelProxy(BaseModelProxy):
    def __init__(self):
        super().__init__()
        self.model = Result

    def create(self, subtask_id, url_id, url_address, **kwargs):
        """
        保存爬取结果
        :param subtask_id:
        :param url_id:
        :param url_address:
        :param kwargs:
        :return:
        """

        result_obj = Result(
            subtask_id=subtask_id, url_id=url_id, url_address=url_address,
            http_code=kwargs.get('http_code'), title=kwargs.get('title'),
            content=kwargs.get('content'), current_url=kwargs.get('current_url'),
            har_uuid=kwargs.get('har_uuid'), screenshot_id=kwargs.get('screenshot_id'),
            response_headers=kwargs.get('response_headers', {}), redirect_chain=kwargs.get('redirect_chain', []),
            cookies=kwargs.get('cookies', [])
        )
        self.db_session.add(result_obj)
        self.safe_commit()
        return result_obj

    def query_already_crawl_url_ids(self, subtask_id):
        """
        查询已经抓取过的url
        :param subtask_id:
        :return:
        """

        query = self.db_session.query(self.model.url_id).filter(self.model.subtask_id == subtask_id).all()
        return [each[0] for each in query]
