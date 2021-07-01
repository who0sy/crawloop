# -*- coding: utf-8 -*-


import requests

from webs.api.exceptions.customs import ServerError, InvalidAPIRequest, RecordNotFound, RecordAlreadyExists


class RequestMixin(object):
    CODE_EXCEPTION_MSG = {
        400: InvalidAPIRequest,
        404: RecordNotFound,
        409: RecordAlreadyExists,
        422: InvalidAPIRequest,
        500: ServerError,
    }

    def __init__(self):
        self.session = requests.Session()

    @property
    def _headers(self):
        return {
            "Content-Type": "application/json",
        }

    def request(self, server, method, url, json=None, params=None, timeout=60):
        try:
            response = self.session.request(
                method, url, json=json, params=params,
                timeout=timeout, headers=self._headers
            )
        except requests.exceptions.ConnectTimeout:
            raise self.CODE_EXCEPTION_MSG[500](f"{server}服务器连接超时！")
        except requests.exceptions.ConnectionError:
            raise self.CODE_EXCEPTION_MSG[500](f"{server}服务器连接错误！")

        try:
            response_data = response.json()
        except Exception as e:
            raise ServerError(f"{server}服务器参数解析失败！")

        if not (200 <= response.status_code < 300):
            exception = self.CODE_EXCEPTION_MSG[response.status_code] \
                if response.status_code in self.CODE_EXCEPTION_MSG else self.CODE_EXCEPTION_MSG[400]
            raise exception(f"{server} Response:{response_data.get('error').get('message')}")

        return response_data


web_client = RequestMixin()
