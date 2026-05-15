# wenxuan-skills

`wenxuan-skills` 是一组围绕账号对标流程整理的本地 skills。

当前保留并整理后的主线只有 4 个，统一放在 `skills/` 目录下：

1. `source-router`
   搜索、路由、网页抽取、账号内容入口。
2. `creator-capture`
   把已有导出结果规范化成统一 `CaptureBundle`。
3. `account-brain`
   从 `CaptureBundle` 推导学习资产。
4. `codex-image-studio`
   调用图像接口生成图片。

## 配置

统一在仓库根目录放 `.env`：

```powershell
cd D:\dev\my-project\wenxuan-skills
Copy-Item .env.example .env
```

脚本会优先读取：

1. 仓库根目录 `.env`
2. 仓库根目录 `.env.local`
3. 当前工作目录 `.env`
4. 个别 skill 目录下的 `.env` 或 `.env.local`

推荐只维护根目录这一份。

## 常用环境变量

- `GITHUB_TOKEN`：增强 GitHub 搜索稳定性
- `TAVILY_API_KEY` / `EXA_API_KEY` / `BRAVE_SEARCH_API_KEY`：网页搜索
- `TIKHUB_API_KEY`：小红书、抖音、B 站、公众号等账号内容链路
- `FIRECRAWL_API_KEY`：网页抓取增强
- `OPENAI_API_KEY`：图片生成
- `OPENAI_BASE_URL`：图像接口地址
- `OPENAI_IMAGE_MODEL`：图像模型名

## 快速使用

### 1. `source-router`

```powershell
cd D:\dev\my-project\wenxuan-skills\skills\source-router\scripts
python search_aggregator.py --query "SEO 是啥" --json
python search_aggregator.py --query "social media search agent" --task-type repo_lookup --platform github --json
python search_aggregator.py --query "基德的秘宝箱 小红书账号 按时间排序前45篇" --task-type username_content --platform xhs --creator "基德的秘宝箱" --limit 45 --sort time_desc --save --json
```

网页读取：

```powershell
python web_access.py extract "https://example.com" --json
python web_access.py crawl "https://example.com" --depth 1 --limit 20 --json
```

### 2. `creator-capture`

把已有原始导出 JSON 规范化：

```powershell
cd D:\dev\my-project\wenxuan-skills\skills\creator-capture\scripts
python normalize_input.py input.json --pretty
```

### 3. `account-brain`

基于规范化后的 `CaptureBundle` 生成学习资产：

```powershell
cd D:\dev\my-project\wenxuan-skills\skills\account-brain\scripts
python derive_learning_assets.py capture-bundle.json --pretty
```

### 4. `codex-image-studio`

```powershell
cd D:\dev\my-project\wenxuan-skills
python skills\codex-image-studio\scripts\generate_image_via_local_api.py --prompt "极简中文知识海报，米白底，深棕标题，卡片布局" --out output\sample.png
```

## 当前状态

- `source-router`：最完整，可直接跑
- `creator-capture`：可跑，但当前偏“规范化已有导出”
- `account-brain`：可跑，依赖 `creator-capture` 输出
- `codex-image-studio`：可跑，依赖图片 API

## skills CLI

现在仓库已经是标准多-skill 结构，可以先本地测试发现：

```powershell
npx skills add . --list
```

发布到 GitHub 后，可直接按仓库安装：

```powershell
npx skills add yourname/wenxuan-skills --list
npx skills add yourname/wenxuan-skills -a codex --skill source-router -g -y
```

## 目录约定

- 主入口文档：`README.md`
- 统一环境文件：`.env`
- 运行结果：`skills/source-router/output/`
