# -*- coding: utf-8 -*-
import re
from datetime import datetime

from webs.api.models.db_proxy import task_model_proxy
from webs.api.exceptions.customs import InvalidAPIRequest, RecordNotFound
from webs.api.utils.helper import nowstr, today


class LengthChecker(object):
    """字段长度校验"""

    def __init__(self, sign, length):
        self.sign = sign
        self.length = length

    def __call__(self, verified):
        if verified is not None and len(verified) > self.length:
            raise InvalidAPIRequest(f'{self.sign}长度过长！')


class OneOf(object):
    """Validator which succeeds if ``value`` is a member of ``choices``"""

    def __init__(self, choices):
        self.choices = choices

    def __call__(self, verified):
        if verified not in self.choices:
            raise InvalidAPIRequest(f'请选择{self.choices}其中之一！')


class TaskValidator(object):
    """主任务验证器"""

    def __init__(self):
        self.url_pattern = r'(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?'

    def url_valid(self, url):
        if not re.match(self.url_pattern, url):
            raise InvalidAPIRequest(f'{url}不是一个合法的Url！')

    def task_id_exist_valid(self, task_id):
        if not task_model_proxy.find(id=task_id):
            raise RecordNotFound('该任务不存在！')

    @staticmethod
    def schedule_valid(kwargs):
        """验证周期性调度相关参数"""
        schedule_type, schedule_data = kwargs.get('schedule_type'), kwargs.get('schedule_data')

        # 验证定时执行
        if schedule_type == 'datetime':
            if len(schedule_data) > 1:
                raise InvalidAPIRequest('无效的执行时间！')
            run_date = schedule_data.get('run_date')
            if not run_date:
                raise InvalidAPIRequest('无效的执行时间！')
            # 和当前时间比较
            if run_date <= nowstr():
                raise InvalidAPIRequest('执行时间不能小于当前时间！')

        # 验证间隔执行和周期调度
        elif schedule_type in ('interval', 'cron'):
            if not schedule_data.get('start_date') or not schedule_data.get('end_date'):
                raise InvalidAPIRequest('请输入开始时间和结束时间！')

            interval_effective_params = {
                'weeks', 'days', 'hours', 'minutes', 'seconds',
                'start_date', 'end_date', 'max_instances'
            }
            cron_effective_params = {
                'week', 'day', 'hour', 'minute',
                'second', 'year', 'month',
                'day_of_week', 'max_instances',
                'start_date', 'end_date'
            }

            if (schedule_type == 'cron' and set(schedule_data.keys()).difference(cron_effective_params)) or (
                    schedule_type == 'interval' and set(schedule_data.keys()).difference(interval_effective_params)):
                raise InvalidAPIRequest('无效的调度参数！')

            if not set(schedule_data.keys()).difference({'start_date', 'end_date'}):
                raise InvalidAPIRequest('请输入正确的调度参数！')

            if schedule_data.get('start_date') >= schedule_data.get('end_date'):
                raise InvalidAPIRequest('开始时间不能大于结束时间！')

            if schedule_data.get('end_date') < today():
                raise InvalidAPIRequest('结束时间不能小于当前时间！')


class TimeValidator(object):

    def __init__(self, s=None, e=None):
        self.s = s
        self.e = e

    @staticmethod
    def date_or_datetime_valid(_time):
        try:
            datetime.strptime(_time, "%Y-%m-%d")
            return
        except (ValueError, AttributeError) as e:
            pass
        try:
            datetime.strptime(_time, "%Y-%m-%d %H:%M:%S")
            return
        except (ValueError, AttributeError) as e:
            pass
        raise InvalidAPIRequest('请输入正确的日期时间！')

    def __call__(self, time_field):
        if not self.s <= time_field <= self.e:
            raise InvalidAPIRequest('请输入正确的时间范围！')


task_validator = TaskValidator()
time_validator = TimeValidator()
