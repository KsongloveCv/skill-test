"""
微信操作模块：封装 wxauto 相关功能
"""

import time
import logging
from wxauto4 import WeChat
from .utils import random_delay

logger = logging.getLogger(__name__)

class WeChatController:
    def __init__(self):
        self.wx = WeChat()
        logger.info("微信控制器初始化完成")

    def search_and_open_contact(self, name):
        """
        搜索并打开联系人/公众号
        实现方式：使用微信内 Ctrl+F 搜索，然后输入名称，回车
        """
        import pyautogui
        import pygetwindow as gw

        # 激活微信窗口
        try:
            win = gw.getWindowsWithTitle('微信')[0]
            win.activate()
        except IndexError:
            logger.warning("未找到微信窗口，请确保微信已登录且在前台")
            return False

        time.sleep(0.5)

        # 使用快捷键 Ctrl+F 打开搜索
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.8)

        # 清空输入框并输入名称
        pyautogui.hotkey('ctrl', 'a')  # 全选
        pyautogui.press('backspace')
        random_delay(0.2, 0.5)
        pyautogui.write(name, interval=0.1)
        time.sleep(1.5)

        # 按回车确认
        pyautogui.press('enter')
        time.sleep(2)

        # 简单判断是否打开成功（此处可扩展）
        logger.info(f"已搜索并尝试打开：{name}")
        return True

    def get_current_chat_messages(self):
        """
        获取当前聊天窗口的消息列表
        返回: list of dict, 每个 dict 包含 'name', 'content', 'time'
        """
        try:
            msgs = self.wx.GetAllMessage()  # 获取最近 count 条消息
            logger.info(f"成功获取 {len(msgs)} 条消息")
            return msgs
        except Exception as e:
            logger.error(f"获取消息失败: {e}")
            return []

    def scroll_chat(self, direction='up', times=5):
        """
        滚动聊天区域
        direction: 'up' 向上滚动（查看历史） / 'down' 向下滚动
        """
        import pyautogui
        scroll_amount = 3 if direction == 'up' else -3  # 一次滚动3个单位
        for _ in range(times):
            pyautogui.scroll(scroll_amount)
            random_delay(0.2, 0.5)