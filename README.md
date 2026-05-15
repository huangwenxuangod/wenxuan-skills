# wenxuan-skills

`wenxuan-skills` 是一套从“检索”到“知识库”到“内容”再到“图片”的本地 skills。

当前主链路已经压成 4 个业务型 skills，统一放在 `skills/` 目录下：

1. `wenxuan-skills-search`
   搜索、路由、网页抽取、账号内容采集。
2. `wenxuan-skills-knowledge-base`
   把搜索结果沉淀成项目级知识库。
3. `wenxuan-skills-content-studio`
   基于知识库做小红书选题和内容输出。
4. `wenxuan-skills-image-studio`
   基于知识库和内容稿直接生图，并保留 prompt 资产。

## 配置

推荐把配置统一写在工作区或仓库根目录的 `.env`：

```powershell
cd D:\dev\my-project\wenxuan-skills
Copy-Item .env.example .env
```

现在所有公开 skill 都会自动按下面顺序补环境变量（仅填充缺失值，不覆盖已存在的进程环境变量）：

1. 仓库根目录 `.env`
2. 仓库根目录 `.env.local`
3. 当前工作目录 `.env`
4. 当前工作目录 `.env.local`
5. 当前 skill 目录下的 `.env`
6. 当前 skill 目录下的 `.env.local`

所以你有两种推荐方式：

- 想全局复用：维护仓库根目录 `.env`
- 想按项目隔离：在你运行 skill 的工作区放一份 `.env`

## 输出目录

所有 skill 默认统一输出到当前执行工作区下：

```text
当前工作目录/wenxuan-output/
```

也就是你在哪个工作区执行，结果就落在哪个工作区下的 `wenxuan-output/`，并按阶段分目录：

```text
wenxuan-output/
  search/
  knowledge-base/
  content-studio/
  image-studio/
```

例如你在：

```text
D:\work\client-a
```

里调用 skill，那么默认输出会在：

```text
D:\work\client-a\wenxuan-output
```

## 常用环境变量

- `GITHUB_TOKEN`：增强 GitHub 搜索稳定性
- `TAVILY_API_KEY` / `EXA_API_KEY` / `BRAVE_SEARCH_API_KEY`：网页搜索
- `TIKHUB_API_KEY`：小红书、抖音、B 站、公众号等账号内容链路
- `FIRECRAWL_API_KEY`：网页抓取增强
- `OPENAI_API_KEY`：图片生成
- `OPENAI_BASE_URL`：图像接口地址
- `OPENAI_IMAGE_MODEL`：图像模型名

## 快速使用

## 推荐链路

如果你只想看最终图文结果，推荐直接走：

1. `wenxuan-skills-search`
2. `wenxuan-skills-knowledge-base`
3. `wenxuan-skills-content-studio`
4. `wenxuan-skills-image-studio`

或者直接使用 `wenxuan-skills-image-studio` 里的全流程脚本，一条命令从输入走到输出。

### 最短路径：直接出结果

如果你已经有知识库：

```powershell
python skills\wenxuan-skills-image-studio\scripts\run_full_pipeline.py --knowledge-base D:\work\client-a\wenxuan-output\knowledge-base\knowledge-base.json --json
```

如果你已经有搜索结果：

```powershell
python skills\wenxuan-skills-image-studio\scripts\run_full_pipeline.py --search-result D:\work\client-a\wenxuan-output\search\search-result.json --json
```

如果你想从一个 query 直接开始：

```powershell
python skills\wenxuan-skills-image-studio\scripts\run_full_pipeline.py --query "AI 效率工具 小红书图文方向" --json
```

### 1. `wenxuan-skills-search`

```powershell
cd D:\dev\my-project\wenxuan-skills\skills\wenxuan-skills-search\scripts
python search.py --query "AI 效率工具 小红书图文方向" --save --json
```

网页读取：

```powershell
python web_access.py extract "https://example.com" --save --json
```

### 2. `wenxuan-skills-knowledge-base`

把搜索或采集结果沉淀为知识库：

```powershell
cd D:\dev\my-project\wenxuan-skills\skills\wenxuan-skills-knowledge-base\scripts
python build_knowledge_base.py D:\work\client-a\wenxuan-output\search\search-result.json --json
```

### 3. `wenxuan-skills-content-studio`

基于知识库生成小红书选题和内容：

```powershell
cd D:\dev\my-project\wenxuan-skills\skills\wenxuan-skills-content-studio\scripts
python generate_content.py D:\work\client-a\wenxuan-output\knowledge-base\knowledge-base.json --json
```

### 4. `wenxuan-skills-image-studio`

```powershell
cd D:\dev\my-project\wenxuan-skills
python skills\wenxuan-skills-image-studio\scripts\render_images.py D:\work\client-a\wenxuan-output\knowledge-base\knowledge-base.json D:\work\client-a\wenxuan-output\content-studio\content-bundle.json --json
```

直接跑全流程：

```powershell
python skills\wenxuan-skills-image-studio\scripts\run_full_pipeline.py --search-result D:\work\client-a\wenxuan-output\search\search-result.json --json
```

## 最终结果看哪里

你最终只需要看这几个文件：

- 内容文稿：`./wenxuan-output/content-studio/final-post.md`
- 分页内容：`./wenxuan-output/content-studio/content-bundle.json`
- 图片提示词：`./wenxuan-output/image-studio/image-prompts.json`
- 图文汇总：`./wenxuan-output/image-studio/result-summary.md`
- 实际图片：`./wenxuan-output/image-studio/generated-images/`

## 当前状态

- `wenxuan-skills-search`：输入一个 query、URL 或账号，输出原始资料
- `wenxuan-skills-knowledge-base`：把原始资料整理成项目知识库
- `wenxuan-skills-content-studio`：输出小红书选题、分页结构和最终文稿
- `wenxuan-skills-image-studio`：直接输出最终图片，同时保留图片 prompt

## skills CLI

现在仓库已经是标准多-skill 结构，推荐直接从 GitHub 安装：

```powershell
npx skills add huangwenxuangod/wenxuan-skills --list
npx skills add huangwenxuangod/wenxuan-skills -a codex --skill wenxuan-skills-search -g -y
```

安装全部 skill：

```powershell
npx skills add huangwenxuangod/wenxuan-skills -a codex --skill '*' -g -y
```

也可以先在本地测试发现：

```powershell
npx skills add . --list
```

## 目录约定

- 主入口文档：`README.md`
- 统一环境文件：`.env`
- 统一输出目录：`./wenxuan-output/`
