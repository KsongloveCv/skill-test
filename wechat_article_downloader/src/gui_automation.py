"""
GUI 自动化辅助模块：点击、截图、OCR 定位等
"""

import time
import logging
import pyautogui
import pytesseract
from PIL import Image
from .utils import random_delay, ensure_dir
import config

logger = logging.getLogger(__name__)

# 设置 pytesseract 的路径（若未加入环境变量则需手动指定，例如：
pytesseract.pytesseract.tesseract_cmd = r'D:\\Python\\Tesseract-OCR\\tesseract.exe'

def click_at(x, y):
    """移动到坐标并点击"""
    pyautogui.moveTo(x, y, duration=0.3)
    pyautogui.click()
    random_delay(0.5, 1)

def write_text(text, interval=0.05):
    """模拟键盘输入文本"""
    pyautogui.write(text, interval=interval)

def press_key(key):
    """按下单个按键"""
    pyautogui.press(key)

def hotkey(*keys):
    """组合键"""
    pyautogui.hotkey(*keys)

def take_screenshot(region=None, save_path=None):
    """
    对指定区域截图并可选保存
    :param region: (left, top, width, height)
    :param save_path: 保存路径，若为 None 则不保存，返回 PIL Image 对象
    """
    img = pyautogui.screenshot(region=region)
    if save_path:
        ensure_dir(save_path)
        img.save(save_path)
        logger.info(f"截图已保存至：{save_path}")
    return img

def locate_text_on_screen(text, region=None, lang=config.OCR_LANG):
    """
    使用 OCR 在屏幕/指定区域中查找文字，返回第一个匹配的中心坐标
    如果未找到则返回 None
    """
    try:
        screenshot = pyautogui.screenshot(region=region)
        data = pytesseract.image_to_data(screenshot, lang=lang, output_type=pytesseract.Output.DICT)
        n_boxes = len(data['text'])
        for i in range(n_boxes):
            word = data['text'][i].strip()
            if text in word:
                (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                if region:
                    x += region[0]
                    y += region[1]
                center_x = x + w // 2
                center_y = y + h // 2
                logger.info(f"OCR 找到 '{text}' 于 ({center_x}, {center_y})")
                return (center_x, center_y)
        logger.warning(f"OCR 未找到文字：{text}")
        return None
    except Exception as e:
        logger.error(f"OCR 出错：{e}")
        return None

def click_text(text, region=None):
    """在屏幕上找到文字并点击"""
    pos = locate_text_on_screen(text, region)
    if pos:
        click_at(*pos)
        return True
    return False

# 如果未安装 tesseract，locate_text_on_screen 将不可用，可在此提示