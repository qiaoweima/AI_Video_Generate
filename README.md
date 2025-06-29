# 微博热搜爬虫

这是一个简单的微博热搜爬虫程序，可以定时爬取微博热搜榜前10条内容，并将结果保存为Markdown格式。

## 功能特点

- 自动爬取微博热搜榜前10条内容
- 按日期和时间记录热搜内容
- 支持定时爬取（默认每小时一次）
- 自动去重（同一天内不重复记录相同的热搜）
- 结果保存为Markdown格式，方便查看和分享

## 环境要求

- Python 3.6+
- 依赖库：
  - requests
  - beautifulsoup4
  - schedule

## 安装依赖

```bash
pip install requests beautifulsoup4 schedule
```

## 使用方法

### 直接运行

```bash
python main.py
```

程序会立即爬取一次热搜，然后每小时自动爬取一次。爬取结果会保存在`data`目录下，文件名格式为`YYYY-MM-DD.md`。

### 使用批处理文件运行（Windows）

```bash
test.bat
```

## 数据格式

爬取的数据保存为Markdown格式，示例如下：

```markdown
# 微博热搜 2023-06-29

## 08:00

1. [热搜标题1](https://s.weibo.com/热搜链接1)
2. [热搜标题2](https://s.weibo.com/热搜链接2)
...

## 09:00

1. [热搜标题1](https://s.weibo.com/热搜链接1)
2. [热搜标题3](https://s.weibo.com/热搜链接3)
...
```

## 自定义配置

如需修改爬取频率，可以编辑`main.py`文件中的`schedule_task`方法：

```python
# 修改为每30分钟运行一次
schedule.every(30).minutes.do(self.run_task)

# 或者在特定时间运行
schedule.every().day.at("08:00").do(self.run_task)
```

## 注意事项

- 请合理设置爬取频率，避免对微博服务器造成过大压力
- 程序运行过程中如需停止，请按`Ctrl+C`
- 爬虫可能因为微博页面结构变化而失效，如遇此情况请更新选择器
