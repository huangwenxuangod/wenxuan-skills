# Skill 创建规范

## 核心原则

Skill 不是普通提示词，而是一个可自动触发、可复用、可验证的标准化工作流。

## 目录结构

```text
skill-name/
├── SKILL.md              # 必需
├── agents/openai.yaml    # 推荐，Codex UI 元数据
├── references/           # 可选，详细资料
├── scripts/              # 可选，重复执行的脚本
└── assets/               # 可选，模板与输出素材
```

不创建无必要的 README、安装说明或重复文档。

## SKILL.md

```yaml
---
name: skill-name
description: 说明这个 Skill 做什么，以及用户在什么场景或使用什么表达时应触发。
---
```

- `name` 必须与目录名一致，只用小写字母、数字和连字符，最长 64 字符。
- `description` 是自动触发的核心，必须同时写清能力、使用场景和关键触发词，最长 1024 字符。
- 不在 frontmatter 中直接添加 `version`、`author` 等字段；需要时放进 `metadata`。
- 仅在 Skill 有特定系统、软件、网络或工具要求时添加 `compatibility`。
- 正文使用命令式表达，只保留工作流、决策规则、边界和输出格式。
- 建议控制在 500 行、5000 tokens 内；超出部分移入 `references/`。

## 设计要求

1. **单一职责**：一个 Skill 解决一类稳定、重复出现的问题。
2. **明确触发**：说明什么时候用、什么时候不用，避免过度触发。
3. **流程闭环**：写清输入、处理步骤、输出和失败处理。
4. **渐进加载**：核心规则放 `SKILL.md`，详细资料按需读取。
5. **真实边界**：不编造信息，不覆盖系统规则，不依赖不存在的工具。
6. **联动克制**：只声明必要的上下游交接，不假设其他 Skill 一定自动加载。
7. **版权清晰**：改造第三方 Skill 时保留原许可证和作者声明。

## 创建流程

1. 用具体输入输出样例定义问题和边界。
2. 使用 `$skill-creator` 初始化目录。
3. 编写精简的 `SKILL.md`，按需添加资源。
4. 生成 `agents/openai.yaml`。
5. 运行：

```powershell
python "$HOME\.codex\skills\.system\skill-creator\scripts\quick_validate.py" <skill目录>
```

6. 用真实任务测试触发准确性、结果质量和失败边界。

## 全局安装

将完整 Skill 目录复制到：

```text
C:\Users\<用户名>\.codex\skills\<skill-name>
```

安装后重启 Codex。

## 发布检查

- [ ] 目录名与 `name` 一致
- [ ] `description` 包含能力与触发场景
- [ ] frontmatter 通过校验
- [ ] 引用的文件和脚本真实存在
- [ ] 没有重复、过期或无关内容
- [ ] 第三方内容保留版权
- [ ] 已用真实任务测试

## 参考

- [Agent Skills 规范](https://agentskills.io/specification)
- [Agent Skills 最佳实践](https://agentskills.io/skill-creation/best-practices)
- [OpenAI Codex Skills](https://developers.openai.com/codex/skills)
