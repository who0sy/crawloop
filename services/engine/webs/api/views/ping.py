# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify

ping = Blueprint('ping', __name__)


@ping.route('/ping')
def ping_pong():
    """
    测试服务是否可用
    """
    return jsonify({
        "data": "pong",
        "status": True
    })
