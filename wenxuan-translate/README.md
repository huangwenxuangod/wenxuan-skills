# Wenxuan Translate

> 专业中英翻译引擎（英文 → 中文）。

## 是什么

wenxuan-translate 是 wenxuan-skills 仓库下的第 7 个 skill，专门处理**英文内容到中文的专业翻译**。

**核心理念**：翻译不是换语言，是把英文背后的"具体的人/具体的位置/具体的代价"原汁原味带到中文里。

## 核心特性

| 特性 | 详情 |
|---|---|
| **人味双注入** | humanlize 心法（位置/代价/手迹），主 agent 过程注入 + sub-agent 后置复检 |
| **多 Agent 架构** | 主 agent + 人味 sub + 事实/溯源 sub（2 sub-agent 协同）|
| **9 大质量门** | F1-F9 硬约束（反虚构/术语一致/文化标注/决策记录/语气保留/长度适应/多轮自检/人工复检/反向校验）|
| **场景驱动** | H1 爆款 / H2 行业 / H4 个人收藏自动识别 |
| **Markdown-first** | 翻译→MD→PDF 分离（CSS 排版内置）|
| **必出 PDF** | 排版精美的纯中文 PDF |
| **术语表累积** | `references/terminology-glossary.md` 跨次翻译复用 |
| **声音校准 4 维** | 句长/标点/人称/正式度对齐原文 |
| **文化决策 5 步** | 搜索→识梗→选路→标注→复检全流程 |
| **反向校验 F9** | 关键段落中→英 back-translation，防止翻译失真 |

## 触发方式

1. `/wenxuan-translate <链接或文件>` — 主动
2. "翻译这个英文推文" / "把这段英文翻成中文" — 自然语言
3. "H1 翻译" / "H2 翻译" / "H4 翻译" — 强制场景

## 输入/输出

**输入**：
- 英文链接（WebFetch 抓取）
- 英文 Markdown 文档（.md 文件）
- 粘贴的英文文本

**输出**：
- `D:\path-to-wealth-freedom\内容\文章\翻译\译文-<原标题或日期>.md`（纯中文）
- `D:\path-to-wealth-freedom\内容\文章\翻译\译文-<原标题或日期>.pdf`（必出）

## 5 大流程

1. **Step 1 接收输入** —— 链接 / MD / 粘贴
2. **Step 2 场景识别 + 翻译** —— 主 agent + humanlize 过程注入
3. **Step 3 人味 sub-agent 复检** —— humanlize 心法后置审校
4. **Step 4 事实核查 + 溯源 sub-agent 并行** —— F1-F9 质量门
5. **Step 5 输出 MD + PDF** —— 必出

## 9 大质量门

| # | 名称 | 规则 |
|---|---|---|
| F1 | 反虚构核查 | 译文中不能出现"原文无"的内容 |
| F2 | 术语一致性 | 同一术语全文统一翻译 |
| F3 | 文化差异标注 | 英文俗语/双关/文化梗要标注（5 步决策树）|
| F4 | 翻译决策记录 | 关键术语/难点翻法要记录为什么 |
| F5 | 原文语气保留 | 讽刺/调侃/感叹，译文同等语气（4 维声音校准）|
| F6 | 长度自适应 | 中英文字数比按语义调整 |
| F7 | 多轮自检 | 翻译完自己读一遍，找"翻译腔"重写（AI 味 3 维分类）|
| F8 | 人工复检高亮 | 输出时高亮"建议人工复检"段落 |
| F9 | 反向校验 | 关键段落中→英 back-translation，防止翻译失真 |

详细规则见 `references/quality-gates.md`。

## 详细文档

- [SKILL.md](SKILL.md) —— 主 skill 定义（5 大流程 + 9 质量门 + 触发词 + 输入/输出）
- [references/humanlize-prompt-snippet.md](references/humanlize-prompt-snippet.md) —— humanlize 心法 Prompt 注入片段
- [references/translation-standards.md](references/translation-standards.md) —— 4 大翻译原则
- [references/quality-gates.md](references/quality-gates.md) —— 9 大质量门详细规则
- [references/terminology-research.md](references/terminology-research.md) —— 术语研究方法
- [references/terminology-glossary.md](references/terminology-glossary.md) —— 术语表（自动累积）

## 速览

| 维度 | 规则 |
|---|---|
| 翻译方向 | 英文 → 中文（v1 不做中→英）|
| 输入 | 链接 / MD / 粘贴文本 |
| 输出 | MD（纯中文）+ PDF |
| 质量门 | F1-F9 全部硬约束 |
| 场景 | H1/H2/H4 智能识别 + 可手动覆盖 |
| 子 Agent | 2 个（人味 + 事实/溯源）|
| humanlize 注入 | 双重（主 agent 过程 + sub-agent 后置）|
| 触发词 | `/wenxuan-translate` / "翻译..." / "H1 翻译" |
| 必出 | MD + PDF |
| 不支持 | PDF/截图/HTML（v1）|
