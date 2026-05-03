"""
全局配置文件
"""

# 微信主窗口标题（用于定位窗口，如“微信”）
WECHAT_WINDOW_TITLE = "微信"

# 默认文章保存目录
DEFAULT_SAVE_DIR = "downloads/articles"

# 请求头，模拟浏览器访问
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# 请求间隔范围（秒）
MIN_REQUEST_DELAY = 3
MAX_REQUEST_DELAY = 8

# GUI 操作后的默认等待时间（秒）
GUI_SLEEP = 1.5

# OCR 语言（chi_sim 简体中文 + eng 英文）
OCR_LANG = "chi_sim+eng"

# 是否启用 OCR 识别文章标题（速度较慢）
USE_OCR = True  # 若为 False，则使用预定义的聊天区域坐标点击