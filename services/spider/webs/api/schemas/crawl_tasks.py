# -*- coding: utf-8 -*-

from webargs import fields

from webs.api.schemas import OneOf

create_crawl_task_schema = {
    'subtask_id': fields.Int(required=True),
    'url_nested_list': fields.DelimitedList(fields.Nested({
        'url_id': fields.Int(required=True),
        'url_address': fields.Str(required=True),
        'url_options': fields.Dict(missing={})
    }), required=True),
    'options': fields.Nested({
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
        'wait_until': fields.Str(
            missing='load', validate=OneOf(choices=['domcontentloaded', 'load', 'networkidle'])),  # 控制页面何时加载成功
        'rpc_server': fields.Str(required=True)
    }, missing={})
}
