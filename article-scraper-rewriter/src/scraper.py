"""网页抓取与内容提取模块"""

import re
import time
import os
import requests
from bs4 import BeautifulSoup
from readability import Document
from typing import Dict, Optional
import hashlib

def scrape_article(url: str, config: Dict) -> Dict[str, str]:
    """
    从 URL 抓取文章内容
    
    Returns:
        {"title": str, "content": str}
    """
    scraper_config = config.get("scraping", {})
    
    headers = {
        "User-Agent": scraper_config.get("user_agent", 
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    }
    timeout = scraper_config.get("timeout", 30)
    retry = scraper_config.get("retry", 3)
    delay = scraper_config.get("delay", 1)
    
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'original_html')
    os.makedirs(output_dir, exist_ok=True)
    # 重试机制
    for attempt in range(retry):
        try:
            print(url)
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            response.encoding = 'utf-8'
            print(response.status_code)
            if response.status_code != 200:
                raise Exception(f"HTTP Status {response.status_code} : {url}")
            # 自动检测编码
            # if response.encoding == "ISO-8859-1":
            #     response.encoding = response.apparent_encoding
            
            html = response.text
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title').get_text(strip=True)
            # 将 HTML 写入到 original_html 目录
            # url_hash = hashlib.md5(url.encode()).hexdigest()
            
            output_file = os.path.join(output_dir, f'{title}.html')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"HTML 已保存到: {output_file}")
            
            break
        except Exception as e:
            if attempt == retry - 1:
                raise Exception(f"无法获取网页内容: {str(e)}")
            time.sleep(delay * (attempt + 1))
    
    # 使用 readability 提取主要内容
    doc = Document(html)
    
    title = doc.title()
    # content_html = doc.summary()

    # 如果 readability 未提取到标题，尝试从 h1 或 og:title 获取
    if not title:
        soup = BeautifulSoup(html, "lxml")
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
        else:
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                title = og_title["content"]
            else:
                title = "未提取到标题"
    
    # 清洗文本
    content = clean_text(html)

    output_file = os.path.join(output_dir, f'{title}.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"文本 已保存到: {output_file}")
    
    return {
        "title": clean_title(title),
        "content": content
    }


def clean_title(title: str) -> str:
    """清洗标题"""
    # 移除多余空白
    title = re.sub(r"\s+", " ", title)
    # 移除常见网站后缀
    title = re.sub(r"\s*[-–|]\s*.*?(网|博客|频道|专栏)$", "", title)
    return title.strip()


def clean_text(text: str) -> str:
    """清洗正文文本"""
    # 解析正文 HTML 为纯文本
    soup = BeautifulSoup(text, "html.parser")
    
    # 移除不需要的元素
    for element in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
        element.decompose()
          
    content = soup.find('div', class_='postBody').get_text(strip=True)
    return content



    # 替换多个换行为双换行
    text = re.sub(r"\n{3,}", "\n\n", text)
    # 移除行首尾空白
    lines = [line.strip() for line in text.split("\n")]
    # 过滤空行和太短的行（可能是广告/导航残留）
    lines = [line for line in lines if len(line) > 10 or line == ""]
    # 合并连续空行
    text = "\n".join(lines)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    
    return text.strip()