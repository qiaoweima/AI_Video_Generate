import os
import time
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import schedule

# 配置
WEIBO_HOT_URL = "https://s.weibo.com/top/summary"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

class WeiboHotSearch:
    def __init__(self):
        self.today_hot_searches = set()  # 用于存储今天已经爬取的热搜
        self.data_dir = "data"
        self.ensure_data_dir()

    def ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def get_hot_search(self):
        """爬取微博热搜"""
        try:
            # 使用移动版微博的请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive'
            }
            
            # 尝试访问移动版微博热搜页面
            url = "https://m.weibo.cn/api/container/getIndex?containerid=106003type%3D25%26t%3D3%26disable_hot%3D1%26filter_type%3Drealtimehot"
            print(f"正在访问移动版API: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'data' in data and 'cards' in data['data'] and len(data['data']['cards']) > 0:
                        card = data['data']['cards'][0]
                        if 'card_group' in card:
                            hot_items = []
                            for item in card['card_group'][:10]:  # 只取前10条
                                if 'desc' in item:
                                    title = item['desc']
                                    # 构造搜索链接
                                    encoded_title = requests.utils.quote(title)
                                    link = f"https://s.weibo.com/weibo?q=%23{encoded_title}%23"
                                    
                                    if title and title not in self.today_hot_searches:  # 去重
                                        hot_items.append({"title": title, "link": link})
                                        self.today_hot_searches.add(title)
                                        print(f"找到热搜: {title}")
                            
                            return hot_items
                        else:
                            print("未找到热搜卡片组")
                    else:
                        print("API响应格式不符合预期")
                except Exception as e:
                    print(f"解析API响应失败: {str(e)}")
            else:
                print(f"请求失败，状态码: {response.status_code}")

            return []
        except Exception as e:
            print(f"爬取失败: {str(e)}")
            return []

    def update_markdown(self, hot_items):
        """更新markdown文件"""
        if not hot_items:
            return

        today = datetime.now().strftime("%Y-%m-%d")
        md_file = os.path.join(self.data_dir, f"{today}.md")

        # 读取现有内容
        existing_content = ""
        if os.path.exists(md_file):
            with open(md_file, "r", encoding="utf-8") as f:
                existing_content = f.read()

        # 添加新内容
        current_time = datetime.now().strftime("%H:%M")
        new_content = f"\n## {current_time}\n\n"
        for item in hot_items:
            new_content += f"1. [{item['title']}]({item['link']})\n"

        # 如果文件不存在，添加标题
        if not existing_content:
            existing_content = f"# 微博热搜 {today}\n"

        # 写入文件
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(existing_content + new_content)

    def run_task(self):
        """运行爬虫任务"""
        print(f"开始爬取微博热搜 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        hot_items = self.get_hot_search()
        if hot_items:
            self.update_markdown(hot_items)
            print(f"成功更新了 {len(hot_items)} 条热搜")
        else:
            print("没有新的热搜")

    def schedule_task(self):
        """设置定时任务"""
        # 每小时运行一次
        schedule.every(1).hours.do(self.run_task)
        # 立即运行一次
        self.run_task()

        # 保持运行
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    hot_search = WeiboHotSearch()
    try:
        # 检查命令行参数
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == "--once":
            # 只运行一次
            hot_search.run_task()
        else:
            # 运行定时任务
            hot_search.schedule_task()
    except KeyboardInterrupt:
        print("\n程序已停止")

if __name__ == "__main__":
    main()
