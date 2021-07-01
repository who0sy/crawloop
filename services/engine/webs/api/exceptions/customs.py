# -*- coding: utf-8 -*-


from werkzeug.exceptions import BadRequest, \
    NotFound, Unauthorized, Forbidden, InternalServerError, Conflict


class CustomException(Exception):
    """Custom JSON based exception."""

    status_code = BadRequest.code
    message = ""

    def __init__(self, message=None, status_code=None):
        """
        :param status_code: response status_code
        :param message: exception message
        """

        Exception.__init__(self)

        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return {
            "status": False,
            "error": {
                "message": self.message,
                "type": str(self.__class__.__name__)
            }
        }


class InvalidContentType(CustomException):
    """
    Raised when an invalid Content-Type is provided.
    """

    status_code = BadRequest.code


class UnauthorizedAPIRequest(CustomException):
    """
    Raise if the user is not authorized.  Also used if you want to use HTTP
    basic auth.
    """

    status_code = Unauthorized.code


class InvalidPermissions(CustomException):
    """
    Raise if the user doesn't have the permission for the requested resource
    but was authenticated.
    """

    status_code = Forbidden.code


class InvalidAPIRequest(CustomException):
    """
    Raised when an invalid request has been made.
    (e.g. accessed unexisting url, the schema validation did
    not pass)
    """

    status_code = BadRequest.code


class ServerError(CustomException):
    """
    Generic internal error.
    Inherit this error for all subsequent
    errors that are related to database.
    """

    status_code = InternalServerError.code


class DatabaseError(CustomException):
    """
    Generic database interaction error.
    Inherit this error for all subsequent
    errors that are related to database.
    """

    status_code = InternalServerError.code


class RecordNotFound(DatabaseError):
    """
    Raised when the record was not found in the database.
    """

    status_code = NotFound.code


class RecordAlreadyExists(DatabaseError):
    """
    Raised in the case of violation of a unique constraint.
    """

    status_code = Conflict.code


class PublishError(CustomException):
    """
    Raised in the case of violation of a publish error.
    """

    status_code = InternalServerError.code
