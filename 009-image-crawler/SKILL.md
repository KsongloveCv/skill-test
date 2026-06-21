---
name: image-crawler
description: >-
  按用户指定的图片类型和数量，从网络搜索并下载壁纸/插画到本地文件夹。
  当用户说「爬图」「下载图片」「图片爬虫」「帮我抓 N 张 XX 图」「二次元 20 张」
  「anime wallpaper 10」或提供「类型 + 数量」时使用。
---

# 图片爬虫（009-image-crawler）

按 **图片类型 + 数量** 批量搜索并下载图片，默认保存到 `~/Desktop/photo/`。

项目路径：`~/Desktop/AI-Test/009-image-crawler/`

## 用户输入解析

| 字段 | 示例 | 默认值 |
|------|------|--------|
| 类型 | 二次元、anime、风景、赛博朋克、猫、豪车 | 必填 |
| 数量 | 20、10 张、5 pics | `10` |
| 输出目录 | 保存到桌面 xxx | `~/Desktop/photo` |
| 分辨率 | 4K / 3840 | 宽 ≥ 1920；用户明确要求 4K 时用 `--min-width 3840` |

## 执行步骤

1. **确认参数**：类型、数量、输出目录、是否严格 4K。
2. **运行脚本**：

```bash
python3 ~/Desktop/AI-Test/009-image-crawler/scripts/download_images.py \
  --type "<图片类型>" \
  --count <数量> \
  --output "<输出目录>"
```

严格 4K 时追加 `--min-width 3840`。

3. **汇报结果**：成功张数、保存路径、失败原因（如有）。

## 示例

```bash
python3 ~/Desktop/AI-Test/009-image-crawler/scripts/download_images.py \
  --type "豪车" \
  --count 10 \
  --output ~/Desktop/photo
```

## 依赖

- `firecrawl` CLI（`~/.npm-global/bin/firecrawl`）
- API Key：`FIRECRAWL_API_KEY` 或 `~/.cursor/mcp.json` 中 `firecrawl-mcp` 配置

## 注意事项

- 图片来源于公开壁纸站搜索结果，**仅供个人壁纸/参考**，勿商用。
- 若下载失败，可放宽 `--min-width` 或更换类型关键词。
