# -*- coding: utf-8 -*-

import os
import requests

from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

favicon_link_rules = [
    'icon',
    'shortcut icon',
    'apple-touch-icon',
    'apple-touch-icon-precomposed',
]

meta_names = ['msapplication-TileImage', 'og:image']

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
}


def get_favicon_link(url, html):
    """
    获取网站图标链接
    :param url:
    :param html:
    :return:
    """

    # 正则匹配网站源码是否包含图标链接
    soup = BeautifulSoup(html, features='html.parser')

    # 查找link标签
    for rule in favicon_link_rules:
        favicon_tag = soup.find('link', attrs={'rel': lambda r: r and r.lower() == rule, 'href': True})
        if favicon_tag:
            favicon_href = favicon_tag.get('href', '').strip()
            return fmt_link(url, favicon_href)

    # 查找meta标签
    for meta_tag in soup.find_all('meta', attrs={'content': True}):
        meta_type = meta_tag.get('name') or meta_tag.get('property') or ''.lower()
        for name in meta_names:
            if meta_type == name.lower():
                favicon_href = meta_tag.get('href', '').strip()
                return fmt_link(url, favicon_href)

    # 请求根目录下是否存在/favicon.ico文件
    root_icon_link = get_root_dir_icon(url)
    if root_icon_link:
        return root_icon_link, 'ico'

    return None, None


def fmt_link(website_url, href):
    """
    格式化标签
    :param website_url:
    :param href:
    :return: favicon_link, ext
    """

    if not href or href.startswith('data:image/'):
        return None, None

    if not urlparse(href).netloc:
        href = urljoin(website_url, href)

    if urlparse(href).netloc:
        url_parsed = href
    else:
        url_parsed = urljoin(website_url, href)

    url_parsed = urlparse(url_parsed, scheme=urlparse(website_url).scheme)
    _, ext = os.path.splitext(url_parsed.path)
    favicon_url = url_parsed.geturl()
    try:
        response = requests.get(favicon_url, timeout=30, allow_redirects=True, verify=False, headers=headers)
        if response.status_code == 200 and response.headers['Content-Type'].startswith('image'):
            return favicon_url, ext[1:].lower()
    except Exception as e:
        return None, None
    return None, None


def get_root_dir_icon(url):
    try:
        parsed = urlparse(url)
        favicon_url = parsed.scheme + "://" + parsed.netloc + '/favicon.ico'
        response = requests.get(favicon_url, timeout=30, allow_redirects=True, verify=False, headers=headers)
        if response.status_code == 200 and response.headers['Content-Type'].startswith('image'):
            return response.url
    except Exception as e:
        return

    return
