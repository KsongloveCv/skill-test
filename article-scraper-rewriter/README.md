# Article Scraper & Rewriter Skill

从 URL 抓取文章内容，进行 AI 润色，并提取关键词和标签。

## 快速开始

### Python 环境
Python 3.10

### 1. 创建虚拟环境
```bash
python -m venv venv
```
### 2. 激活虚拟环境
```bash
venv\Scripts\activate
```
### 3. 安装依赖
```bash
pip install -r requirements.txt
```

```bash
清华大学：https://pypi.tuna.tsinghua.edu.cn/simple
阿里云：http://mirrors.aliyun.com/pypi/simple/
中国科技大学：https://pypi.mirrors.ustc.edu.cn/simple
华中理工大学：http://pypi.hustunique.com/
山东理工大学：http://pypi.sdutlinux.org/
豆瓣：http://pypi.douban.com/simple/
```

### 4. 运行命令
```bash
python src/main.py --url "https://www.cnblogs.com/zlt2000/p/19577443" --max-keywords 5 --max-tags 3
```
