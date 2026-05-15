# wenxuan-skills 总设计文档

## 一、项目定位

`wenxuan-skills` 不是普通的搜索工具集。

它的目标是构建一个：

> **专业的对标技能系统**

用于跑通下面这条完整链路：

1. 搜索并定位对标自媒体账号
2. 抓取该账号的公开内容与结构信号
3. 将账号行为模式编码成 AI 可学习的模型
4. 让 AI 直接生成相似表达风格的图文内容

当前明确聚焦赛道：

- **图文赛道**
- **文案由 AI 生成**
- **图片由 AI 生成**
- **主要平台优先围绕中文平台与图文内容生态**

---

## 二、核心设计原则

### 1. 不是“给人看的分析工具”，而是“给 AI 学的行为系统”

很多对标分析最后停在报告层。

`wenxuan-skills` 要避免这一点。

最终产出不能只是：
- 这个账号做得很好
- 它的标题很吸引人
- 它的视觉很统一

而必须变成：
- 可结构化
- 可程序消费
- 可被 AI 复用
- 可驱动生成

也就是：

> **行为模式 > 解读报告**

---

### 2. 不是“多搜几个结果”，而是“命中最像答案的源”

搜索只是入口，不是结果。

真正重要的是：

- 问题该去哪里找
- 账号该怎么抓
- 哪些是公开原始证据
- 哪些是站外替代信号
- 哪些地方必须诚实降级

也就是：

> **source routing > search provider count**

---

### 3. 默认面向“账号镜像构建”

这个系统最核心的任务不是一条内容分析，而是：

> **把一个账号尽可能变成机器可以理解和复用的镜像**

包括：
- 名字
- 简介
- 标题公式
- 内容结构
- 图片视觉
- 发布时间
- 引流方式
- 变现线索

并且必须双通道读取：

1. 内容知识线
   - 抽知识、背景、概念、案例、主题关系
   - 组织成 JSON 知识库，用于选题挖掘

2. 视觉风格线
   - 抽版式、配色、留白、字体感、装饰语法
   - 反推成 prompt 规则，用于模仿和超越

这两条线不能混成同一份笼统分析。

---

### 4. 先做“学习引擎”，再做“生成引擎”

如果没有前面的账号理解与行为编码，直接做生图/写文案，只会变成粗糙模仿。

所以必须优先建设：

1. 搜索与路由
2. 抓取与结构化
3. 行为编码
4. 内容生成

---

### 5. 支持并行任务接口

很多场景不是单线程完成的，而是要同时开几条线。

系统必须支持：

1. **扇出**
   - 一次把任务拆成多个子任务
   - 例如：抓取、内容抽取、视觉抽取、生成预备同时启动

2. **并行执行**
   - 多个子任务可以同时跑
   - 只要输入不冲突，就不要排队等

3. **扇入**
   - 子任务完成后再回收为一个统一结果
   - 例如：`CaptureBundle` -> `LearningAssetsBundle` -> `GeneratedPostBundle`

并行最适合的地方：

- 多平台搜索
- 一个账号的多页内容抓取
- `content_kb` 与 `visual_prompt_kernel` 生成
- 多张图的并行生图

总原则：

> 先拆任务，再并行跑，最后统一收口

---

## 三、系统总架构

`wenxuan-skills` 最终采用：

> **一个总控 skill + 四个子 skill**

的结构。

### 总控 skill

#### 1. `benchmark-orchestrator`

这是整个系统的总控 skill。

它不负责深度执行单点任务，而负责：

- 接收用户的对标请求
- 判断当前任务处于哪个阶段
- 调度子 skill
- 控制输出标准
- 决定何时继续抓取、何时进入行为编码、何时进入生成

它是：

> **总控台 / orchestrator / 工作流管理器**

---

### 子 skill

#### 2. `source-router`

作用：
- 最强搜索入口
- 问题到信息源路由
- 多 provider 聚合与 fallback

职责：
- 判断去 GitHub / Reddit / 官方文档 / 视频平台 / 封闭平台 / 本地知识库哪里找
- 为 creator 请求建立 route plan
- 提供 provider plan、fallback、环境能力诊断

现状：
- 已有第一版，当前是 `wenxuan-skills` 唯一已落地 skill

---

#### 3. `creator-capture`

作用：
- 账号抓取器
- 公开内容资产化入口

职责：
- 输入账号名 / handle / 链接 / 平台
- 抓账号主页、内容列表、标题、正文、视觉资源、评论线索、引流动作、商业化痕迹
- 输出统一结构化资产

这个 skill 是整个系统最重要的基础层。

因为：

> 没有抓取资产，就没有后面的学习和生成。

---

#### 4. `account-brain`

作用：
- 行为模式编码器
- 账号 AI 学习层

职责：
- 将 `creator-capture` 的原始资产，转成 AI 可学习的行为模型
- 不是输出面向人的长报告
- 而是输出机器友好的 JSON / structured markdown

这个 skill 的定位非常关键：

> 不是告诉“我”怎么做，而是告诉“AI”这个账号是怎么运作的。

