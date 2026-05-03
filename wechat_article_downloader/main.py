"""
主程序入口：根据用户输入搜索公众号文章并下载
"""

import time
import logging
from src.utils import setup_logging, random_delay
from src.wechat_controller import WeChatController
from src.article_downloader import ArticleDownloader
from src.gui_automation import click_at, write_text, press_key, hotkey, take_screenshot, locate_text_on_screen
import config

# 配置日志
setup_logging()
logger = logging.getLogger(__name__)

def main():
    print("="*60)
    print("微信公众号文章下载工具")
    print("="*60)

    # 用户输入
    account_name = input("请输入公众号名称：").strip()
    keyword = input("请输入文章关键词（留空则下载全部可见文章）：").strip()
    save_dir = input(f"请输入保存目录（默认：{config.DEFAULT_SAVE_DIR}）：").strip()
    if not save_dir:
        save_dir = config.DEFAULT_SAVE_DIR

    # 初始化控制器
    wx_ctrl = WeChatController()
    downloader = ArticleDownloader(save_dir)

    # 1. 搜索并打开公众号
    logger.info(f"准备搜索公众号：{account_name}")
    if not wx_ctrl.search_and_open_contact(account_name):
        logger.error("无法打开公众号，程序退出")
        return

    # 等待窗口激活
    time.sleep(2)

    # 2. 向上滚动加载更多历史消息（可根据需要调整）
    print("正在加载消息列表...")
    wx_ctrl.scroll_chat(direction='up', times=10)
    time.sleep(2)

    # 3. 获取当前聊天窗口的消息
    messages = wx_ctrl.get_current_chat_messages()
    if not messages:
        logger.warning("未获取到任何消息，可能是聊天窗口未激活或 wxauto 版本问题")
        # 尝试使用 GUI 方式获取（备用方案见下文）
        # 此处略
        return

    # 4. 筛选可能包含文章的条目（公众号消息通常 name 为公众号名称）
    #    这里简单根据关键词匹配内容
    articles = []
    for msg in messages:
        # msg 的结构: {'time': ..., 'name': ..., 'content': ...}
        content = msg.get('content', '')
        if keyword and keyword.lower() not in content.lower():
            continue
        articles.append(msg)

    print(f"符合条件 {len(articles)} 条消息")
    if not articles:
        logger.info("没有找到相关消息")
        return

    # 5. 逐条处理：尝试提取 URL 或通过 GUI 打开并复制
    for idx, msg in enumerate(articles, 1):
        print(f"\n处理第 {idx}/{len(articles)} 条消息")
        content = msg.get('content', '')
        # 尝试提取 URL（公众号短链接）
        import re
        url_match = re.search(r'(https?://mp\.weixin\.qq\.com/s/[^\s]+)', content)
        if url_match:
            url = url_match.group(1)
            logger.info(f"发现文章链接：{url}")
            success, path = downloader.download_from_url(url)
            if success:
                print(f"  ✓ 已下载：{path}")
            else:
                print(f"  × 下载失败，尝试 GUI 方式...")
                success, path = _download_via_gui(msg, downloader)
                if success:
                    print(f"  ✓ 已下载：{path}")
                else:
                    print("  × GUI 方式也失败，跳过")
        else:
            # 没有 URL，只能通过 GUI 方式
            logger.info("未提取到链接，使用 GUI 方式打开文章")
            success, path = _download_via_gui(msg, downloader)
            if success:
                print(f"  ✓ 已下载：{path}")
            else:
                print("  × GUI 方式失败，跳过")

        random_delay(3, 6)

    print("\n处理完成！")

def _download_via_gui(msg, downloader):
    """
    通过 GUI 操作：在聊天窗口中找到消息并点击打开，然后全选复制保存
    此函数需要根据屏幕布局调整坐标，这里给出示例框架
    """
    # 实际使用时，需要先通过 OCR 或给定坐标找到消息位置并点击
    # 以下是一个高度简化的示例，假设我们已知道消息在屏幕上的大致位置
    # 建议实现：截图消息区域 -> OCR 找到标题 -> 双击标题打开文章
    try:
        # 步骤1：点击聊天窗口中的该消息（这里需要坐标或 OCR）
        # 使用 OCR 定位消息内容（速度较慢）
        title_hint = msg.get('content', '')[:30]
        if config.USE_OCR:
            # OCR 搜索整个屏幕或微信窗口区域
            pos = locate_text_on_screen(title_hint)
            if pos:
                click_at(*pos)
                time.sleep(3)  # 等待文章加载
            else:
                return False, None
        else:
            logger.warning("OCR 未启用，无法自动定位消息位置。请手动点击文章后继续...")
            input("请确保已打开目标文章，然后按 Enter 继续...")

        # 步骤2：在文章页面中全选并复制
        # 点击文章内容区域以确保焦点
        click_at(500, 500)  # 假设文章在窗口中央，需根据实际调整
        time.sleep(0.5)
        hotkey('ctrl', 'a')
        time.sleep(0.5)
        hotkey('ctrl', 'c')
        time.sleep(0.5)

        # 步骤3：保存剪贴板内容
        success, path = downloader.save_from_clipboard(title_hint=title_hint)

        # 关闭文章窗口（Alt+F4 或点击关闭按钮）
        hotkey('alt', 'f4')
        time.sleep(1)
        return success, path

    except Exception as e:
        logger.error(f"GUI 下载出错: {e}")
        return False, None

if __name__ == "__main__":
    main()