# -*- coding: utf-8 -*-

import os

from flask import Flask

from webs.api.utils.requests import before_request_middleware, \
    after_request_middleware, teardown_appcontext_middleware
from webs.api.utils.responses import JSONResponse, app_error_handler
from webs.api.utils.routers import register_routes as init_routes
from webs.api.utils.settings import init_db


def create_app():
    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # register all blueprints
    init_routes(app=app)

    # register custom response class
    app.response_class = JSONResponse

    # register custom error handler
    app_error_handler(app=app)

    # register before request middleware
    before_request_middleware(app=app)

    # register after request middleware
    after_request_middleware(app=app)

    # register after app context teardown middleware
    teardown_appcontext_middleware(app=app)

    # set up extensions
    app_db = init_db(app=app)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': app_db}

    return app
