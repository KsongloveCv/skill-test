---
name: wechat-publish
description: 将 Markdown 文章发布到微信公众号的完整流程：读取 Markdown → 转换为微信兼容 HTML → 处理图片上传 → 生成最终可粘贴的 HTML。当用户提到发公众号、发布公众号、微信公众号发布、推文发布、公众号排版发布、Markdown发公众号时触发此 Skill。即使用户只说「帮我发一篇公众号文章」或「把这篇文章发到微信」，也应使用此 Skill。
---

# 发公众号 — 微信公众号文章发布流程

将 Markdown 文章完整转换为可直接粘贴到微信公众号编辑器的 HTML，并处理图片替换。

## 工作流程

### 第 1 步：读取 Markdown

1. 让用户提供 Markdown 文件路径，或直接粘贴 Markdown 内容
2. 读取文件内容，确认格式完整（标题、正文、图片引用等）

### 第 2 步：转换 HTML

运行 `scripts/md_to_wechat_html.py` 将 Markdown 转为微信兼容 HTML：

```bash
python scripts/md_to_wechat_html.py input.md --theme fresh-literary
```

主题选项：
- `fresh-literary` — 清新文艺风（默认，柔和暖色调）
- `business-professional` — 商务专业风（沉稳蓝灰）
- `tech-minimalist` — 科技极简风（黑白灰）

转换规则（所有样式必须是内联 style）详见 `references/wechat_style_guide.md`。

核心约束：
- 所有样式写在 `style=""` 属性中
- 禁止 `<style>` 标签、CSS 类名、`position`、`display: flex`
- 用 `<section>` 或 `<p>` 作容器，不用 `<div>`
- 本地图片标记为 `<!-- WECHAT_IMG_PLACEHOLDER: 描述 -->` 占位符
- 外部链接转为脚注格式 `[¹]`，文末列出链接地址

### 第 3 步：处理图片

1. 运行 `scripts/extract_images.py` 提取所有本地图片路径：

```bash
python scripts/extract_images.py input.md
```

2. 输出一份上传清单，用户需手动上传图片到微信素材库：
   - 登录微信公众平台 → 管理 → 素材管理 → 上传图片
   - 复制每张图片返回的 URL

3. 用户拿到图片 URL 后，创建 `images_map.json`：

```json
{
  "本地路径或图片描述": "https://mmbiz.qpic.cn/...",
  "images/photo1.jpg": "https://mmbiz.qpic.cn/..."
}
```

4. 运行 `scripts/replace_image_urls.py` 替换占位符：

```bash
python scripts/replace_image_urls.py output.html --map images_map.json
```

如果文章中没有本地图片（全部是网络图片或纯文字），跳过此步。

### 第 4 步：发布指引

输出最终 HTML 后，向用户提供操作说明：

1. 复制最终 HTML 代码
2. 打开微信公众号后台 → 新建图文 → 点击编辑器工具栏的「源码」按钮
3. 粘贴 HTML 代码，再点击「源码」返回可视化模式
4. 检查排版效果，特别是图片和脚注链接
5. 点击手机预览，确认手机端显示正常
6. 确认无误后发布

## 快速模式

如果用户只是想快速把一篇纯文字 Markdown 发到公众号（无本地图片），可以简化流程：

1. 运行转换脚本 → 直接得到 HTML
2. 告知用户复制粘贴到微信后台即可

不需要经过图片提取和替换步骤。

## 输出格式

最终交付给用户的包括：

1. **HTML 文件** — 可直接粘贴到微信编辑器的完整 HTML
2. **图片清单**（如有本地图片） — 需手动上传的图片列表和映射模板
3. **操作指引** — 从复制到发布的完整步骤说明

## 依赖

- Python 3.10+
- `markdown` 库（pip install markdown）

脚本位于 `scripts/` 目录，样式参考位于 `references/wechat_style_guide.md`。
