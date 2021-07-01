# -*- coding: utf-8 -*-


"""
Url模型
"""

from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func

from webs.api.models import db


class Url(db.Model):
    __tablename__ = 'urls'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    address = Column(String(1024), unique=True, index=True)

    create_time = Column(TIMESTAMP, server_default=func.now(), index=True)
    update_time = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), index=True)

    def __repr__(self):
        return f'<Url-{self.address}>'
