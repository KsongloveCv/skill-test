"""
测试微信控制器（需要微信已登录）
"""

import unittest
from src.wechat_controller import WeChatController

class TestWeChatController(unittest.TestCase):
    def test_init(self):
        ctrl = WeChatController()
        self.assertIsNotNone(ctrl.wx)

    def test_get_messages(self):
        ctrl = WeChatController()
        # 确保当前聊天窗口有消息
        msgs = ctrl.get_current_chat_messages(5)
        self.assertIsInstance(msgs, list)
        if msgs:
            self.assertIn('content', msgs[0])

if __name__ == '__main__':
    unittest.main()