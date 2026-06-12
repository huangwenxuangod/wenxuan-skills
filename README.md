# wenxuan-skills

一个面向开发、产品研究与内容工作流的本地 Skills 仓库。

当前目标不是收集零散提示词，而是把开发过程中反复出现的问题、判断规则和解决流程，逐步沉淀成可复用的 skills。

## Skills

当前共有 **4 个 Skills**，其中 3 个可用、1 个开发中：

| Skill | 状态 | 用途 |
|---|---|---|
| `anti-pua` | 开发中 | 由 AI 反向督促用户行动并完成目标。 |
| `core-only` | 可用 | 默认只输出核心结果，明确要求时再完整展开。 |
| `wenxuan-writer` | 可用 | 使用文轩的身份和既定风格撰写公众号长文。 |
| `zero-lost` | 可用 | 调度项目记忆，在新会话中恢复历史上下文。 |

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
├── core-only/
├── wenxuan-writer/
└── zero-lost/
```

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
