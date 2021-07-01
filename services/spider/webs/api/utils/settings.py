# -*- coding: utf-8 -*-

from flask_migrate import Migrate

from webs.api.models import db, redis_store


def init_db(app):
    """
    Create database if doesn't exist and
    create all tables.
    """

    # 初始化pg
    db.init_app(app)
    migrate = Migrate(compare_type=True, compare_server_default=True)
    migrate.init_app(app, db)

    # 初始化Redis
    redis_store.init_app(app)

    return db
