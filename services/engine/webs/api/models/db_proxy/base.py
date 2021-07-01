# -*- coding: utf-8 -*-

from datetime import datetime

from flask import current_app
from sqlalchemy import func, desc, asc
from sqlalchemy.exc import SQLAlchemyError

from webs.api.exceptions.customs import DatabaseError, InvalidAPIRequest
from webs.api.models import db


class BaseModelProxy(object):
    def __init__(self):
        self.model = None
        self.allow_query_all = True
        self.db_session = db.session

    def query_list(self, query=None, **kwargs):
        """
        :param query:
        :param kwargs:
        :return:
        """
        return self.base_query(query=query or self.self_session, **kwargs)

    def find(self, query_model=None, **kwargs):
        """
        :param query_model:
        :param kwargs:
        :return:
        """

        return self.db_session.query(query_model or self.model).filter_by(**kwargs).first()

    def find_all(self, query_model=None, **kwargs):
        """
        :param query_model:
        :param kwargs:
        :return:
        """

        return self.db_session.query(query_model or self.model).filter_by(**kwargs).all()

    def find_all_with_condition(self, *condition):
        """
        :param condition: []
        :return:
        """

        return self.db_session.query(self.model).filter(*condition).all()

    def set_many_attr(self, fields_v, obj=None, obj_id=None):
        """
        :param obj:
        :param obj_id:
        :param fields_v:
        :return:
        """
        obj = obj or self.find(id=obj_id)
        for k, v in fields_v.items():
            setattr(obj, k, v)
        self.safe_commit()
        return obj

    def set_attr_by_id(self, obj_id, field, value):
        """
        :param obj_id:
        :param field:
        :param value:
        :return:
        """

        obj = self.find(id=obj_id)
        self.set_attr(obj, field, value)
        return obj

    def set_attr(self, obj, field, value):
        """
        :param obj:
        :param field:
        :param value:
        :return:
        """
        if field in self.model_fields():
            setattr(obj, field, value.strip() if isinstance(value, str) else value)
            self.safe_commit()
        return obj

    def set_attr2many(self, objs, field, value):
        """
        :param objs:
        :param field:
        :param value:
        :return:
        """
        for obj in objs:
            if field in self.model_fields():
                setattr(obj, field, value)
        self.safe_commit()

    def set_query_model(self, model=None):
        """
        配置查询模型
        :param model:
        :return:
        """

        self.model = model

    def set_build_query_filter(self, query_filter_func):
        """
        配置筛选入口函数
        :param query_filter_func:
        :return:
        """
        self._build_query_filter = query_filter_func

    def delete_model(self, **kwargs):
        """
        :param kwargs:
        :return:
        """
        self.db_session.query(self.model).filter_by(**kwargs).delete(synchronize_session=False)
        self.safe_commit()

    def delete_models(self, ids, fields='id'):
        """
        :param ids:
        :param fields:
        :return:
        """
        self.db_session.query(self.model).filter(getattr(self.model, fields).in_(ids)).delete(synchronize_session=False)
        self.safe_commit()

    @property
    def self_session(self):
        return db.session.query(self.model)

    def base_query(self, query, as_dict_func='as_dict', **kwargs):
        """
        :param query:
        :param as_dict_func:
        :param kwargs:
        :return:
        """

        total_count = self.query_count(query)
        query = self._build_query_filter(
            query, kwargs.get('filter', {}), strict=kwargs.get('strict'))
        query = self._build_query_order(query, kwargs.get('order', {}))
        filter_count = self.query_count(query)
        data = self._query_with_pagination(
            query, kwargs.get('page', 0), kwargs.get('size', 15))
        json_data = self._build_json_data(data, filter_count, total_count, as_dict_func=as_dict_func, **kwargs)
        return json_data

    @staticmethod
    def query_count(query):
        count_q = query.filter().statement.with_only_columns([func.count()]).order_by(None)
        count = query.session.execute(count_q).scalar()
        return count

    def _build_json_data(self, data, filter_count, total_count, fields=None, as_dict_func=None, **kwargs):
        """
        :param data:
        :param filter_count:
        :param total_count:
        :param fields:
        :param kwargs:
        :return:
        """

        return {
            "records": [self.trans2dict(obj, fields=fields, as_dict_func=as_dict_func, **kwargs) for obj in data],
            "total_count": total_count,
            "filter_count": filter_count
        }

    @staticmethod
    def _build_query_filter(query, condition, strict=False):
        """
        :param query:
        :param condition:
        :param strict:
        :return:
        """

        return query

    @staticmethod
    def trans2dict(obj, fields=None, as_dict_func=None, **kwargs):
        """
        :param obj:
        :param fields:
        :param as_dict_func:
        :param kwargs:
        :return:
        """

        # return obj.as_dict(fields=fields)
        as_dict_func = getattr(obj, as_dict_func)
        return as_dict_func(fields=fields)

    def _build_query_order(self, query, order):
        """
        :param query:
        :param order:
        :return:
        """
        order_fields = []
        for f in order:
            if f.lstrip('-') not in self.model_fields():
                raise InvalidAPIRequest('请输入正确的排序字段！')
            order_fields.append(
                desc(getattr(self.model, f.lstrip('-'))) if f.startswith('-')
                else asc(getattr(self.model, f)))
        return query.order_by(*order_fields, desc(self.model.id))

    def _query_with_pagination(self, query, page=1, size=10):
        """
        :param query:
        :param page:
        :param size:
        :return:
        """

        start = (page - 1) * size
        length = size
        if size == -1 and self.allow_query_all:
            return query.all()
        if start < 0 or length < 0:
            start = 0
            length = 15
        query = query.slice(start, start + length)
        data = query.all()
        return data

    def model_fields(self, un_fields=[]):
        return [column.name for column in self.model.__table__.columns
                if column.name not in un_fields]

    def safe_commit(self):
        try:
            self.db_session.commit()
        except SQLAlchemyError as db_error:
            current_app.logger.error(db_error)
            self.db_session.rollback()
            raise DatabaseError
