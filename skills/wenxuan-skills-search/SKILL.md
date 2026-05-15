---
name: wenxuan-skills-search
description: 统一搜索与采集入口。负责网页搜索、URL 抽取、站点 crawl、账号内容抓取，并把原始结果落到当前工作区的 `wenxuan-output/search/`。
---

# wenxuan-skills Search

适用场景：

- 搜索某个主题、概念、项目
- 抓取网页正文
- 爬取站点
- 抓取指定平台账号的公开内容

主入口：

- `scripts/search.py`
- `scripts/web_access.py`

输出目录：

- `./wenxuan-output/search/`
