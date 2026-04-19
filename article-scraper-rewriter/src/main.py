#!/usr/bin/env python3
"""主入口模块"""

import argparse
import sys
from pathlib import Path
import os
# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scraper import scrape_article
from src.rewriter import rewrite_content
from src.extractor import extract_keywords_tags
from src.utils import load_config, format_output


def process_article(
    url: str,
    language: str = "auto",
    max_keywords: int = 5,
    max_tags: int = 3,
    config_path: str = "config.yaml"
) -> list:
    """
    处理文章的主函数
    
    Args:
        url: 目标文章 URL
        language: 文章语言（默认自动检测）
        max_keywords: 关键词数量
        max_tags: 标签数量
        config_path: 配置文件路径
    
    Returns:
        格式化的输出字符串
    """
    # 加载配置
    config = load_config(config_path)
    
    # Step 1: 抓取文章
    print(f"正在抓取文章: {url}", file=sys.stderr)
    scraped = scrape_article(url, config)
    if not scraped["content"]:
        return "错误：无法提取文章内容，请检查 URL 是否有效。"
    
    print(f"标题: {scraped['title']}", file=sys.stderr)
    print(f"正文长度: {len(scraped['content'])} 字符", file=sys.stderr)
    
    # Step 2: 润色内容
    print("正在润色内容...", file=sys.stderr)
    rewritten = rewrite_content(
        title=scraped["title"],
        content=scraped["content"],
        config=config,
        language=language
    )
    
    # Step 3: 提取关键词和标签
    print("正在提取关键词和标签...", file=sys.stderr)
    kw_tags = extract_keywords_tags(
        content=rewritten["content"],
        config=config,
        max_keywords=max_keywords,
        max_tags=max_tags
    )
    
    # Step 4: 格式化输出
    output = format_output(
        title=rewritten["title"],
        content=rewritten["content"],
        keywords=kw_tags["keywords"],
        tags=kw_tags["tags"],
        url=url
    )
    
    return [rewritten["title"], output]

def output_result(result: str, title: str, output_path: str = "output"):
    
    """输出结果到文件或标准输出"""
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), output_path)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{title}.md")

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"结果已保存至: {output_path}", file=sys.stderr)
    else:
        print(result)


def clean_text() -> str:
    """清洗正文文本"""
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'original_html')
    output_path = os.path.join(output_dir, f"1.html")
    print(output_path)
    # 读取整个文件
    content = ""
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    content = soup.find('div', class_='postBody').get_text(strip=True)
    print(content)

def main():
    parser = argparse.ArgumentParser(description="文章抓取与润色工具")

    parser.add_argument("--url", required=True, help="目标文章 URL")
    parser.add_argument("--language", default="auto", help="文章语言（默认自动检测）")
    parser.add_argument("--max-keywords", type=int, default=5, help="关键词数量（默认 5）")
    parser.add_argument("--max-tags", type=int, default=3, help="标签数量（默认 3）")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--output", default="output", help="输出文件路径（可选）")
    
    args = parser.parse_args()
    
    title, content = process_article(
        url=args.url,
        language=args.language,
        max_keywords=args.max_keywords,
        max_tags=args.max_tags,
        config_path=args.config
    )
    
    output_result(content, title, args.output)
    # if args.output:
    #     with open(args.output, "w", encoding="utf-8") as f:
    #         f.write(result)
    #     print(f"结果已保存至: {args.output}", file=sys.stderr)
    # else:
    #     print(result)


if __name__ == "__main__":
    main()