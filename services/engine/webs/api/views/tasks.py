# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify
from webargs.flaskparser import use_args

from webs.api.bizs.task import TaskBiz
from webs.api.schemas import task_validator
from webs.api.schemas.tasks import create_task_schema, task_id_schema

tasks = Blueprint('tasks', __name__, url_prefix='/tasks')


@tasks.route('', methods=['POST'])
@use_args(create_task_schema, locations=('json',), validate=task_validator.schedule_valid)
def create_task(args):
    """
    创建爬虫任务
    :param args:
    :return:
    """

    task_biz = TaskBiz()
    data = task_biz.create_task(**args)

    return jsonify({
        'status': True,
        'data': data
    }), 201


@tasks.route('', methods=['DELETE'])
@use_args(task_id_schema, locations=('json',))
def delete_task(args):
    """
    删除爬虫任务
    :param args:
    :return:
    """

    task_biz = TaskBiz()
    task_biz.delete_task(args['task_id'])

    return jsonify({
        'status': True
    }), 204


@tasks.route('/status')
@use_args(task_id_schema, locations=('query',))
def get_task_status(args):
    """
    查询任务进度
    :param args:
    :return:
    """

    task_biz = TaskBiz()
    return jsonify({
        'status': True,
        'data': task_biz.get_task_status(**args)
    }), 200


@tasks.route('/pause', methods=['PATCH'])
@use_args(task_id_schema, locations=('json',))
def pause_task(args):
    """
    暂停调度任务
    :param args:
    :return:
    """

    task_biz = TaskBiz()
    task_biz.pause_task(args['task_id'])

    return jsonify({
        'status': True,
    }), 200


@tasks.route('/resume', methods=['PATCH'])
@use_args(task_id_schema, locations=('json',))
def resume_task(args):
    """
    恢复调度任务
    :param args:
    :return:
    """

    task_biz = TaskBiz()
    task_biz.resume_task(args['task_id'])

    return jsonify({
        'status': True,
    }), 200


@tasks.route('/redelivery', methods=['POST'])
@use_args(task_id_schema, locations=('json',))
def redelivery(args):
    """
    重新下发
    """

    task_biz = TaskBiz()
    task_biz.redelivery(args['task_id'])
    return jsonify({'status': True}), 200
