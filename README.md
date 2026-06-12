# wenxuan-skills

一个面向开发、产品研究与内容工作流的本地 Skills 仓库。

当前目标不是收集零散提示词，而是把开发过程中反复出现的问题、判断规则和解决流程，逐步沉淀成可复用的 skills。

创建新 Skill 时遵循 [Skill 创建规范](./SKILL-CREATION.md)。

## Skills

当前共有 **5 个 Skills**：

| Skill | 状态 | 用途 |
|---|---|---|
| `anti-pua` | 可用 | 在用户拖延或找借口时反向督促行动。 |
| `learn` | 可用 | 深挖选题并生成可直接用于写作的学习包。 |
| `wenxuan-paper` | 可用 | 基于三遍阅读法深度解读学术论文，支持逐段精读。 |
| `wenxuan-title` | 可用 | 为文轩的文章生成标题与封面配文。 |
| `wenxuan-writer` | 可用 | 使用文轩的身份和既定风格撰写公众号长文。 |

## 设计原则

- 一个目录就是一个 skill。
- 每个 skill 至少包含 `SKILL.md`。
- 推荐补充 `agents/openai.yaml` 作为 UI 元数据。
- 复杂 skill 再按需补充 `references/`、`scripts/`、`assets/`。
- `SKILL.md` 只写触发条件、核心流程和边界，不堆砌大段背景。

## 当前结构

```text
wenxuan-skills/
├── README.md
├── anti-pua/
├── learn/
├── wenxuan-paper/
├── wenxuan-title/
└── wenxuan-writer/
```

## 内容生产链路

`learn → wenxuan-writer → wenxuan-title`

`anti-pua` 仅在用户拖延、逃避输出或中断链路时介入。

`wenxuan-paper` 独立触发，仅处理明确属于学术论文的 PDF。

## 适用场景

- 把常见开发错误变成固定排查流程
- 把重复性的 code review 关注点变成检查清单
- 把“某类问题如何修”变成可触发的 skill
- 把一次次有效经验沉淀成长期资产

## 仓库使用建议

- 新建 skill 时使用 `skill-creator` 初始化。
- 每次新增 skill，优先先写清楚：
  - 什么时候触发
  - 输入通常长什么样
  - 标准处理步骤是什么
  - 什么时候不该用这个 skill
- 如果一个问题已经重复出现 3 次以上，就值得独立成 skill

## 安装

把某个 skill 目录复制到：

`C:\Users\37453\.codex\skills\<skill-name>`

如果是本地开发，可直接把整个目录同步过去；安装后重启 Codex 以确保重新索引。

## 许可证

本仓库采用 [MIT License](./LICENSE)；基于第三方项目改造的 Skill 同时保留原作者版权声明。
