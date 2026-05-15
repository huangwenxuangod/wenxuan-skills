# Source Router（wenxuan-skills）

Source Router 是一个 **问题到信息源的路由搜索技能**：先判断用户到底要“上下文、项目证据、网页正文、站点爬取，还是某个平台账号的内容列表”，再选择 GitHub、Web Search、Web Access、TikHub、browser-use 等能力。

## 核心能力

- 意图路由：`entity_context` / `repo_lookup` / `url_extract` / `site_crawl` / `username_content` 等。
- Key-aware provider 选择：只调用当前场景需要、且已配置的 provider；缺 key 会记录在 `skipped_providers`。
- Provider mode：`fast` / `balanced` / `deep` / `social` / `technical`。
- Web Access：`scripts/web_access.py` 支持 URL extract 和 site crawl。
- TikHub 社媒链路：XHS、抖音、B站、公众号、视频号、Instagram、Reddit、X、YouTube 的 endpoint 白名单与部分可执行链路。
- Browser-use fallback：当 API/网页抽取失败、需要登录态或 JS 渲染时，按 `references/browser-use-strategy.md` 执行 MCP 浏览器读取。
- 输出沉淀：`--save` 保存 JSON + Markdown 到 `output/`。

## 关键命令

```bash
# 诊断这个问题会用哪些 provider
python "wenxuan-skills/source-router/scripts/search_aggregator.py" --query "social media search agent" --diagnose-providers

# GitHub/技术项目搜索
python "wenxuan-skills/source-router/scripts/search_aggregator.py" --query "social media search agent" --task-type repo_lookup --platform github --json

# 小红书账号 -> 内容列表（需要 TIKHUB_API_KEY）
python "wenxuan-skills/source-router/scripts/search_aggregator.py" --query "基德的秘宝箱 小红书账号 按时间排序前45篇" --task-type username_content --platform xhs --creator "基德的秘宝箱" --limit 45 --sort time_desc --json

# URL 抽取
python "wenxuan-skills/source-router/scripts/search_aggregator.py" --query "帮我读取 https://example.com" --json

# 站点爬取
python "wenxuan-skills/source-router/scripts/search_aggregator.py" --query "爬取 https://example.com 全站" --json
```

## 目录结构

```text
wenxuan-skills/source-router/
  SKILL.md
  README.md
  .env.example
  scripts/
    config.py
    providers.py
    search_aggregator.py
    web_access.py
    README.md
  references/
    tikhub-endpoints.md
    browser-use-strategy.md
  output/
```

## 原则

1. 不把搜索入口冒充成已抓取内容。
2. 封闭平台优先 TikHub/API；失败后再 browser-use 登录态兜底。
3. URL/站点任务走 Web Access，不乱打 Tavily/Exa。
4. 技术问题优先 GitHub/issues/code/Reddit。
5. 社媒账号内容任务优先 username -> profile/id -> content list。
