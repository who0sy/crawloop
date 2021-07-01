# -*- coding: utf-8 -*-

import asyncio
import os
import uuid
from asyncio import QueueEmpty
from datetime import datetime

from playwright import async_playwright


class PlayWrightHandler(object):

    def __init__(self, subtask_id, url_nested_list, options={}):

        # 当前子任务id
        self.subtask_id = subtask_id

        # url队列
        self.urls_q = asyncio.Queue()

        # RPC服务端地址
        self.rpc_server = options.get('rpc_server')

        # 爬取参数
        self.url_nested_list = self.init_url_options(url_nested_list, options)
        self.url_count = len(url_nested_list)
        self.browser_type = options.pop('browser_type', 'firefox')
        self.page_wait_time = options.pop('page_wait_time', 3)
        self.headless = options.pop('headless', False)
        self.referer = options.pop('referer', None)  # TODO
        self.max_concurrent = options.pop('concurrency', 10)
        self.url_timeout = options.pop('url_timeout', 30) * 1000  # 单位为毫秒
        self.proxy_url = options.pop('proxy_url', None)
        self.user_agent = options.pop('user_agent', None)
        self.record_redirect = options.pop('record_redirect', False)  # TODO
        self.use_browser_cache = options.pop('use_browser_cache', True)  # TODO
        self.enabled_render_js = options.pop('enabled_render_js', True)  # TODO
        self.wappalyzer = options.pop('wappalyzer')
        self.wait_until = options.pop('wait_until', 'load')  # domcontentloaded/load/networkidle

        # 未完成抓取的url
        self.undone_url_ids = [url_info['url_id'] for url_info in url_nested_list]

        # 当前浏览器实例
        self.browser = None

        # 支持tls1.0和tls2.0的chrome浏览器实例
        self.chrome_browser = None

        # 浏览器使用环境
        self.browser_session = None

        # 多协程共享数据容器，主要用于存储页面回调
        self.coroutine_data_dict = {}

        # 创建截图目录
        if not os.path.exists('/usr/src/app/screenshots'):
            os.mkdir('/usr/src/app/screenshots')

        # 创建har目录
        if not os.path.exists('/usr/src/app/hars'):
            os.mkdir('/usr/src/app/hars')

    def run(self):
        """主入口"""

        # 创建事件循环
        loop = asyncio.get_event_loop()

        # 注册事件
        loop.run_until_complete(self.main())

        # 关闭事件循环
        loop.close()

        return self.undone_url_ids

    async def main(self):
        """逻辑处理程序"""

        async with async_playwright() as browser_session:
            self.browser_session = browser_session

            # 初始化参数浏览器
            if self.browser_type == 'chromium':
                self.browser = await browser_session.chromium.launch(
                    headless=self.headless, proxy={'server': 'per-context'} if self.proxy_url else None
                )
            elif self.browser_type == 'firefox':
                self.browser = await browser_session.firefox.launch(
                    headless=self.headless, proxy={'server': 'per-context'} if self.proxy_url else None
                )

            # Url入队
            for url_info in self.url_nested_list: self.urls_q.put_nowait(url_info)

            # 构造任务
            use_concurrent = self.max_concurrent if self.url_count >= self.max_concurrent else self.url_count
            tasks = [self.handle_tasks() for i in range(use_concurrent)]

            # 执行任务 超时时间设置为600秒
            await asyncio.wait(tasks, timeout=600)

            # 关闭浏览器
            await self.browser.close()

            # 关闭tls浏览器
            # if self.chrome_browser: await self.chrome_browser.close()

    @staticmethod
    def init_url_options(url_nested_list, options):
        """
        合并Options
        :return:
        """

        for url_info in url_nested_list:
            for option, v in options.items():
                if option not in url_info['url_options']:
                    url_info['url_options'][option] = v
        return url_nested_list

    async def handle_tasks(self):
        """处理任务逻辑"""
        while not self.urls_q.empty():
            # 取得容器内待消费的url
            try:
                url_info = self.urls_q.get_nowait()
            except QueueEmpty as e:
                break

            # url参数容器
            url_options = url_info.pop('url_options', {})

            # 初始化har文件id
            har_uuid = str(uuid.uuid4())

            # 初始化page回调容器
            http_archive_dict, redirect_result = {'url_address': url_info['url_address'], 'hars': []}, []

            # 创建page
            page = await self.browser.newPage(
                ignoreHTTPSErrors=url_options.get('ignore_ssl', True),
                javaScriptEnabled=url_options.get('enabled_render_js', True),
                userAgent=url_options.get('user_agent'),
                proxy={"server": url_options.get('proxy_url')} if url_options.get('proxy_url') else None,
                extraHTTPHeaders={"Accept-Language": "zh-CH,en;q=0.5"}
            )

            # 回调处理所有response
            page.on('response', self.handle_response(url_options.get('record_har'), http_archive_dict, redirect_result))

            # 请求
            try:
                response = await page.goto(url_info['url_address'], waitUntil=self.wait_until, timeout=self.url_timeout)
                await asyncio.sleep(self.page_wait_time)
            except Exception as e:
                response = None

            # 获取响应时间
            try:
                response_time = int(response.request.timing['responseEnd'])
            except Exception as e:
                response_time = None

            # 获取页面渲染时间
            try:
                load_complete_time_str = await page.evaluate(
                    """window.performance.timing.loadEventEnd - window.performance.timing.navigationStart""")
                load_complete_time = None if int(load_complete_time_str) < 0 else int(load_complete_time_str)
            except Exception as e:
                load_complete_time = None

            # 获取cookies
            cookies = await page.context.cookies([url_info['url_address']])
            for each in cookies:
                if isinstance(each.get('expires'), float):
                    each['expires'] = int(each['expires'])

            # 获取title
            try:
                title = await page.title()
                if title in ('Problem loading page', 'Server Not Found'):
                    title = None
            except Exception as e:
                title = None

            # 获取content
            try:
                content = await page.content()
            except Exception as e:
                content = None

            # 获取headers
            try:
                response_headers = response.headers
            except Exception as e:
                response_headers = {}

            # 处理截图
            if url_options.get('screenshot', False) and redirect_result:
                screenshot_id = str(uuid.uuid4())
                action_count = 0
                while action_count < 10:
                    try:
                        await page.screenshot(path=f'/usr/src/app/screenshots/{screenshot_id}.png', fullPage=True)
                        break
                    except Exception as e:
                        action_count += 1
                        continue
                if action_count == 10:
                    screenshot_id = None
            else:
                screenshot_id = None

            # 融合结果
            result = {
                'url_id': url_info['url_id'],
                'url_address': url_info['url_address'],
                'subtask_id': self.subtask_id,
                'har_uuid': har_uuid if url_options.get('record_har') is True else None,
                'redirect_chain': redirect_result,
                'current_url': page.url,
                'cookies': cookies, 'title': title,
                'content': content, 'response_headers': response_headers,
                'screenshot_id': screenshot_id,
                'http_archive_dict': http_archive_dict,
                'finished_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'rpc_server': self.rpc_server,
                'response_time': response_time,
                'load_complete_time': load_complete_time
            }

            # 从未完成列表内移除
            self.undone_url_ids.remove(url_info['url_id'])

            # 释放cpu执行权，重新进入内核缓冲区，避免某一协程长时间占有cpu控制权从而降级为僵尸进程阻塞相应的协程事件轮询
            await asyncio.sleep(1)

            # 设置退出条件
            await page.context.close()

            # 设置浏览器类型如果是'chromium'对爬虫结果预处理
            if self.browser_type == 'chromium' and not redirect_result:
                result['content'] = None
                result['current_url'] = None
                result['title'] = None

            # 异步发送存储任务
            from worker import celery_app
            celery_app.send_task(name='save_results', queue='results', kwargs=result)

    def handle_response(self, record_har, http_archive_dict, redirect_result):
        """
        回调处理response
        :return:
        """

        def real_handle_response(response):
            self_request = response.request

            # 记录har
            if record_har:
                http_archive_dict['hars'].append({
                    'request_url': self_request.url,
                    'http_method': self_request.method,
                    'request_headers': self_request.headers,
                    'status_code': response.status,
                    'response_headers': response.headers
                })

            # 判别是否是导航请求并记录重定向
            if self_request.isNavigationRequest() and not self_request.frame.parentFrame:
                redirect_result.append({'redirect_url': response.url, 'redirect_http_code': response.status})

        return real_handle_response
