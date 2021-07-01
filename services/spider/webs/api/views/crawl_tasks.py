# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify
from webargs.flaskparser import use_args

from webs.api.bizs.crawl_task import CrawlTaskBiz
from webs.api.schemas.crawl_tasks import create_crawl_task_schema

crawl_tasks = Blueprint('crawl_tasks', __name__, url_prefix='/crawl_tasks')


@crawl_tasks.route('', methods=['POST'])
@use_args(create_crawl_task_schema, locations=('json',))
def create_crawl_task(args):
    """
    创建爬虫任务
    :param args:
    :return:
    """
    crawl_task_biz = CrawlTaskBiz()
    data = crawl_task_biz.create_crawl_task(**args)

    return jsonify({
        'status': True,
        'data': data
    }), 201
