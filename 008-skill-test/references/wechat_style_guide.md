# 微信公众号内联样式规范

微信公众号编辑器只接受内联样式，所有样式必须写在 `style=""` 中。

## 通用约束

- 禁止 `<style>` 标签、CSS 类名、外部样式表
- 禁止 `position`、`z-index`、`display: flex`、`@media`、CSS 动画、伪类
- 用 `<section>` 或 `<p>` 作块级容器，避免 `<div>`（微信会把 div 转 p 导致布局异常）
- 图片链接使用占位符 `<!-- WECHAT_IMG_PLACEHOLDER: 图片描述 -->`
- 链接使用脚注格式 `[¹]`，文末列出地址

## 清新文艺风（默认）

柔和温暖色调，适合生活随笔、读书笔记、个人分享。

### 基础变量

```
主色: #3f3f3f（深灰）
辅色: #888（中灰）
强调色: #c05b4a（暖红棕）
背景色: #f9f5f0（暖白）
代码背景: #f6f6f6
引用边框色: #c05b4a
```

### h1（文章主标题）

```
text-align: center;
font-size: 22px;
font-weight: bold;
color: #3f3f3f;
margin-top: 1.5em;
margin-bottom: 1em;
```

### h2（一级小节标题）

```
font-size: 18px;
font-weight: bold;
color: #3f3f3f;
margin-top: 1.5em;
margin-bottom: 0.8em;
border-bottom: 1px solid #eee;
padding-bottom: 0.3em;
```

### h3（二级小节标题）

```
font-size: 16px;
font-weight: bold;
color: #3f3f3f;
margin-top: 1.2em;
margin-bottom: 0.6em;
```

### 正文段落

```
font-size: 15px;
line-height: 1.8;
letter-spacing: 0.5px;
color: #3f3f3f;
margin-bottom: 1em;
```

### 加粗 `<strong>`

```
color: #c05b4a;
font-weight: bold;
```

### 斜体 `<em>`

```
font-style: italic;
color: #888;
```

### 行内代码 `<code>`

```
background-color: #f6f6f6;
border-radius: 3px;
padding: 2px 4px;
font-size: 14px;
font-family: Menlo, Monaco, "Courier New", monospace;
color: #c05b4a;
```

### 引用块 `<blockquote>`

```
border-left: 3px solid #c05b4a;
background-color: #f9f5f0;
padding: 10px 15px;
margin: 1.5em 0;
font-size: 14px;
color: #888;
```

### 代码块 `<pre>`

```
background-color: #f6f6f6;
border-radius: 5px;
padding: 12px;
margin: 1.5em 0;
font-size: 13px;
line-height: 1.6;
white-space: pre-wrap;
font-family: Menlo, Monaco, "Courier New", monospace;
overflow-x: auto;
```

### 列表 `<ul>` / `<ol>`

```
font-size: 15px;
line-height: 1.8;
color: #3f3f3f;
margin-bottom: 1em;
padding-left: 2em;
```

列表项 `<li>`：

```
margin-bottom: 0.5em;
```

### 图片 `<img>`

```
max-width: 100%;
display: block;
margin: 1.5em auto;
border-radius: 4px;
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
```

图片说明 `<p>`（图片下方）：

```
text-align: center;
font-size: 13px;
color: #888;
margin-top: 0.3em;
margin-bottom: 1.5em;
```

### 分割线 `<hr>`

```
border: none;
border-top: 1px solid #eee;
margin: 2em 0;
```

### 表格

```html
<table style="width: 100%; border-collapse: collapse; margin: 1.5em 0; font-size: 14px;">
  <thead>
    <tr style="background-color: #f9f5f0; font-weight: bold; color: #3f3f3f;">
      <th style="border: 1px solid #ddd; padding: 8px 10px;">...</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border: 1px solid #ddd; padding: 8px 10px; color: #3f3f3f;">...</td>
    </tr>
  </tbody>
</table>
```

### 脚注区（文末链接）

```
margin-top: 2em;
padding-top: 1em;
border-top: 1px solid #eee;
font-size: 13px;
color: #888;
```

---

## 商务专业风

沉稳蓝灰配色，适合行业分析、企业动态、专业报告。

### 基础变量

```
主色: #2b2b2b（深黑灰）
辅色: #666（中灰）
强调色: #1a6fa5（深蓝）
背景色: #f8f8f8（浅灰白）
代码背景: #f0f0f0
引用边框色: #1a6fa5
```

样式结构与清新文艺风一致，仅替换颜色变量。

---

## 科技极简风

黑白灰极简，适合技术教程、产品文档、开发日志。

### 基础变量

```
主色: #222（纯深灰）
辅色: #999（中灰）
强调色: #222（与主色一致，靠加粗区分）
背景色: #fff（纯白）
代码背景: #f5f5f5
引用边框色: #222
```

样式结构与清新文艺风一致，仅替换颜色变量。
