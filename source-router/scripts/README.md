# scripts

本目录放 `source-router` 的**可执行脚本层**。

## 当前脚本

- `config.py`：服务优先级、环境变量、默认参数
- `providers.py`：所有搜索服务 provider 的统一适配层
- `search_aggregator.py`：统一入口，按优先级调用 provider，失败自动回退，输出 route_plan，并生成结构化抓取结果；支持 `--extract-top N` 对搜索结果继续做正文抽取
- `web_access.py`：Web Access 入口，支持 URL extract 和 same-domain crawl，按 Jina Reader -> Firecrawl -> plain HTTP -> browser fallback 顺序尝试

## 当前重点能力

这套脚本现在优先服务一个很明确的目标：

> **用户名 -> 该用户的视频 / 图文 / 文章内容**

也就是说，不再优先追求热点榜单、垃圾搜索接口，而是尽量直接走：
1. 找用户名 / 用户
2. 解析用户主页标识
3. 拉该用户的内容列表
4. 输出结构化 JSON + 核心链接

## .env 自动加载

脚本会自动尝试读取以下位置的 `.env`，且**不会覆盖已经存在的系统环境变量**：

```text
当前工作目录/.env
wenxuan-skills/source-router/.env
wenxuan-skills/source-router/.env.local
```

示例配置见：

```text
wenxuan-skills/source-router/.env.example
```

安全诊断：

```bash
python "wenxuan-skills/source-router/scripts/search_aggregator.py" \
  --query "env check" \
  --env-safety
```

## Provider Profile 与 Budget

`--mode` 可以显式指定，也可以留空自动按 task type 推断：

| task type | 默认 mode |
|---|---|
| `repo_lookup` / `technical_howto` / `tool_selection` | `technical` |
| `username_content` / `creator_capture` / `social_tactic` / `video_search` | `social` |
| `url_extract` | `fast` |
| `site_crawl` / `entity_context` / `trend_signal` / `concept_explainer` / `simple_search` | `balanced` |

| mode | 行为 |
|---|---|
| `fast` | 只取第 1 个可用 provider |
| `balanced` | 取前 3 个可用 provider |
| `deep` | 最多 8 个 provider，并默认 `extract_top=3` |
| `social` | 最多 4 个 provider，优先 TikHub/社媒链路 |
| `technical` | 最多 5 个 provider，优先 GitHub/issues/code/Reddit |

`--budget` 控制成本/深度：

| budget | 行为 |
|---|---|
| `low` | 限制 provider 数量，少抽正文，适合快速低成本 |
| `medium` | 默认 |
| `high` | 增加 provider 数量和 extract_top，适合深度研究 |

示例：

```bash
python "wenxuan-skills/source-router/scripts/search_aggregator.py" \
  --query "social media search agent" \
  --task-type repo_lookup \
  --platform github \
  --budget high \
  --json
```

## Provider 灵活调用策略
planned_providers: 这个场景理论上适合哪些 provider
available_providers: 当前环境可直接调用的 provider
skipped_providers: 因缺少 API key 被跳过的 provider
```

例如：

```bash
python "wenxuan-skills/source-router/scripts/search_aggregator.py" \
  --query "AI social search agent" \
  --diagnose-providers
```

如果你希望强制尝试所有 planned provider，包括没配 key 的，也可以用：

```bash
python "wenxuan-skills/source-router/scripts/search_aggregator.py" \
  --query "AI social search agent" \
  --all-providers \
  --json
```

设计原则：
- 技术/开源问题优先 GitHub / issues / code / Reddit。
- 实体上下文优先已配置的 Web Search / semantic search。
- XHS/抖音/B站/公众号/视频号/Instagram 账号内容优先 TikHub；没配 `TIKHUB_API_KEY` 时不伪装抓取成功。
- URL 读取/爬站直接走 `web_access`，不需要 Tavily/Exa 等搜索 key。
- 没配 key 的 provider 默认跳过并记录在 `route_plan.skipped_providers` 与 `capture_meta.skipped_providers`。

## Web Access 能力

`web_access.py` 已打通第一版可执行链路：

```text
extract URL:
  Jina Reader
  -> Firecrawl scrape
  -> plain HTTP readability-lite
  -> browser-use / Playwright planned fallback

crawl site:
  Firecrawl crawl
  -> Firecrawl map + extract
  -> plain same-domain crawl
  -> browser-use / Playwright planned fallback
