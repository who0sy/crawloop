# -*- coding: utf-8 -*-

import base64
import os
from io import BytesIO

from PIL import Image
from flask import make_response, send_file

from webs.api.exceptions.customs import RecordNotFound, InvalidAPIRequest
from webs.api.models.db_proxy import result_model_proxy


class ResultBiz(object):

    def result_by_url(self, url, fields):
        """
        根据url查询结果
        :param url:
        :param fields:
        :return:
        """

        # 获取url id

        return result_model_proxy.get_by_url(url, fields)

    def result_by_id(self, result_id):
        """
        根据result查询结果
        :param result_id:
        :return:
        """
        return result_model_proxy.get_by_result_id(result_id)

    def get_screenshot(self, screenshot_id, download=False):
        """
        获取截图
        :param screenshot_id:
        :param download:
        :return:
        """

        screenshot_path = f'/usr/src/app/screenshots/{screenshot_id}.png'
        if not os.path.exists(screenshot_path):
            raise RecordNotFound('截图不存在！')
        response = make_response(send_file(
            filename_or_fp=screenshot_path,
            as_attachment=download
        ))
        response.direct_passthrough = False
        return response

    def get_screenshot_base64_encode(self, screenshot_id):
        """
        获取截图Base64编码
        :param screenshot_id:
        :return:
        """
        screenshot_path = f'/usr/src/app/screenshots/{screenshot_id}.png'
        if not os.path.exists(screenshot_path):
            raise RecordNotFound('截图不存在！')
        with open(screenshot_path, 'rb') as f:
            img_encode_str = base64.b64encode(f.read()).decode('utf-8')
        return img_encode_str

    def download_har(self, har_uuid):
        """
        下载har文件
        :param har_uuid:
        :return:
        """
        har_path = f'/usr/src/app/hars/{har_uuid}.json'
        if not os.path.exists(har_path):
            raise RecordNotFound('该文件不存在！')
        response = make_response(send_file(
            filename_or_fp=har_path,
            as_attachment=True
        ))
        response.direct_passthrough = False
        return response

    def get_favicon(self, favicon_md5, download=False):
        """
        获取图标
        :param favicon_md5:
        :param download:
        :return:
        """

        newest_record = result_model_proxy.find(favicon_md5=favicon_md5)
        if not newest_record:
            raise RecordNotFound('图标不存在！')
        _, ext = os.path.splitext(newest_record.favicon_link)
        favicon_path = f'/usr/src/app/screenshots/{favicon_md5}{ext}'
        if not os.path.exists(favicon_path):
            raise RecordNotFound('图标不存在！')
        response = make_response(send_file(
            filename_or_fp=favicon_path,
            as_attachment=download
        ))
        response.direct_passthrough = False
        return response

    def get_small_screenshot(self, screenshot_id, wide, high):
        """查看图片缩略图"""

        screenshot_path = f'/usr/src/app/screenshots/{screenshot_id}.png'
        if not os.path.exists(screenshot_path):
            raise RecordNotFound('截图不存在！')
        im = Image.open(f'/usr/src/app/screenshots/{screenshot_id}.png')

        src_wide, src_high = im.size
        ratio = src_wide / wide
        im = im.resize((wide, int(src_high / ratio)), Image.ANTIALIAS)
        im = im.crop((0, 0, wide, high))

        # 存入临时内存中
        byte_io = BytesIO()
        im.save(byte_io, 'PNG')
        byte_io.seek(0)

        response = make_response(send_file(
            filename_or_fp=byte_io,
            as_attachment=False,
            mimetype='image/png'
            # attachment_filename=f'{screenshot_id}.png'
        ))
        response.direct_passthrough = False
        return response
