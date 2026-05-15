---
name: wenxuan-skills-source-router
description: 多源搜索、网页抽取、账号内容入口技能。优先用它做检索、路由和第一步抓取。
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, mcp__web-search__web_search, mcp__skill-handler__Skill, mcp__browser-use__browser_list_profiles, mcp__browser-use__browser_open, mcp__browser-use__browser_eval, mcp__browser-use__browser_click_element, mcp__browser-use__browser_type, mcp__browser-use__browser_scroll, mcp__browser-use__browser_close
---

# Source Router

优先在这些场景使用：

- 普通网页搜索
- GitHub / 技术检索
- 已知 URL 抽取
- 站点 crawl
- 指定账号的内容入口抓取

主入口脚本：

- `scripts/search_aggregator.py`
- `scripts/web_access.py`

统一配置：

- 仓库根目录 `.env`
- 说明见 `../README.md`

常用示例：

```bash
python scripts/search_aggregator.py --query "SEO 是啥" --json
python scripts/search_aggregator.py --query "social media search agent" --task-type repo_lookup --platform github --json
python scripts/search_aggregator.py --query "基德的秘宝箱 小红书账号 按时间排序前45篇" --task-type username_content --platform xhs --creator "基德的秘宝箱" --limit 45 --sort time_desc --save --json
python scripts/web_access.py extract "https://example.com" --json
```

使用约束：

- 先判断任务类型，再选 provider
- 封闭平台抓不到就明确降级
- 结果优先返回结构化 JSON
- 更完整的运行说明只看 `../README.md`
