import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from main import WeiboHotSearch

class TestWeiboHotSearch(unittest.TestCase):
    def setUp(self):
        # 创建测试目录
        self.test_data_dir = "test_data"
        if not os.path.exists(self.test_data_dir):
            os.makedirs(self.test_data_dir)

        # 创建测试实例
        self.hot_search = WeiboHotSearch()
        self.hot_search.data_dir = self.test_data_dir

    def tearDown(self):
        # 清理测试文件
        today = datetime.now().strftime("%Y-%m-%d")
        test_file = os.path.join(self.test_data_dir, f"{today}.md")
        if os.path.exists(test_file):
            os.remove(test_file)

        # 删除测试目录
        if os.path.exists(self.test_data_dir):
            os.rmdir(self.test_data_dir)

    def test_ensure_data_dir(self):
        """测试确保数据目录存在的功能"""
        # 删除目录以测试创建功能
        if os.path.exists(self.test_data_dir):
            os.rmdir(self.test_data_dir)

        self.hot_search.ensure_data_dir()
        self.assertTrue(os.path.exists(self.test_data_dir))

    @patch('requests.get')
    def test_get_hot_search(self, mock_get):
        """测试爬取微博热搜的功能"""
        # 模拟请求响应
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <body>
                <div class="data">
                    <table>
                        <tr>
                            <td class="td-01">1</td>
                            <td class="td-02">
                                <a href="/weibo?q=%23测试热搜1%23">测试热搜1</a>
                            </td>
                        </tr>
                        <tr>
                            <td class="td-01">2</td>
                            <td class="td-02">
                                <a href="/weibo?q=%23测试热搜2%23">测试热搜2</a>
                            </td>
                        </tr>
                    </table>
                </div>
            </body>
        </html>
        """
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response

        # 测试获取热搜
        hot_items = self.hot_search.get_hot_search()

        # 验证结果
        self.assertEqual(len(hot_items), 2)
        self.assertEqual(hot_items[0]['title'], '测试热搜1')
        self.assertEqual(hot_items[0]['link'], 'https://s.weibo.com/weibo?q=%23测试热搜1%23')
        self.assertEqual(hot_items[1]['title'], '测试热搜2')
        self.assertEqual(hot_items[1]['link'], 'https://s.weibo.com/weibo?q=%23测试热搜2%23')

    def test_update_markdown(self):
        """测试更新markdown文件的功能"""
        # 准备测试数据
        hot_items = [
            {"title": "测试热搜1", "link": "https://s.weibo.com/link1"},
            {"title": "测试热搜2", "link": "https://s.weibo.com/link2"}
        ]

        # 更新markdown文件
        self.hot_search.update_markdown(hot_items)

        # 验证文件是否创建
        today = datetime.now().strftime("%Y-%m-%d")
        test_file = os.path.join(self.test_data_dir, f"{today}.md")
        self.assertTrue(os.path.exists(test_file))

        # 验证文件内容
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查标题和内容
        self.assertIn(f"# 微博热搜 {today}", content)
        self.assertIn("测试热搜1", content)
        self.assertIn("测试热搜2", content)
        self.assertIn("https://s.weibo.com/link1", content)
        self.assertIn("https://s.weibo.com/link2", content)

if __name__ == '__main__':
    unittest.main()