---

#### 5. `codex-image-studio`

作用：
- 图文生产器
- 文案生成 + 生图执行层

职责：
- 读取 `account-brain` 输出的行为模型
- 根据选题生成：
  - 标题
  - 正文
  - 图像 prompt
  - 多页图文结构
  - 单张图文海报
- 最终产出平台可发布的图文内容

它当前只服务一个赛道：

> **图文赛道**

---

## 四、总控与子 skill 的关系

总控 skill 负责“阶段判断”和“任务编排”。

### 关系图

```text
benchmark-orchestrator
  ├─ source-router
  ├─ creator-capture
  ├─ account-brain
  └─ codex-image-studio
```

### 调度逻辑

#### 场景 A：只想搜一个账号是谁

总控 skill 调：
- `source-router`

如果只是背景了解，不进入抓取。

#### 场景 B：我要彻底对标一个账号

总控 skill 顺序调：
- `source-router`
- `creator-capture`
- `account-brain`

如果用户还要生成内容，再继续：
- `codex-image-studio`

#### 场景 C：我已经有行为模型，要直接出图文

总控 skill 直接调：
- `codex-image-studio`

#### 场景 D：我需要并行跑多个子任务

总控 skill 先拆成任务树，再并行调度：

- 抓取线程
- 知识抽取线程
- 视觉抽取线程
- 生图线程

最后统一收口到一个结果包。

---

## 五、系统运行流程

### Phase 1：账号定位

入口：
- `benchmark-orchestrator`
- 调用 `source-router`

目标：
- 搜到目标账号本体
- 确认平台
- 确认公开入口
- 判断可抓取程度

输出：
- `route_plan.json`
- `account_locator.json`

---

### Phase 2：账号抓取

入口：
- `creator-capture`

目标：
- 尽可能抓取账号全量公开资产

输出：
- `account_profile.json`
- `post_index.json`
- `post_details.json`
- `comment_signals.json`
- `traffic_hooks.json`
- `monetization_clues.json`
- `visual_assets_index.json`

---

### Phase 3：行为编码

入口：
- `account-brain`

目标：
- 将账号原始资产编码成 AI 可学习的模型

输出：
- `behavior_dna.json`
- `positioning_model.json`
- `title_model.json`
- `copy_model.json`
- `visual_style_model.json`
- `posting_strategy_model.json`
- `conversion_model.json`
- `monetization_model.json`

---

### Phase 4：图文生成

入口：
- `codex-image-studio`

目标：
- 根据行为模型生成图文内容

输出：
- `generated_titles.json`
- `generated_copy.json`
- `image_prompts.json`
- `post_layout_plan.json`
- `final_posts/`

---

## 六、四个子 skill 的详细设计

## 6.1 `source-router`

### 目标

作为系统最强搜索能力，负责：

- 路由正确
- provider 合理
- fallback 透明
- 输出可信

### 核心能力

1. 问题分类
2. 信息源优先级判断
3. provider 聚合与回退
4. creator 请求特殊处理
5. URL extract / crawl / browser fallback

### 输入

- `query`
- `task_type`
- `platform`
- `creator`
- `limit`
- `sort`

### 输出

- `route_plan`
- `provider_plan`
- `related_links`
- `search_results`
- `capture_feasibility`

### 当前现状

- 已具备第一版能力
- 是现阶段最成熟的模块

---

## 6.2 `creator-capture`

### 目标

把账号抓成“结构化内容资产”。

### 核心能力

1. 账号主页抓取
2. 内容列表抓取
3. 标题/时间/正文抽取
4. 评论线索抽取
5. 引流动作识别
6. 商业化线索记录
7. 视觉资源索引

### 重点支持字段

#### 账号层
- platform
- display_name
- handle
- bio
- avatar_style
- profile_url
- external_links
- private_domain_links
- contact_methods

#### 内容层
- title
- subtitle
- cover_text
- first_sentence
- body
- hashtags
- publish_time
- content_type
- metrics

#### 行为线索层
- cta_signals
- traffic_signals
- monetization_signals
- comment_patterns

#### 视觉层
- color_palette_guess
- layout_guess
- typography_guess
- decorative_elements
- image_subject_type
- visual_reference_urls

### 输出

- `account_profile.json`
- `posts.json`
- `visual_assets.json`
- `engagement_signals.json`
- `commercial_signals.json`

### 当前建设优先级

这个 skill 是第一优先开发目标。

---

## 6.3 `account-brain`

### 目标

将账号内容学习成 AI 行为模型。

### 核心能力

1. 账号定位编码
2. 标题模式编码
3. 正文结构编码
4. 视觉语言编码
5. 发布时间与频率编码
6. 引流动作编码
7. 变现机制编码

### 关键输出

#### `behavior_dna.json`

整体账号的浓缩行为指纹。

#### `title_model.json`

示例字段：

```json
{
  "primary_patterns": [],
  "opening_components": [],
  "promise_style": "",
  "emotion_level": "",
  "instruction_density": "",
  "common_lengths": []
}
```

