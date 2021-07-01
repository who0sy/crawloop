# -*- coding: utf-8 -*-

from datetime import datetime
from flask import current_app, request
from sqlalchemy.exc import DatabaseError
from webs.api.exceptions.customs import InvalidContentType
from webs.api.models import db

ACL_ORIGIN = 'Access-Control-Allow-Origin'
ACL_METHODS = 'Access-Control-Allow-Methods'
ACL_ALLOWED_HEADERS = 'Access-Control-Allow-Headers'
ACL_CREDENTIALS = 'Access-Control-Allow-Credentials'
ACL_CACHE_CONTROL = 'Cache-Control'

GET_METHOD = 'GET'
OPTIONS_METHOD = 'OPTIONS'
ALLOWED_ORIGINS = '*'
ALLOWED_METHODS = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
ALLOWED_HEADERS = 'Authorization, DNT, X-CustomHeader, Keep-Alive, User-Agent, ' \
                  'X-Requested-With, If-Modified-Since, Cache-Control, Content-Type'
ALLOWED_CREDENTIALS = 'true'  # Allow send cookie
ALLOWED_CACHE_CONTROL = 'no-cache, no-store, must-revalidate'


def before_request_middleware(app):
    app.before_request_funcs.setdefault(None, [
        ensure_request_log,
        ensure_content_type,
    ])


def after_request_middleware(app):
    app.after_request_funcs.setdefault(None, [
        enable_cors,
        commit_session,
    ])


def teardown_appcontext_middleware(app):
    app.teardown_appcontext_funcs = [
        shutdown_session,
    ]


def ensure_request_log():
    """当为生产环境时，屏蔽中间件日志记录器"""
    if current_app.debug:
        current_app.logger.info(
            "Request Time: {time} || Request Client IP: {client} || Full Path: {path} || "
            "Parameters: {param}".format(
                time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                client=request.environ.get('HTTP_X_REAL_IP', request.remote_addr),
                path=request.full_path,
                param=request.data.decode('utf-8')))


def ensure_content_type():
    """
    Ensures that the Content-Type for all requests
    is `application-json` or `multipart/form-data`, otherwise appropriate error
    is raised.
    :raises: InvalidContentType if Content-Type is not `application-json`
    or not `multipart/form-data`
    """

    content_type = request.headers.get('Content-Type')
    if request.method != GET_METHOD and request.method != OPTIONS_METHOD and \
            (not content_type or not ('application/json' in content_type or
                                      'multipart/form-data' in content_type)):
        raise InvalidContentType(
            message='Invalid Content-Type. '
                    'Only `application/json` or `multipart/form-data` is allowed')


def enable_cors(response):
    """
    Enable Cross-origin resource sharing.
    These headers are needed for the clients that
    will consume the API via AJAX requests.
    """
    if request.method == OPTIONS_METHOD:
        response = current_app.make_default_options_response()
    response.headers[ACL_ORIGIN] = ALLOWED_ORIGINS
    response.headers[ACL_METHODS] = ALLOWED_METHODS
    response.headers[ACL_ALLOWED_HEADERS] = ALLOWED_HEADERS
    response.headers[ACL_CACHE_CONTROL] = ACL_CACHE_CONTROL

    return response


def commit_session(response):
    """
    Try to commit the db session in the case
    of a successful request with status_code
    under 400.
    """
    if response.status_code >= 400:
        return response
    try:
        db.session.commit()
    except DatabaseError:
        db.session.rollback()
    return response


def shutdown_session(exception=None):
    """
    Remove the db session and detach from the
    database driver after application shutdown.
    """
    db.session.remove()