```

### URL 抽取

```bash
python "wenxuan-skills/source-router/scripts/web_access.py" extract "https://example.com" --json
```

指定 provider 顺序：

```bash
python "wenxuan-skills/source-router/scripts/web_access.py" extract "https://example.com" --providers jina,firecrawl,plain_http,browser --save --json
```

### 站点 Crawl

```bash
python "wenxuan-skills/source-router/scripts/web_access.py" crawl "https://example.com" --depth 1 --limit 20 --save --json

# 跳过 Firecrawl，使用本地 plain HTTP 同域 crawl
python "wenxuan-skills/source-router/scripts/web_access.py" crawl "https://example.com" --depth 1 --limit 20 --no-firecrawl --json
```

### 搜索后抽取 Top N

```bash
python "wenxuan-skills/source-router/scripts/search_aggregator.py" --query "TikHub XHS user notes endpoint" --extract-top 3 --json
```

注意：browser fallback 当前会返回可执行步骤提示：`browser_list_profiles -> browser_open -> browser_eval -> browser_close`。真正的自动登录态浏览器执行仍需后续接 browser-use / Playwright MCP profile。


- `github`（GitHub repository search，支持无 token 匿名 fallback）
- `github_issues`
- `github_code`
- `github_discussions`（当前为 URL fallback / stub）
- `youtube`（phase 1 adapter；后续优先接 YouTube Data API / yt-dlp / transcript）
- `reddit`（phase 1 adapter）
- `x`（phase 1 adapter）
- `bilibili`（phase 1 adapter；TikHub/B站链路已开始接入）
- `tavily`
- `exa`
- `brave`
- `metaso`
- `serpapi`
- `serper`
- `bing`
- `google_cse`
- `firecrawl`
- `tikhub`

### TikHub / 平台 creator capture 方向（当前最值得关注）
已开始按 `username -> content` 方向接入：
- `xhs`：已升级为优先 `search_users -> user_info -> user_notes`；无法解析 user_id 时才 fallback 到 `search_notes`，并明确标记不够精确。
- `douyin`：按白名单链路 `handler_user_profile_v2/用户搜索 -> fetch_user_post_videos` 推进。
- `bilibili`：按白名单链路 `user id/profile -> fetch_user_post_videos` 推进。
- `wechat_mp`：`fetch_search_official_account -> fetch_mp_article_list`。
- `wechat_channels`：`fetch_user_search_v2 -> fetch_home_page`。
- `youtube`：优先建议 YouTube Data API / yt-dlp / transcript 链路。
- `instagram`：保留 TikHub/API/browser planned actions，未确认 endpoint 前不返回伪内容。

> 注意：TikHub 文档存在“标题像目标接口，点进去却是别的平台/别的产品”的情况，所以当前实现坚持**endpoint 白名单思路**，只接已经确认过的平台路径。

## 路由层能力
`search_aggregator.py` 已支持：
- 问题类型推断（如 `concept_explainer` / `entity_context` / `simple_search` / `repo_lookup` / `creator_capture` / `username_content`）
- 平台 hint 推断（GitHub / YouTube / B站 / X / Reddit / XHS / 抖音 / 微信 / Instagram）
- route_plan 输出：说明意图判断、路由原因、required_capabilities、provider 顺序、准确性约束
- “前 N 篇/最近 N 条/--limit”数量解析，`username_content` 默认抓 10 条
- “按时间排序/最新/热门/点赞”排序解析，支持 `--sort time_desc|popularity_desc|relevance`
- provider priority plan 构建
- 统一 schema：`creator` / `results[]` / `capture_meta` / `related_links`
- `--save` 落盘 JSON + Markdown 到 `output/`

## 已实现
- GitHub repositories
- GitHub issues
- GitHub code
- GitHub 无 token 搜索 URL fallback
- YouTube 搜索入口适配
- Reddit 搜索入口适配
- X / Twitter 搜索入口适配
- B站搜索入口适配
- Tavily
- Exa
- Brave
- SerpAPI
- Serper
- Bing
- Google CSE
- TikHub username -> content 第一版骨架

## Stub / 待确认接口
- GitHub discussions（需 GraphQL / repo-scoped 方案）
- Metaso（目前返回官方入口和 next step）
- Firecrawl（目前返回官方入口和 next step）
- TikHub WeChat username/content（接口方向已确认，但还未完成稳定映射）

## 关于 GitHub token

`GITHUB_TOKEN` 不是为了“有 token 才能开始”，而是为了：
- 提高 rate limit
- 提高稳定性
- 支持 repo / issues / code 等更频繁、更深入的搜索

当前已实现降级：
- 没有 token 时，GitHub provider 会返回 GitHub web search URL 作为匿名 fallback
- 聚合器仍可继续组合 Tavily / Exa / Brave 等结果

## 统一输出格式

所有 provider 最终都映射成 AI 可直接消费的结构：

```json
{
  "query": "阑夕",
  "route_plan": {
    "task_type": "username_content",
    "action": "creator_posts",
    "platform": "xhs",
    "creator": "阑夕",
    "requested_limit": 10,
    "sort_order": "relevance",
    "providers": ["tikhub", "tavily"],
    "required_capabilities": ["tikhub_social_api", "social_creator_posts", "pagination", "normalization"],
    "reason": "用户询问的是指定平台/账号的内容列表，优先走平台专用 creator->content 链路，而不是普通网页搜索。"
  },
  "task_type": "username_content",
  "platform_hint": "xhs",
  "creator_hint": "阑夕",
  "success": true,
  "creator": {
    "platform": "xhs",
    "display_name": "阑夕",
    "handle": "阑夕",
    "bio": "",
    "profile_url": "",
    "followers": null,
    "verified": null,
    "aliases": [],
    "discovered_from": []
  },
  "results": [
    {
      "platform": "xhs",
      "type": "content",
      "title": "...",
      "body": "...",
      "transcript": "",
      "comments": [],
      "stats": {},
      "published_at": null,
      "source_url": "...",
      "media_urls": [],
      "tags": [],
      "provider": "tikhub",
      "source_type": "xhs_content",
      "score": 12.3,
      "metadata": {},
      "author": {}
    }
  ],
  "related_links": ["..."],
  "capture_meta": {
    "attempted_providers": ["tikhub"],
    "failed_providers": [],
    "captured_count": 3,
    "captured_at": "2026-05-13T12:00:00+00:00",
    "completeness": "partial"
  },
  "error": null
}
```

## 环境变量

每个服务都通过环境变量读取 key：

- `GITHUB_TOKEN`（可选增强）
- `TAVILY_API_KEY`
- `EXA_API_KEY`
- `BRAVE_SEARCH_API_KEY`
- `METASO_API_KEY`（当前可选）
- `SERPAPI_API_KEY`
- `SERPER_API_KEY`
- `BING_SEARCH_API_KEY`
- `GOOGLE_CSE_API_KEY`
- `GOOGLE_CSE_ENGINE_ID`
- `FIRECRAWL_API_KEY`（当前可选）
- `TIKHUB_API_KEY`（当前必须配置，才能走 TikHub 用户名 -> 内容抓取）

示例见：
- `../.env.example`

## 运行示例

概念检索：

```bash
python "wenxuan-skills/source-router/scripts/search_aggregator.py" --query "SEO 是啥" --json
```

GitHub 项目检索：

```bash
python "wenxuan-skills/source-router/scripts/search_aggregator.py" --query "social media search agent" --task-type repo_lookup --platform github --json
```

用户名 -> 内容（小红书 / 抖音 / B站 / 微信方向）：

```bash
python "wenxuan-skills/source-router/scripts/search_aggregator.py" --query "阑夕" --task-type username_content --platform xhs --creator "阑夕" --save --json
```

指定数量和排序，例如“小红书账号基德的秘宝箱，按时间排序前45篇”：

```bash
python "wenxuan-skills/source-router/scripts/search_aggregator.py" --query "基德的秘宝箱 小红书账号 按时间排序前45篇" --task-type username_content --platform xhs --creator "基德的秘宝箱" --limit 45 --sort time_desc --save --json
```

实体上下文检索，例如“数字生命卡兹克是谁”：

```bash
python "wenxuan-skills/source-router/scripts/search_aggregator.py" --query "数字生命卡兹克是谁" --task-type entity_context --json
```

指定 provider 顺序：

```bash
python "wenxuan-skills/source-router/scripts/search_aggregator.py" --query "Claude Code skills" --providers github,github_issues,tavily,exa,brave --json
```
