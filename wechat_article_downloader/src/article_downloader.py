"""
文章下载模块：支持直接 URL 下载、剪贴板获取
"""

import os
import time
import logging
import requests
import pyperclip
from .utils import rate_limit, safe_filename, ensure_dir
from .article_parser import parse_html
import config

logger = logging.getLogger(__name__)

class ArticleDownloader:
    def __init__(self, save_dir=config.DEFAULT_SAVE_DIR):
        self.save_dir = save_dir
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)
        ensure_dir(save_dir)

    @rate_limit(min_delay=config.MIN_REQUEST_DELAY, max_delay=config.MAX_REQUEST_DELAY)
    def download_from_url(self, url):
        """
        通过 URL 下载文章，保存为 HTML 文件
        返回 (success, filepath)
        """
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            html = resp.text

            # 解析提取信息
            article = parse_html(html)
            if not article['title']:
                logger.warning("未能解析出标题，可能不是公众号文章")
                return False, None

            # 生成安全文件名
            base_name = safe_filename(article['title'], 50)
            file_path = os.path.join(self.save_dir, f"{base_name}.html")

            # 构造完整 HTML 并保存
            full_html = self._build_html(article)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(full_html)

            logger.info(f"文章已保存：{file_path}")
            return True, file_path

        except requests.HTTPError as e:
            logger.error(f"HTTP 错误：{e}")
            return False, None
        except Exception as e:
            logger.error(f"下载失败：{e}")
            return False, None

    def save_from_clipboard(self, title_hint='未命名文章'):
        """
        从剪贴板获取文章内容（假设已在微信中全选复制）
        保存为纯文本或 HTML（取决于剪贴板内容）
        """
        # 尝试获取 HTML 格式（win32clipboard 可能需要）
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_HTML):
                html = win32clipboard.GetClipboardData(win32clipboard.CF_HTML)
                win32clipboard.CloseClipboard()
                article = parse_html(html)
                base_name = safe_filename(article['title'] or title_hint, 50)
                file_path = os.path.join(self.save_dir, f"{base_name}.html")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                logger.info(f"从剪贴板 HTML 保存至 {file_path}")
                return True, file_path
        except Exception:
            pass

        # 回退到纯文本
        try:
            text = pyperclip.paste()
            if text:
                base_name = safe_filename(title_hint, 50)
                file_path = os.path.join(self.save_dir, f"{base_name}.txt")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                logger.info(f"从剪贴板纯文本保存至 {file_path}")
                return True, file_path
        except Exception as e:
            logger.error(f"获取剪贴板内容失败：{e}")

        return False, None

    def _build_html(self, article):
        """构建完整的 HTML 文档"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{article['title']}</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        img {{ max-width: 100%; }}
    </style>
</head>
<body>
    <h1>{article['title']}</h1>
    <p>作者：{article['author']} &nbsp; 发布时间：{article['publish_time']}</p>
    <div class="content">{article['content']}</div>
</body>
</html>"""