"""
测试文章解析器
"""

import unittest
from src.article_parser import parse_html

SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head><title>测试文章</title></head>
<body>
<h1 class="rich_media_title">人工智能的未来</h1>
<div id="js_content">这是正文内容</div>
<span id="js_name">作者A</span>
<em id="publish_time">2025-01-01</em>
</body>
</html>
"""

class TestArticleParser(unittest.TestCase):
    def test_parse_html(self):
        article = parse_html(SAMPLE_HTML)
        self.assertEqual(article['title'], '人工智能的未来')
        self.assertEqual(article['author'], '作者A')
        self.assertIn('正文内容', article['content'])

if __name__ == '__main__':
    unittest.main()