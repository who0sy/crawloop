# -*- coding: utf-8 -*-

import json
from functools import singledispatch
from flask import jsonify, Response, current_app, request
from sqlalchemy.exc import DBAPIError
from webargs import ValidationError
from werkzeug.exceptions import BadRequest, NotFound, MethodNotAllowed, HTTPException, RequestEntityTooLarge

from webs.api.exceptions.customs import CustomException, RecordNotFound, \
    InvalidAPIRequest, DatabaseError, ServerError


@singledispatch
def to_serializable(rv):
    """
    Define a generic serializable function.
    """
    pass


@to_serializable.register(dict)
def ts_dict(rv):
    """Register the `dict` type
    for the generic serializable function.
    :param rv: object to be serialized
    :type rv: dict
    :returns: flask Response object
    """
    return jsonify(rv)


@to_serializable.register(list)
def ts_list(rv):
    """Register the `list` type
    for the generic serializable function.
    :param rv: objects to be serialized
    :type rv: list
    :returns: flask Response object
    """
    return Response(json.dumps(rv, indent=4, sort_keys=True))


class JSONResponse(Response):
    """
    Custom `Response` class that will be
    used as the default one for the application.
    All responses will be of type
    `application-json`.
    """

    @classmethod
    def force_type(cls, rv, environ=None):
        if rv.status_code not in (301, 302, 303, 305, 307):
            return super(JSONResponse, cls).force_type(to_serializable(rv), environ)
        return rv


