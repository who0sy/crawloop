# -*- coding: utf-8 -*-

from webs.api.models import Result
from webs.api.models.db_proxy.base import BaseModelProxy


class ResultModelProxy(BaseModelProxy):
    def __init__(self):
        super().__init__()
        self.model = Result

    def save_model_by_grpc(self, **kwargs):
        """
        基于rpc回收爬虫数据
        :param kwargs:
        :return:
        """

        obj = Result(
            subtask_id=kwargs['subtask_id'], url_id=kwargs['url_id'], url_address=kwargs['url_address'],
            http_code=kwargs.get('http_code'), title=kwargs.get('title'), content=kwargs.get('content'),
            current_url=kwargs.get('current_url'), redirect_chain=kwargs.get('redirect_chain', []),
            response_headers=kwargs.get('response_headers', {}), har_uuid=kwargs.get('har_uuid'),
            screenshot_id=kwargs.get('screenshot_id'), finished_at=kwargs['finished_at'],
            cookies=kwargs.get('cookies', []), wappalyzer_results=kwargs.get('wappalyzer_results', []),
            text=kwargs.get('text'), favicon_md5=kwargs.get('favicon_md5'), favicon_link=kwargs.get('favicon_link'),
            response_time=kwargs.get('response_time'), load_complete_time=kwargs.get('load_complete_time'),
            charset=kwargs.get('charset')
        )
        self.db_session.add(obj)
        self.db_session.flush()
        self.safe_commit()
        return obj

    def get_by_url(self, url, fields):
        """
        基于url取结果
        :param url:
        :param fields:
        :return:
        """

        # obj = self.self_session.filter(
        #     or_(self.model.url_address == url.rstrip('/'), self.model.url_address == url.rstrip('/') + '/')) \
        #     .order_by(self.model.finished_at.desc()).first()
        from webs.api.models.db_proxy import url_model_proxy
        url_obj = url_model_proxy.find(address=url)
        if not url_obj:
            return {}

        # 查询所有记录
        objs = self.self_session.filter(self.model.url_id == url_obj.id) \
            .order_by(self.model.id.desc()).all()

        latest_record = {}
        if objs:
            latest_record = objs[0].as_dict()
            latest_record['other_records'] = [{
                'result_id': each.id,
                'finished_at': each.finished_at.strftime("%Y-%m-%d %H:%M:%S")}
                for each in objs[1:]
            ]

        if fields: latest_record = {each: latest_record[each] for each in fields if each in latest_record}

        return latest_record

    def get_by_result_id(self, result_id):
        """
        基于id取结果
        :param result_id:
        :return:
        """

        obj = self.self_session.filter(self.model.id == result_id).order_by(self.model.finished_at.desc()).first()
        return {} if not obj else obj.as_dict()

    def get_favicon_data_by_url(self, url):
        """
        根据url获取已存在的图标信息
        :param url:
        :return:
        """

        obj = self.db_session.query(self.model.favicon_md5, self.model.favicon_link) \
            .filter(self.model.url_address == url).order_by(self.model.create_time.desc()).first()
        return (None, None) if not obj else (obj[0], obj[1])