#### `copy_model.json`

描述正文结构：
- 开头句法
- 段落组织
- 清单密度
- 教学感 / 故事感 / 观点感

#### `visual_style_model.json`

描述图片风格：
- 配色
- 材质
- 边框
- 装饰符号
- 排版布局
- 主体元素
- 信息密度

#### `conversion_model.json`

描述：
- 引流到哪里
- 如何引导关注 / 收藏 / 评论 / 私信

### 核心原则

这个 skill 不写“好不好”。

它只负责：

> **这个账号是如何运作的**

---

## 6.4 `codex-image-studio`

### 目标

将行为模型转为图文内容生产。

### 核心能力

1. 根据 `behavior_dna` 生成选题
2. 根据 `title_model` 生成标题
3. 根据 `copy_model` 生成正文
4. 根据 `visual_style_model` 生成图片 prompt
5. 生成图文结构与页面顺序
6. 输出平台可直接使用的图文资产

### 输入

- `behavior_dna.json`
- 用户选题 / 方向
- 页数
- 平台
- 风格约束

### 输出

- `titles.json`
- `copy.json`
- `image_prompts.json`
- `visual_reference_plan.json`
- `final_posts/`

### 当前约束

当前明确只服务：
- 图文赛道
- AI 文案
- AI 生图

---

## 七、目录结构设计

建议最终目录结构如下：

```text
wenxuan-skills/
  MASTER-PLAN.md
  benchmark-orchestrator/
    SKILL.md
    references/
    examples/
  source-router/
    SKILL.md
    scripts/
    references/
    examples/
    tests/
    output/
  creator-capture/
    SKILL.md
    scripts/
    references/
    examples/
    tests/
  account-brain/
    SKILL.md
    references/
    schemas/
    examples/
  codex-image-studio/
    SKILL.md
    references/
    assets/
    examples/
    prompts/
```

---

## 八、统一数据目录设计

建议单独维护一个工作区：

```text
competitor-workspace/
  raw/
    xhs/
    douyin/
    bilibili/
  normalized/
    account_profile.json
    posts.json
    comments.json
    visual_assets.json
  learned/
    behavior_dna.json
    positioning_model.json
    title_model.json
    copy_model.json
    visual_style_model.json
    posting_strategy_model.json
    conversion_model.json
    monetization_model.json
  generation/
    topic_input.json
    generated_titles.json
    generated_copy.json
    image_prompts.json
    final_posts/
```

---

## 九、典型使用场景

### 场景 1：搜一个账号是谁

只调用：
- `benchmark-orchestrator`
- `source-router`

输出：
- 账号背景
- 平台分布
- 是否值得继续抓取

### 场景 2：我想全面对标这个账号

调用：
- `benchmark-orchestrator`
- `source-router`
- `creator-capture`
- `account-brain`

输出：
- 账号镜像
- AI 学习模型

### 场景 3：我已经确认要学它，直接给我生成图文

调用：
- `benchmark-orchestrator`
- `account-brain`
- `codex-image-studio`

输出：
- 文案
- 图片 prompt
- 图文成品

---

## 十、实施优先级

### P0：先做强

1. `source-router`
2. `creator-capture`

原因：
- 前者是入口
- 后者是资产层

### P1：最关键的能力中枢

3. `account-brain`

原因：
- 它决定系统是不是“给 AI 学”

### P2：生产闭环

4. `codex-image-studio`

原因：
- 这是最终变现与产出的落点

### P3：最后补总控

5. `benchmark-orchestrator`

说明：
- 逻辑上它是总控
- 但工程上可以最后做
- 前期可以先用文档和手工调度模拟总控

---

## 十一、关键设计判断

### 1. 为什么不要单独保留 `pattern-miner`

因为它不应该作为独立面向用户的 skill 存在。

模式抽取本质上属于：
- `account-brain` 的内部能力

它应该服务行为编码，而不是单独暴露。

### 2. 为什么不要做“给我看的 clone kit”

因为你的目标不是人工阅读和学习，而是：

> **把行为系统喂给 AI**

所以输出要优先结构化对象，而不是长篇说明书。

### 3. 为什么图文赛道要先做视觉模型

因为图文赛道的竞争力很大一部分来自：
- 封面
- 版式
- 配色
- 信息组织
- 视觉人格

如果只有标题和正文，没有视觉行为模型，就不算真正对标。

---

## 十二、未来扩展方向

在图文赛道跑通后，可以扩展：

1. 短视频脚本生成
2. 视频分镜 prompt
3. 口播内容结构编码
4. 系列内容选题引擎
5. 多账号融合学习

但当前不建议分散注意力。

---

## 十三、结论

`wenxuan-skills` 最终要做的，不是“一个会搜索的 skill 包”，而是：

> **一个专业的对标技能系统**

它的核心能力链路是：

> 搜账号 -> 抓资产 -> 编码行为 -> 生成图文

其最终价值不是分析，而是：

> **让 AI 真的学会一个账号，并稳定生成该风格体系下的新内容**
