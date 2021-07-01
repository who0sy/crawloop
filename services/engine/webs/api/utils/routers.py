# -*- coding: utf-8 -*-

import pkgutil


def register_routes(app):
    """Register routes."""
    from .. import views
    from flask.blueprints import Blueprint

    for _, name, _ in pkgutil.iter_modules(views.__path__, prefix=views.__name__ + "."):
        blueprint_name = name.split('.')[-1]
        modules = __import__(name, fromlist="dummy")
        blueprint = getattr(modules, blueprint_name)
        if isinstance(blueprint, Blueprint):
            app.register_blueprint(blueprint)
