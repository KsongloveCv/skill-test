"""Markdown → 微信公众号兼容 HTML 转换器

用法:
    python md_to_wechat_html.py input.md [--output output.html] [--theme fresh-literary]

输出微信编辑器可直接粘贴的内联样式 HTML，本地图片标记为占位符。
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    print("需要 markdown 库: pip install markdown", file=sys.stderr)
    sys.exit(1)


# 主题配色定义
THEMES = {
    "fresh-literary": {
        "primary": "#3f3f3f",
        "secondary": "#888",
        "accent": "#c05b4a",
        "bg": "#f9f5f0",
        "code_bg": "#f6f6f6",
        "quote_border": "#c05b4a",
    },
    "business-professional": {
        "primary": "#2b2b2b",
        "secondary": "#666",
        "accent": "#1a6fa5",
        "bg": "#f8f8f8",
        "code_bg": "#f0f0f0",
        "quote_border": "#1a6fa5",
    },
    "tech-minimalist": {
        "primary": "#222",
        "secondary": "#999",
        "accent": "#222",
        "bg": "#fff",
        "code_bg": "#f5f5f5",
        "quote_border": "#222",
    },
}


def build_inline_styles(theme: dict) -> dict:
    """根据主题配色生成各元素的完整内联样式字典"""
    c = theme
    return {
        "wrapper": f"padding: 0 16px;",
        "h1": (
            f"text-align: center; font-size: 22px; font-weight: bold;"
            f" color: {c['primary']}; margin-top: 1.5em; margin-bottom: 1em;"
        ),
        "h2": (
            f"font-size: 18px; font-weight: bold; color: {c['primary']};"
            f" margin-top: 1.5em; margin-bottom: 0.8em;"
            f" border-bottom: 1px solid #eee; padding-bottom: 0.3em;"
        ),
        "h3": (
            f"font-size: 16px; font-weight: bold; color: {c['primary']};"
            f" margin-top: 1.2em; margin-bottom: 0.6em;"
        ),
        "p": (
            f"font-size: 15px; line-height: 1.8; letter-spacing: 0.5px;"
            f" color: {c['primary']}; margin-bottom: 1em;"
        ),
        "strong": f"color: {c['accent']}; font-weight: bold;",
        "em": f"font-style: italic; color: {c['secondary']};",
        "code_inline": (
            f"background-color: {c['code_bg']}; border-radius: 3px;"
            f" padding: 2px 4px; font-size: 14px;"
            f" font-family: Menlo, Monaco, 'Courier New', monospace;"
            f" color: {c['accent']};"
        ),
        "blockquote": (
            f"border-left: 3px solid {c['quote_border']};"
            f" background-color: {c['bg']}; padding: 10px 15px;"
            f" margin: 1.5em 0; font-size: 14px; color: {c['secondary']};"
        ),
        "pre": (
            f"background-color: {c['code_bg']}; border-radius: 5px;"
            f" padding: 12px; margin: 1.5em 0; font-size: 13px;"
            f" line-height: 1.6; white-space: pre-wrap;"
            f" font-family: Menlo, Monaco, 'Courier New', monospace;"
            f" overflow-x: auto;"
        ),
        "ul": (
            f"font-size: 15px; line-height: 1.8; color: {c['primary']};"
            f" margin-bottom: 1em; padding-left: 2em;"
        ),
        "ol": (
            f"font-size: 15px; line-height: 1.8; color: {c['primary']};"
            f" margin-bottom: 1em; padding-left: 2em;"
        ),
        "li": f"margin-bottom: 0.5em;",
        "img": (
            f"max-width: 100%; display: block; margin: 1.5em auto;"
            f" border-radius: 4px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);"
        ),
        "img_caption": (
            f"text-align: center; font-size: 13px; color: {c['secondary']};"
            f" margin-top: 0.3em; margin-bottom: 1.5em;"
        ),
        "hr": f"border: none; border-top: 1px solid #eee; margin: 2em 0;",
        "table": (
            f"width: 100%; border-collapse: collapse; margin: 1.5em 0; font-size: 14px;"
        ),
        "th": (
            f"background-color: {c['bg']}; font-weight: bold;"
            f" color: {c['primary']}; border: 1px solid #ddd; padding: 8px 10px;"
        ),
        "td": (
            f"border: 1px solid #ddd; padding: 8px 10px; color: {c['primary']};"
        ),
        "footnote_area": (
            f"margin-top: 2em; padding-top: 1em; border-top: 1px solid #eee;"
            f" font-size: 13px; color: {c['secondary']};"
        ),
        "footnote_item": (
            f"font-size: 13px; color: {c['secondary']};"
            f" margin-bottom: 0.3em;"
        ),
    }


def convert_md_to_html(md_text: str, theme_name: str = "fresh-literary") -> str:
    """将 Markdown 文本转换为带内联样式的微信兼容 HTML"""
    theme = THEMES.get(theme_name, THEMES["fresh-literary"])
    styles = build_inline_styles(theme)

    # 用 markdown 库解析，关闭 toc 的 id 生成避免干扰样式注入
    extensions = ["fenced_code", "tables", "codehilite"]
    extension_configs = {"codehilite": {"guess_lang": False}}
    md = markdown.Markdown(extensions=extensions, extension_configs=extension_configs)
    raw_html = md.convert(md_text)

    # 先处理本地图片（标记占位符），再注入样式，避免属性顺序干扰
    raw_html = mark_local_images(raw_html)

    # 逐步注入内联样式
    styled_html = inject_styles(raw_html, styles)

    # 收集链接并转换为脚注
    styled_html = convert_links_to_footnotes(styled_html, styles)

    # 包裹在 section 容器中
    result = f'<section style="{styles["wrapper"]}">\n{styled_html}\n</section>'

    return result


def inject_styles(html: str, styles: dict) -> str:
    """为 HTML 元素注入内联样式"""

    # h1（兼容带 id/class 等属性的标签）
    html = re.sub(
        r"<h1(?!\s+style=)[^>]*>",
        lambda m: m.group(0).replace("<h1", f'<h1 style="{styles["h1"]}"'),
        html,
    )
    # h2
    html = re.sub(
        r"<h2(?!\s+style=)[^>]*>",
        lambda m: m.group(0).replace("<h2", f'<h2 style="{styles["h2"]}"'),
        html,
    )
    # h3
    html = re.sub(
        r"<h3(?!\s+style=)[^>]*>",
        lambda m: m.group(0).replace("<h3", f'<h3 style="{styles["h3"]}"'),
        html,
    )
    # h4-h6 按 h3 样式处理
    for tag in ["h4", "h5", "h6"]:
        html = re.sub(
            rf"<{tag}(?!\s+style=)[^>]*>",
            lambda m: m.group(0).replace(f"<{tag}", f'<{tag} style="{styles["h3"]}"'),
            html,
        )

    # p（排除已在 blockquote/pre/table 内的 p）
    html = re.sub(
        r"<p(?!\s+style=)>",
        f'<p style="{styles["p"]}">',
        html,
    )

    # strong
    html = re.sub(
        r"<strong>",
        f'<strong style="{styles["strong"]}">',
        html,
    )

    # em
    html = re.sub(
        r"<em>",
        f'<em style="{styles["em"]}">',
        html,
    )

    # 行内 code（非 pre 内的）
    html = re.sub(
        r"<code(?!\s+class=)>",
        f'<code style="{styles["code_inline"]}">',
        html,
    )

    # blockquote
    html = re.sub(
        r"<blockquote>",
        f'<blockquote style="{styles["blockquote"]}">',
        html,
    )

    # pre
    html = re.sub(
        r"<pre>",
        f'<pre style="{styles["pre"]}">',
        html,
    )

    # ul
    html = re.sub(
        r"<ul>",
        f'<ul style="{styles["ul"]}">',
        html,
    )

    # ol
    html = re.sub(
        r"<ol>",
        f'<ol style="{styles["ol"]}">',
        html,
    )

    # li
    html = re.sub(
        r"<li>",
        f'<li style="{styles["li"]}">',
        html,
    )

    # img（注入样式但不破坏现有属性）
    html = re.sub(
        r"<img(?!\s+style=)",
        f'<img style="{styles["img"]}"',
        html,
    )

    # hr
    html = re.sub(
        r"<hr\s*/?>",
        f'<hr style="{styles["hr"]}">',
        html,
    )

    # table
    html = re.sub(
        r"<table>",
        f'<table style="{styles["table"]}">',
        html,
    )

    # th
    html = re.sub(
        r"<th>",
        f'<th style="{styles["th"]}">',
        html,
    )

    # td
    html = re.sub(
        r"<td>",
        f'<td style="{styles["td"]}">',
        html,
    )

    return html


LINK_PATTERN = re.compile(r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>', re.DOTALL)
SUPERSCRIPT_MAP = {
    1: "¹", 2: "²", 3: "³",
    4: "⁴", 5: "⁵", 6: "⁶",
    7: "⁷", 8: "⁸", 9: "⁹",
    10: "¹⁰", 11: "¹¹",
}


def convert_links_to_footnotes(html: str, styles: dict) -> str:
    """将 <a> 链接转为脚注格式"""
    links = LINK_PATTERN.findall(html)
    if not links:
        return html

    footnote_num = 1
    for url, text in links:
        sup = SUPERSCRIPT_MAP.get(footnote_num, f"[{footnote_num}]")
        html = html.replace(
            f'<a href="{url}">{text}</a>',
            f'{text}<sup style="font-size:12px;color:#888;">{sup}</sup>',
        )
        footnote_num += 1

    # 文末脚注区
    footnotes = []
    for idx, (url, _) in enumerate(links, 1):
        sup = SUPERSCRIPT_MAP.get(idx, f"[{idx}]")
        footnotes.append(
            f'<p style="{styles["footnote_item"]}">{sup} {url}</p>'
        )

    footnote_section = (
        f'<section style="{styles["footnote_area"]}">\n'
        + "\n".join(footnotes)
        + "\n</section>"
    )

    return html + "\n" + footnote_section


def mark_local_images(html: str) -> str:
    """将本地图片 src 替换为占位符，保留 alt 文本作为描述"""
    IMG_TAG_PATTERN = re.compile(r'<img\s[^>]*?>', re.DOTALL)

    def replace_img_tag(match):
        tag = match.group(0)
        src_match = re.search(r'src="([^"]+)"', tag)
        alt_match = re.search(r'alt="([^"]*)"', tag)
        if not src_match:
            return tag
        src = src_match.group(1)
        alt = alt_match.group(1) if alt_match else ""
        if not src.startswith(("http://", "https://", "//", "data:")):
            placeholder = f"<!-- WECHAT_IMG_PLACEHOLDER: {alt or src} -->"
            tag = re.sub(r'src="[^"]+"', f'src="{placeholder}"', tag)
        return tag

    return IMG_TAG_PATTERN.sub(replace_img_tag, html)


def replace_local_src_no_alt(match):
    """处理没有 alt 属性的本地图片"""
    src = match.group(1)
    if not src.startswith(("http://", "https://", "//")):
        placeholder = f"<!-- WECHAT_IMG_PLACEHOLDER: {src} -->"
        return f'src="{placeholder}"'
    return match.group(0)


def main():
    parser = argparse.ArgumentParser(description="Markdown → 微信公众号 HTML 转换器")
    parser.add_argument("input", help="输入 Markdown 文件路径")
    parser.add_argument("--output", "-o", help="输出 HTML 文件路径（默认同名 .html）")
    parser.add_argument(
        "--theme", "-t",
        choices=list(THEMES.keys()),
        default="fresh-literary",
        help="排版主题（默认: fresh-literary）",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"文件不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    md_text = input_path.read_text(encoding="utf-8")
    html = convert_md_to_html(md_text, args.theme)

    output_path = Path(args.output) if args.output else input_path.with_suffix(".html")
    output_path.write_text(html, encoding="utf-8")
    print(f"已输出: {output_path}")


if __name__ == "__main__":
    main()
