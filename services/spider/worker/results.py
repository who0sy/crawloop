# -*- coding: utf-8 -*-
import hashlib
import json
import os
import time

from rpc.client.result import ResultClient
from webs.api.models.db_proxy import result_model_proxy
from worker import celery_app


@celery_app.task(name='save_results', queue='results')
def save_results(subtask_id, url_id, url_address, rpc_server, **kwargs):
    """
    保存爬取结果
    :param subtask_id:
    :param url_id:
    :param url_address:
    :param rpc_server:
    :param kwargs:
    :return:
    """

    http_archive_dict = kwargs.pop('http_archive_dict')

    # 保存爬取结果，仅作为容灾备份使用
    result_model_proxy.create(subtask_id, url_id, url_address)

    # 连接grpc服务
    grpc_result_client = ResultClient(rpc_server)

    # 反馈截图
    if kwargs.get('screenshot_id') \
            and os.path.exists('/usr/src/app/screenshots/{}.png'.format(kwargs['screenshot_id'])):
        img_path = '/usr/src/app/screenshots/{}.png'.format(kwargs['screenshot_id'])
        try:
            with open(img_path, 'rb') as f:
                md5 = hashlib.md5()
                while True:
                    fb = f.read(8096)
                    if not fb:
                        break
                    md5.update(fb)
                screenshot_md5 = md5.hexdigest()
            os.rename(img_path, f'/usr/src/app/screenshots/{screenshot_md5}.png')
            kwargs['screenshot_id'] = screenshot_md5
            grpc_result_client.upload_screenshot(screenshot_name=f'{screenshot_md5}.png')
        except Exception as e:
            pass

    # 向engine反馈基本爬取数据
    grpc_result_client.save_base_result(subtask_id, url_id, url_address, **kwargs)

    # 反馈har文件
    if kwargs.get('har_uuid') and http_archive_dict.get('hars'):
        with open('/usr/src/app/hars/{}.json'.format(kwargs['har_uuid']), 'w+', encoding='utf-8') as f:
            f.write(json.dumps(http_archive_dict, ensure_ascii=False, indent=2))
        grpc_result_client.upload_har_file(har_file_name='{}.json'.format(kwargs['har_uuid']))
