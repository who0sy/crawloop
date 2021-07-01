# -*- coding: utf-8 -*-

import bisect
import hashlib
import math
import os
import random
import uuid
from datetime import datetime

import requests
from html2text import HTML2Text

from webs.api.models.db_proxy import subtask_model_proxy
from webs.core.requests import web_client
from worker.library.favicon import get_favicon_link


class WeightedRandomGenerator(object):
    def __init__(self, weights):
        print(weights)
        self.weights = weights
        self.totals = []
        running_total = 0

        for w in weights:
            running_total += w['score']
            self.totals.append(running_total)

    def spawn(self):
        rnd = random.random() * self.totals[-1]
        index = bisect.bisect_right(self.totals, rnd)
        return self.weights[index]

    def __call__(self):
        return self.spawn()


def split_urls(urls):
    """对url列表进行拆分"""
    if len(urls) > 100:
        m = len(urls) // 100
        n = int(math.ceil(len(urls) / float(m)))
        chunk_list = [urls[i:i + n] for i in range(0, len(urls), n)]
    else:
        chunk_list = [urls]

    return chunk_list


def send(schedule_task_id, url_nested_list, server_info, options):
    # 创建子任务模型
    subtask_obj = subtask_model_proxy.create(schedule_task_id, server_id=server_info['server_id'])

    # 发送请求
    try:
        response = web_client.request(
            server=server_info['server_name'],
            url=server_info['server_address'] + '/crawl_tasks',
            method='POST', timeout=60,
            json={
                'subtask_id': subtask_obj.id,
                'url_nested_list': url_nested_list,
                'options': options
            }
        )
        failure_msg = '' if response['status'] is True else response['error']['message']
    except Exception as e:
        failure_msg = e.message
    if failure_msg:
        # 设置子任务失败原因
        subtask_model_proxy.set_many_attr(obj=subtask_obj, fields_v={
            'finished': True,
            'finished_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'delivery_failure_msg': failure_msg
        })


def extract_text(content):
    """
    提取网页正文
    :param content:
    :return:
    """

    h = HTML2Text(bodywidth=0)
    h.ignore_links = True
    h.ignore_images = True
    h.ignore_tables = True
    h.ignore_emphasis = True
    try:
        result = h.handle(content).replace('*', '').replace('\n\n', '\n')
    except Exception as e:
        result = None
    return '' if result == '\n' else result


def save_favicon(url, html):
    """
    保存网站图标
    :param url:
    :param html:
    :return:
    """
    favicon_link, icon_ext = get_favicon_link(url, html)
    if favicon_link:
        try:
            response = requests.get(favicon_link, stream=True, timeout=10)
        except Exception as e:
            return None, None
        temp_filename = str(uuid.uuid4())
        save_path = '/usr/src/app/screenshots/{}.{}'.format(temp_filename, icon_ext)
        with open(save_path, 'wb+') as image:
            for chunk in response.iter_content(1024):
                image.write(chunk)
            image.seek(0)
            favicon_md5 = hashlib.md5(image.read()).hexdigest()
        os.rename(save_path, '/usr/src/app/screenshots/{}.{}'.format(favicon_md5, icon_ext))
        return favicon_md5, favicon_link
    return None, None


def remove_files(path, file_ids):
    """
    文件
    :return:
    """

    for file_id in file_ids:
        try:
            os.remove(f'/usr/src/app/{path}/{file_id}')
        except FileNotFoundError as e:
            pass
