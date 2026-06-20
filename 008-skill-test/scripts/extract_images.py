"""提取 Markdown 文件中的本地图片路径，生成上传清单

用法:
    python extract_images.py input.md [--output images_list.txt]

扫描 Markdown 中的图片引用（![alt](path)），筛选出本地路径，
输出一份清单供用户手动上传到微信素材库。
"""

import argparse
import re
import sys
from pathlib import Path


IMG_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
IMG_HTML_PATTERN = re.compile(r'<img[^>]*?src="([^"]+)"[^>]*?alt="([^"]*)"', re.IGNORECASE)


def extract_local_images(md_text: str) -> list[dict]:
    """提取所有本地图片引用，返回 [{path, alt, line}]"""
    images = []
    lines = md_text.split("\n")

    for line_num, line in enumerate(lines, 1):
        # Markdown 语法
        for match in IMG_PATTERN.finditer(line):
            alt, src = match.group(1), match.group(2)
            if not src.startswith(("http://", "https://", "//", "data:")):
                images.append({"path": src, "alt": alt, "line": line_num})

        # HTML img 标签
        for match in IMG_HTML_PATTERN.finditer(line):
            src, alt = match.group(1), match.group(2)
            if not src.startswith(("http://", "https://", "//", "data:")):
                images.append({"path": src, "alt": alt, "line": line_num})

    return images


def format_image_list(images: list[dict]) -> str:
    """格式化输出清单"""
    if not images:
        return "未找到本地图片引用。\n"

    lines = ["本地图片上传清单（请逐个上传到微信素材库，记录返回的 URL）：", ""]
    for idx, img in enumerate(images, 1):
        lines.append(f"{idx}. 路径: {img['path']}")
        if img["alt"]:
            lines.append(f"   描述: {img['alt']}")
        lines.append(f"   微信URL: ____________________（上传后填写）")
        lines.append("")

    lines.append("---")
    lines.append("上传步骤：")
    lines.append("1. 登录微信公众平台 → 管理 → 素材管理")
    lines.append("2. 点击「上传图片」逐个上传清单中的图片")
    lines.append("3. 上传成功后复制每张图片的 URL")
    lines.append("4. 填入上方对应位置")
    lines.append("5. 运行 replace_image_urls.py 替换 HTML 中的占位符")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="提取 Markdown 中的本地图片路径")
    parser.add_argument("input", help="输入 Markdown 文件路径")
    parser.add_argument("--output", "-o", help="输出清单文件路径（默认 images_list.txt）")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"文件不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    md_text = input_path.read_text(encoding="utf-8")
    images = extract_local_images(md_text)

    output_text = format_image_list(images)
    output_path = Path(args.output) if args.output else input_path.parent / "images_list.txt"
    output_path.write_text(output_text, encoding="utf-8")

    print(f"找到 {len(images)} 张本地图片")
    print(f"清单已输出: {output_path}")


if __name__ == "__main__":
    main()
