# wenxuan-skills

> 这是文轩的个人 Skill 仓库。把日常开发、写作、读论文、运营自媒体中反复用到的判断和流程，沉淀成可触发、可复用的 AI Skill。

不是收集零散提示词，而是把**「这件事我做过三遍以上、值得固化」**的经验，一条条攒下来。

---

## 6 个 Skills

| Skill | 状态 | 一句话 | 触发词 | 规模 |
|---|---|---|---|---|
| **`anti-pua`** | 可用 | 15 种大厂风味 × 三把心理刀，发现拖延就抽 | "我没空""我累了""明天再写" | 212 行 |
| **`wenxuan-learn`** | 可用 | 深挖选题，生成可写作的弹药包（强制事实核查） | `/wenxuan-learn` "我想写一篇关于 XX" | 241 行 |
| **`wenxuan-writer`** | 可用 | 按文轩的「踩坑大学生」口吻写公众号长文 | "写文章""帮我写""按我的风格写""AI 味太重" | 438 行 |
| **`wenxuan-title`** | 可用 | 融合爆款模板 + 哲学认知劫持，起最狠的标题 | `/wenxuan-title` "起个标题" | 791 行 |
| **`wenxuan-paper`** | 可用 | Keshav 三遍阅读法 × IMRaD 结构化拆解学术论文 | `/wenxuan-paper` `/deep` 论文 PDF | 452 行 |
| **`wenxuan-research`** | 可用 | 1 小时内为陌生行业建可沉淀的认知操作系统（数据库+竞品+内容+地图+机会） | `/wenxuan-research` "了解一下 XX 行业" | ~340 行 |
| **`hv-analysis`** | 可用（三方 fork）| 数字生命卡兹克出品，对一个对象做双轴深度研究 → 1-3 万字 PDF 报告 | `/hv-analysis` "研究一下 XX" "横纵分析" | 776 行 |

每个 Skill 独立成目录，详情见各目录下的 `SKILL.md`。

---

## 内容生产主链路

```
wenxuan-learn  →  wenxuan-writer  →  wenxuan-title
   挖弹药         写长文             起标题
```

**`anti-pua` 是链路里的"鞭子"**——用户在任意环节拖延、逃避、找借口，立刻介入。
**`wenxuan-paper` 是独立支线**——专门处理学术论文 PDF。
**`wenxuan-research` 是入口研究**——不写文章，只吃透一个行业，输出可沉淀的认知操作系统。

### 一个具体的例子

> 想写一篇《我用 AI 7 天做了个搞钱工具》

1. `/wenxuan-learn 我用AI做了个搞钱工具` → AI 跑 20+ 轮搜索，挖出 A/B/C/D/F 五层素材，每条事实声明通过核查，生成弹药包.md
2. 看弹药包定选题角度，开始写 → `wenxuan-writer` 按文轩的风格拉出 4000 字长文
3. 写到一半卡住/不想写 → `anti-pua` 介入抽你
4. 完稿想发 → `wenxuan-title` 生成 5 个爆款标题候选
5. 顺带看一篇 arXiv 论文做参考 → `wenxuan-paper` 三遍阅读拆解
6. 想研究一个具体公司/产品/概念 → `hv-analysis` 横纵分析 → 1-3 万字 PDF 报告

---

## 设计原则

- **一个目录就是一个 Skill**。目录名就是 Skill 名。
- **`SKILL.md` 只写触发条件、流程、边界**，不堆背景。
- **复杂 Skill 按需加 `references/`、`scripts/`、`assets/`**。
- **新 Skill 用 `skill-creator` 初始化**。
- **重复 3 次以上的问题，就值得独立成 Skill**。

---

## 当前结构

```text
wenxuan-skills/
├── README.md
├── SKILL-CREATION.md      # Skill 创建规范
├── LICENSE
├── anti-pua/              # 5 风味鞭策引擎
│   ├── SKILL.md
│   └── agents/openai.yaml
├── wenxuan-learn/         # 选题深挖
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/        # 搜索模板、Step5 引导问题
├── wenxuan-writer/        # 公众号长文
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/        # 风格案例库
├── wenxuan-title/         # 标题与封面
│   ├── SKILL.md
│   └── agents/openai.yaml
└── wenxuan-paper/         # 论文深度解读
    ├── SKILL.md
    ├── agents/openai.yaml
    └── scripts/pdf_to_text.py   # pymupdf4llm 转 markdown
└── wenxuan-research/      # 行业认知研究
    ├── SKILL.md
    └── agents/openai.yaml
└── hv-analysis/           # 横纵分析（卡兹克 fork）
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── references/schema.json
    └── scripts/md_to_pdf.py
```

---

## 安装与同步

### 首次安装

把整个仓库（或单个 Skill 目录）复制到 WorkBuddy 的 Skill 目录：

```bash
# 装全部
cp -r D:/dev/my-project/wenxuan-skills/* ~/.workbuddy/skills/

# 或只装一个
cp -r D:/dev/my-project/wenxuan-skills/wenxuan-writer ~/.workbuddy/skills/
```

### 仓库 ↔ WorkBuddy 双向同步

项目仓库是**权威源**（version-controlled），WorkBuddy 用户目录是**运行时副本**。同步两条规则：

| 方向 | 何时跑 | 命令 |
|---|---|---|
| 项目 → WorkBuddy | Skill 改完后 | `cp -r <skill> ~/.workbuddy/skills/` |
| WorkBuddy → 项目 | anti-pua 的 `tracker.md` 累积新记录后 | 单独 cp 那个 md 文件，再 git commit |

> **`anti-pua` 的 `tracker.md` 已迁出仓库**（commit `dcd156a`），它属于运行时数据，不进 git。

---

## 最近更新

| 日期 | 改动 |
|---|---|
| 2026-06-13 | `learn` → `wenxuan-learn` 重命名（统一 `wenxuan-` 前缀） |
| 2026-06-13 | `wenxuan-learn` 新增**事实核查**机制——不实数据/不存在引用不进弹药包 |
| 2026-06-13 | `anti-pua` v3.1，移除鼓励模式、15 风味×三把心理刀精简到 212 行 |
| 2026-06-13 | `wenxuan-writer` 融入 `renwei-writing` 心法（位置/代价/手迹三件套） |
| 2026-06-12 | 安装 `coreyhaines31/marketingskills` 44 个营销 skill 到 `~/.workbuddy/skills/` |
| 2026-06-12 | 新增 `wenxuan-paper`（论文深度解读）+ `scripts/pdf_to_text.py` |

---

## 适用场景

- 把开发中反复排查的错误固化成排查流程
- 把 code review 的关注点变成可触发的 checklist
- 把「某类问题怎么修」从脑子里的隐性知识变成显性的 Skill
- 把一次次的有效经验沉淀成长期资产，而不是每次重新发明轮子

---

## 许可证

本仓库采用 [MIT License](./LICENSE)；基于第三方项目改造的 Skill 同时保留原作者版权声明。
