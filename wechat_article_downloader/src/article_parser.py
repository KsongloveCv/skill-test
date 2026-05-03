"""
文章内容解析器：从 HTML 或剪贴板文本中提取结构化信息
"""

import logging
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

def parse_html(html):
    """
    解析微信公众号文章 HTML
    返回 dict: {'title': ..., 'author': ..., 'publish_time': ..., 'content': ...}
    """
    soup = BeautifulSoup(html, 'lxml')  # 或 'html.parser'
    title = _extract_title(soup)
    author = _extract_author(soup)
    publish_time = _extract_publish_time(soup)
    content = _extract_content(soup)

    return {
        'title': title,
        'author': author,
        'publish_time': publish_time,
        'content': content
    }

def _extract_title(soup):
    # 多种可能的选择器
    for selector in ['h1.rich_media_title', '#activity-name', 'title']:
        tag = soup.select_one(selector)
        if tag:
            return tag.get_text().strip()
    return '未知标题'

def _extract_author(soup):
    tag = soup.select_one('#js_name, .rich_media_meta_text span')
    if tag:
        return tag.get_text().strip()
    return '未知作者'

def _extract_publish_time(soup):
    tag = soup.select_one('#publish_time, .rich_media_meta_text em')
    if tag:
        return tag.get_text().strip()
    return ''

def _extract_content(soup):
    content_div = soup.select_one('#js_content, .rich_media_content')
    if content_div:
        # 移除 script, style 等
        for tag in content_div(['script', 'style']):
            tag.decompose()
        return str(content_div)
    return ''