# -*- coding: utf-8 -*-
import os

from webargs import fields

from webs.api.schemas import LengthChecker, OneOf, task_validator, TimeValidator as TimeRangeValid, time_validator

schedule_data = {
    'run_date': fields.Str(validate=time_validator.date_or_datetime_valid),  # 定时执行时间
    'year': fields.Int(validate=TimeRangeValid(2021, 2999)),
    'month': fields.Int(validate=TimeRangeValid(1, 12)),
    'day': fields.Int(validate=TimeRangeValid(1, 31)),
    'week': fields.Int(validate=TimeRangeValid(1, 53)),
    'day_of_week': fields.Int(validate=TimeRangeValid(0, 6)),
    'hour': fields.Int(validate=TimeRangeValid(0, 23)),
    'minute': fields.Int(validate=TimeRangeValid(0, 59)),
    'second': fields.Int(validate=TimeRangeValid(0, 59)),
    'weeks': fields.Int(),
    'days': fields.Int(),
    'hours': fields.Int(),
    'minutes': fields.Int(),
    'seconds': fields.Int(),
    'start_date': fields.Str(validate=time_validator.date_or_datetime_valid),
    'end_date': fields.Str(validate=time_validator.date_or_datetime_valid),
    'max_instances': fields.Int(missing=1)
}

crawl_options = {
    'browser_type': fields.Str(missing='firefox', validate=OneOf(['chromium', 'firefox'])),
    'priority': fields.Int(missing=3, validate=OneOf(choices=[1, 2, 3, 4, 5])),  # 任务优先级
    'headless': fields.Bool(missing=False),  # 有头/无头模式 默认使用有头模式
    'debug': fields.Bool(missing=False),  # 是否开启调试模式,
    'referer': fields.Str(),  # 网站来路地址
    'concurrency': fields.Int(missing=5, validate=OneOf(choices=[5, 10, 15, 20, 25, 30])),  # 并发数
    'url_timeout': fields.Int(missing=30),  # 单个url超时时间
    'enabled_render_js': fields.Bool(missing=True),
    'page_wait_time': fields.Int(missing=3),  # 等待页面js渲染时间
    'ignore_ssl': fields.Bool(missing=True),  # 是否忽略证书错误
    'screenshot': fields.Bool(missing=False),  # 是否截图
    'proxy_url': fields.Str(),  # 代理
    'user_agent': fields.Str(),  # Ua
    'record_har': fields.Bool(missing=False),  # 请求networks
    'record_redirect': fields.Bool(missing=False),  # 是否记录重定向链接
    'use_browser_cache': fields.Bool(missing=True),  # 是否使用浏览器缓存
    'use_result_cache': fields.Bool(missing=True),  # 是否使用结果缓存
    'wappalyzer': fields.Bool(missing=False),  # 是否使用指纹识别
    'extract_text': fields.Bool(missing=True),  # 是否提取网页正文
    'extract_favicon': fields.Bool(missing=False),  # 是否下载网站图标
    'callback_type': fields.Str(validate=OneOf(choices=['http', 'rpc'])),
    'callback_address': fields.Str(),
    'wait_until': fields.Str(
        missing='load', validate=OneOf(choices=['domcontentloaded', 'load', 'networkidle'])),  # 控制页面何时加载成功，
    'rpc_server': fields.Str(missing=os.getenv('LOCAL_RPC_SERVER_ADDRESS'))
}

create_task_schema = {
    'customer_id': fields.Str(validate=LengthChecker(sign='自定义id', length=255)),
    'task_name': fields.Str(validate=LengthChecker(sign='任务名称', length=255)),
    'urls': fields.DelimitedList(fields.Str(validate=task_validator.url_valid), required=True),
    'schedule_type': fields.Str(missing='instantly', validate=OneOf(['instantly', 'datetime', 'interval', 'cron'])),
    'schedule_data': fields.Nested(schedule_data, missing={}),
    'crawl_options': fields.Nested(crawl_options, missing={}),
    'extra_data': fields.Str(),
}

task_id_schema = {
    'task_id': fields.Int(required=True, validate=task_validator.task_id_exist_valid)
}
