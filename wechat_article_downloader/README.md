# 微信公众号文章下载工具

基于 Python + wxauto + pyautogui 的 PC 微信自动化工具，支持：
- 搜索并打开指定公众号
- 根据关键词筛选历史文章
- 自动下载文章内容并保存为 HTML 文件

## 环境要求
- Windows 操作系统
- Python 3.8+
- 微信客户端（建议 3.9.11.17 版本）
- 安装 Tesseract-OCR（如果需要 OCR 功能）

## 安装步骤
1. 克隆或下载本项目
2. 安装依赖：`pip install -r requirements.txt`
3. 安装 [Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki) 并配置环境变量
4. 登录 PC 微信，并确保微信窗口可见

## 使用方法
运行 `main.py`，根据提示输入公众号名称、关键词和保存目录，程序将自动操作微信下载文章。

**注意**：
- OCR 功能默认关闭（速度较慢），可在 `config.py` 中启用
- 若 GUI 操作坐标不准确，请根据自己屏幕分辨率调整 `main.py` 中的点击坐标
- 建议在测试前先用小号或非重要账号操作，避免误触

## 项目结构
参见目录树

## 免责声明
本工具仅供学习研究使用，请勿用于商业用途或违规采集他人文章。