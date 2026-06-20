"""替换 HTML 中的微信图片占位符为实际 URL

用法:
    python replace_image_urls.py input.html --map images_map.json [--output output.html]

images_map.json 格式:
    {
        "本地路径或描述": "微信素材库 URL",
        ...
    }

将 HTML 中 <!-- WECHAT_IMG_PLACEHOLDER: xxx --> 替换为对应的微信图片 URL。
"""

import argparse
import json
import re
import sys
from pathlib import Path

PLACEHOLDER_PATTERN = re.compile(
    r'<!-- WECHAT_IMG_PLACEHOLDER: (.+?) -->'
)


def load_url_map(map_path: str) -> dict:
    """加载图片 URL 映射"""
    path = Path(map_path)
    if not path.exists():
        print(f"映射文件不存在: {map_path}", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def replace_placeholders(html: str, url_map: dict) -> str:
    """替换 HTML 中的图片占位符"""
    def replacer(match):
        key = match.group(1).strip()
        url = url_map.get(key)
        if not url:
            # 尝试模糊匹配：去掉路径前缀，只用文件名
            filename = Path(key).name
            for map_key, map_url in url_map.items():
                if Path(map_key).name == filename:
                    url = map_url
                    break
        if url:
            return url
        # 未找到映射，保留占位符并警告
        print(f"警告: 未找到图片映射 '{key}'，占位符保留", file=sys.stderr)
        return match.group(0)

    # 替换 src="<!-- WECHAT_IMG_PLACEHOLDER: xxx -->" 中的占位符
    html = re.sub(
        r'src="<!-- WECHAT_IMG_PLACEHOLDER: (.+?) -->"',
        lambda m: f'src="{replacer(m)}"',
        html,
    )

    # 替换游离的注释占位符
    html = PLACEHOLDER_PATTERN.sub(replacer, html)

    return html


def main():
    parser = argparse.ArgumentParser(description="替换 HTML 中的微信图片占位符")
    parser.add_argument("input", help="输入 HTML 文件路径")
    parser.add_argument("--map", "-m", required=True, help="图片 URL 映射 JSON 文件")
    parser.add_argument("--output", "-o", help="输出 HTML 文件路径（默认同名 _final.html）")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"文件不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    html = input_path.read_text(encoding="utf-8")
    url_map = load_url_map(args.map)

    result = replace_placeholders(html, url_map)

    output_path = Path(args.output) if args.output else input_path.parent / f"{input_path.stem}_final.html"
    output_path.write_text(result, encoding="utf-8")
    print(f"替换完成，已输出: {output_path}")


if __name__ == "__main__":
    main()
