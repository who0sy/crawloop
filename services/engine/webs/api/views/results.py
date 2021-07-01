# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify
from webargs.flaskparser import use_args

from webs.api.bizs.result import ResultBiz
from webs.api.schemas.results import result_by_url_schema, result_by_id_schema, get_screenshot_schema, \
    download_har_file_schema, get_favicon_schema, get_small_schema

results = Blueprint('results', __name__, url_prefix='/results')


@results.route('/get-by-url')
@use_args(result_by_url_schema, locations=('query',))
def result_by_url(args):
    """
    根据url查询结果
    :param args:
    :return:
    """

    result_biz = ResultBiz()
    return jsonify({
        'status': True,
        'data': result_biz.result_by_url(args['url'], args['fields'])
    }), 200


@results.route('/get-by-id')
@use_args(result_by_id_schema, locations=('query',))
def result_by_id(args):
    """
    根据id查询结果
    :param args:
    :return:
    """

    result_biz = ResultBiz()
    return jsonify({
        'status': True,
        'data': result_biz.result_by_id(args['result_id'])
    }), 200


@results.route('/screenshot')
@use_args(get_screenshot_schema, locations=('query',))
def get_screenshot(args):
    """
    获取图片
    :param args:
    :return:
    """

    result_biz = ResultBiz()
    return result_biz.get_screenshot(args['screenshot_id'])


@results.route('/screenshot/encode')
@use_args(get_screenshot_schema, locations=('query',))
def get_screenshot_base64(args):
    """
    获取图片base64编码
    :param args:
    :return:
    """

    result_biz = ResultBiz()
    return jsonify({
        'status': True,
        'data': result_biz.get_screenshot_base64_encode(args['screenshot_id'])
    }), 200


@results.route('/screenshot/download')
@use_args(get_screenshot_schema, locations=('query',))
def download_screenshot(args):
    """
    下载图片
    :param args:
    :return:
    """
    result_biz = ResultBiz()
    return result_biz.get_screenshot(args['screenshot_id'], download=True)


@results.route('/screenshot/small')
@use_args(get_small_schema, locations=('query',))
def small_screenshot(args):
    """
    查看图片缩略图
    :param args:
    :return:
    """
    result_biz = ResultBiz()
    return result_biz.get_small_screenshot(**args)


@results.route('/har/download')
@use_args(download_har_file_schema, locations=('query',))
def download_har_file(args):
    """
    下载har文件
    :param args:
    :return:
    """

    result_biz = ResultBiz()
    return result_biz.download_har(args['har_uuid'])


@results.route('/favicon')
@use_args(get_favicon_schema, locations=('query',))
def get_favicon(args):
    """
    查看网站图标
    :param args:
    :return:
    """
    result_biz = ResultBiz()
    return result_biz.get_favicon(args['favicon_md5'])


@results.route('/favicon/download')
@use_args(get_favicon_schema, locations=('query',))
def download_favicon(args):
    """
    下载网站图标
    :param args:
    :return:
    """
    result_biz = ResultBiz()
    return result_biz.get_favicon(args['favicon_md5'], download=True)