def app_error_handler(app):
    @app.errorhandler(CustomException)
    def handle_invalid_usage(error):
        """
        Custom `Exception` class that will be used as the default one for the application.
        Returns pretty formatted JSON error with detailed information.
        """

        error_dict = error.to_dict()
        current_app.logger.warning(
            {
                "Exception_Name": "{exception_name}".format(
                    exception_name=error_dict['error']['type']),
                "Exception_Message": "{exception_message}".format(
                    exception_message=error.message)
            },
            extra={
                "exception_name": error_dict['error']['type'],
                "exception_message": error.message,
                "request_headers": dict(request.headers),
                "request_data": request.data.decode("utf-8"),
                "request_status_code": error.status_code
            }, exc_info=True)

        response = jsonify(error_dict)
        response.status_code = error.status_code
        return response

    @app.errorhandler(BadRequest)
    def handle_bad_request(error):
        """
        Custom error handler for 400 http exception.
        Returns a JSON object with a message of bad request.
        """

        current_app.logger.warning(
            {
                "Exception_Name": "{exception_name}".format(
                    exception_name=BadRequest.__name__),
                "Exception_Message": "{exception_message}".format(
                    exception_message=error.description)
            },
            extra={
                "exception_name": BadRequest.__name__,
                "exception_message": error.description,
                "request_headers": dict(request.headers),
                "request_data": request.data.decode("utf-8"),
                "request_status_code": BadRequest.code
            }, exc_info=True)

        response = jsonify(InvalidAPIRequest(
            message="HTTP请求异常(参数解析错误)").to_dict())
        response.status_code = BadRequest.code
        return response

    @app.errorhandler(NotFound)
    def resource_not_found(error):
        """
        Custom error handler for 404 http exception.
        Returns a JSON object with a message that accessed URL was not found.
        """

        current_app.logger.warning(
            {
                "Exception_Name": "{exception_name}".format(
                    exception_name=NotFound.__name__),
                "Exception_Message": "{exception_message}".format(
                    exception_message=error.description)
            },
            extra={
                "exception_name": NotFound.__name__,
                "exception_message": error.description,
                "request_headers": dict(request.headers),
                "request_data": request.data.decode("utf-8"),
                "request_status_code": NotFound.code
            }, exc_info=True)

        response = jsonify(RecordNotFound(
            message="HTTP请求异常(找不到请求地址)").to_dict())
        response.status_code = NotFound.code
        return response

    @app.errorhandler(MethodNotAllowed)
    def method_not_allowed(error):
        """
        Custom error handler for 405 http exception.
        Returns a JSON object with a message that accessed URL was not found.
        """

        current_app.logger.warning(
            {
                "Exception_Name": "{exception_name}".format(
                    exception_name=MethodNotAllowed.__name__),
                "Exception_Message": "{exception_message}".format(
                    exception_message=error.description)
            },
            extra={
                "exception_name": MethodNotAllowed.__name__,
                "exception_message": error.description,
                "request_headers": dict(request.headers),
                "request_data": request.data.decode("utf-8"),
                "request_status_code": MethodNotAllowed.code
            }, exc_info=True)

        response = jsonify(InvalidAPIRequest(
            message="HTTP请求异常(不允许的请求方法)",
            status_code=MethodNotAllowed.code).to_dict())
        response.status_code = MethodNotAllowed.code
        return response

    @app.errorhandler(DBAPIError)
    def sqlalchemy_db_error(error):
        """
        Custom error handler for DB error.
        Returns a JSON object with an error message.
        """

        current_app.logger.error(
            {
                "Exception_Name": "{exception_name}".format(
                    exception_name=DatabaseError.__name__),
                "Exception_Message": "{exception_message}".format(
                    exception_message="未知的数据库操作错误")
            },
            extra={
                "exception_name": DatabaseError.__name__,
                "exception_message": "未知的数据库操作错误",
                "request_headers": dict(request.headers),
                "request_data": request.data.decode("utf-8"),
                "request_status_code": DatabaseError.status_code
            }, exc_info=True, stack_info=True)

        response = jsonify(DatabaseError(message="未知的数据库操作错误").to_dict())
        response.status_code = DatabaseError.status_code
        return response

    @app.errorhandler(422)
    def webargs_422_error(error):
        """
        Custom error handler for Webargs 422 error.
        Returns a JSON object with an error message.
        """

        current_app.logger.warning(
            {
                "Exception_Name": "{exception_name}".format(
                    exception_name=ValidationError.__name__),
                "Exception_Message": "{exception_message}".format(
                    exception_message="请求参数解析错误")
            },
            extra={
                "exception_name": ValidationError.__name__,
                "exception_message": "请求参数解析错误",
                "request_headers": dict(request.headers),
                "request_data": request.data.decode("utf-8"),
                "request_status_code": InvalidAPIRequest.status_code
            }, exc_info=True)

        response = jsonify({
            "status": False,
            "error": {
                "message": "请求参数解析错误",
                "type": ValidationError.__name__,
            }
        })
        response.status_code = InvalidAPIRequest.status_code
        return response

    @app.errorhandler(500)
    def internal_server_error(error):
        """
        Custom error handler for 500 pages.
        Returns a JSON object with a message that accessed URL was not found.
        """

        current_app.logger.critical(
            {
                "Exception_Name": "{exception_name}".format(
                    exception_name=ServerError.__name__),
                "Exception_Message": "{exception_message}".format(
                    exception_message="服务器操作错误")
            },
            extra={
                "exception_name": ServerError.__name__,
                "exception_message": "服务器操作错误",
                "request_headers": dict(request.headers),
                "request_data": request.data.decode("utf-8"),
                "request_status_code": ServerError.status_code
            }, exc_info=True, stack_info=True)

        response = jsonify(ServerError(message="服务器操作错误").to_dict())
        response.status_code = ServerError.status_code
        return response

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """
        Custom error handler for other common http exceptions.
        Returns a JSON object with a message of bad request.
        """

        current_app.logger.warning(
            {
                "Exception_Name": "{exception_name}".format(
                    exception_name=error.name),
                "Exception_Message": "{exception_message}".format(
                    exception_message=error.description)
            },
            extra={
                "exception_name": error.name,
                "exception_message": error.description,
                "request_headers": dict(request.headers),
                "request_data": request.data.decode("utf-8"),
                "request_status_code": error.code
            }, exc_info=True)

        response = jsonify({
            "status": False,
            "error": {
                "message": "HTTP请求异常",
                "type": error.name,
            }
        })
        response.status_code = error.code
        return response

    @app.errorhandler(RequestEntityTooLarge)
    def upload_file_size_error(error):
        """上传文件超出阈值"""

        current_app.logger.warning(
            {
                "Exception_Name": "{exception_name}".format(
                    exception_name=error.name),
                "Exception_Message": "{exception_message}".format(
                    exception_message=error.description)
            },
            extra={
                "exception_name": error.name,
                "exception_message": error.description,
                "request_headers": dict(request.headers),
                "request_data": request.data.decode("utf-8"),
                "request_status_code": error.code
            }, exc_info=True)

        response = jsonify(InvalidAPIRequest(message="上传文件过大").to_dict())
        response.status_code = InvalidAPIRequest.status_code
        return response
