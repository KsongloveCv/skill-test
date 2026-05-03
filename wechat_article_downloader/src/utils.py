"""
工具函数：日志、延迟、文件名清理等
"""

import logging
import time
import random
import re
import os
from functools import wraps

def setup_logging(level=logging.INFO):
    """配置日志格式"""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def random_delay(min_sec=1, max_sec=3):
    """随机休眠一段时间"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)

def rate_limit(min_delay, max_delay):
    """
    请求频率限制装饰器
    保证两次调用之间至少间隔 min_delay 秒，至多 max_delay 秒的随机延迟
    """
    def decorator(func):
        last_called = [0]
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_delay:
                delay = random.uniform(min_delay, max_delay)
                time.sleep(delay)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

def safe_filename(filename, max_len=100):
    """去除文件名中的非法字符并截断"""
    # 替换非法字符
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    # 截断
    if len(filename) > max_len:
        name, ext = os.path.splitext(filename)
        filename = name[:max_len-len(ext)] + ext
    return filename.strip()

def ensure_dir(path):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)