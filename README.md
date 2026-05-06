

# Skill

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

这是一个实用的 Python 技能集合项目，托管于 [Gitee](https://gitee.com/yong-top/skill)。

## 项目简介

Skill 是一个专注于内容处理与自动化的 Python 项目集，包含两个核心工具：

### 📄 文章爬取与润色工具 (article-scraper-rewriter)

从 URL 抓取文章内容，进行 AI 智能润色，并提取关键词和标签。

**核心功能：**
- 网页文章自动抓取（支持标题、正文提取）
- AI 驱动的文章内容润色优化
- 自动生成关键词和标签
- 支持 SEO 友好的结构化输出

**技术栈：** Python 3.10 + BeautifulSoup + OpenAI API

### 💬 微信公众号文章下载工具 (wechat_article_downloader)

基于 Python + wxauto4 + pyautogui 的 PC 微信自动化工具。

**核心功能：**
- 搜索并打开指定公众号
- 根据关键词筛选历史文章
- 自动下载文章内容并保存为 HTML 文件
- 支持 OCR 文章图片识别（可选）

**技术栈：** Python 3.8+ + wxauto4 + pyautogui + Tesseract-OCR

## 快速开始

### 环境要求
- Windows 操作系统
- Python 3.8+
- 对于微信下载工具：需安装 PC 微信客户端

### 安装依赖

```bash
# 克隆项目
git clone https://gitee.com/yong-top/skill.git
cd skill

# 安装公共依赖
pip install -r requirements.txt

# 各子项目独立依赖请参见各自目录下的 requirements.txt
```

### 使用示例

**文章爬取与润色：**
```bash
cd article-scraper-rewriter
python src/main.py --url "https://example.com/article" --max-keywords 5 --max-tags 3
```

**微信公众号文章下载：**
```bash
cd wechat_article_downloader
python main.py
```

## 项目结构

```
skill/
├── article-scraper-rewriter/    # 文章爬取与润色工具
│   ├── src/
│   │   ├── scraper.py          # 网页爬取模块
│   │   ├── extractor.py        # 内容提取模块
│   │   ├── rewriter.py         # AI 润色模块
│   │   └── main.py             # 主入口
│   ├── examples/               # 示例输出
│   ├── requirements.txt
│   └── README.md
│
├── wechat_article_downloader/   # 微信公众号下载工具
│   ├── src/
│   │   ├── wechat_controller.py  # 微信控制模块
│   │   ├── article_downloader.py  # 文章下载模块
│   │   ├── article_parser.py      # 文章解析模块
│   │   └── gui_automation.py      # GUI 自动化模块
│   ├── tests/                  # 单元测试
│   ├── requirements.txt
│   └── README.md
│
├── LICENSE                     # Apache 2.0 开源许可
├── README.md                   # 项目主文档
└── README.en.md                # English README
```

## 开源许可

本项目遵循 [Apache License 2.0](LICENSE) 开源协议。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

- 🐛 提交 Bug 报告
- 💡 提出新功能建议
- 🔧 提交代码改进
- 📖 完善文档内容

## 免责声明

微信文章下载工具仅供学习研究使用，请勿用于商业用途或违规采集他人文章内容。