---
name: zero-lost
description: 当用户想继续一个项目、回忆之前做过什么、在新会话开始时读取项目记忆，或在切换会话后恢复历史上下文时使用。这个 skill 不重复实现记忆能力，而是调度 agentmemory 已有的 skills 与 session/memory 能力，让当前项目不再从零开始。
---

# Zero Lost

把这个 skill 当成“项目开工调度器”。

它的职责不是替代 `agentmemory`，也不是重写 recall；它的职责是先确保 `agentmemory` 官方 skills 可用，再按合适顺序调用它们，让当前项目带着上下文继续工作。

## 触发时机

- 用户会说类似：
  - 继续实现
  - 继续这个项目
  - 回忆一下之前做了什么
  - 我们上次做到哪了
  - 换了会话继续
  - 先读取项目记忆
- 当前任务明显依赖之前的项目历史、决策、bug、交接或约定。

## 核心行为

1. 默认把当前工作目录当成当前项目，除非用户明确指定其他范围。
2. 先确认 `agentmemory` 官方 skills 是否已经装到 Codex。
3. 如果缺失，先运行本 skill 自带的安装脚本补齐。
4. 安装后要明确告诉用户装上了什么，以及 hooks/connect 是否已刷新成功。
5. 在 Codex Desktop 尤其是 Windows 环境下，要额外检查 `session` / `observation` 是否真的在增长，不能只看插件是否已安装。
6. 如果 `Sessions: 0` 但 `Memories > 0`，优先判断是否只是手动写入了 memory，而生命周期 hooks 没有生效。
7. 如果检测到 Codex Desktop 插件 hooks 静默，要检查并修复全局 `~/.codex/hooks.json`，不要误判为 agentmemory 服务端故障。
8. 优先复用 `agentmemory` 已有的 skills 和能力，不重复发明同类功能。
9. 优先先读 memories，再追相关 sessions。
10. 如果缺少 session 来源链，要明确说明，不要假装它存在。
11. 如果 project scope 漂移到了别的仓库，要明确指出当前 memory 可能“有存但存错项目”。
12. 默认只输出一句话结论，除非用户明确要求展开。

## 调度顺序

当目标是恢复项目上下文时，按这个顺序调度：

1. 先检查 `agentmemory` 是否可用，官方 Codex skills 是否齐全。
   - 额外检查 `agentmemory status` 里的 `Sessions`、`Observations`、`Memories` 是否彼此一致。
   - 如果在 Codex Desktop 上 `Sessions: 0` 且插件已装好，优先怀疑 hooks 静默。
   - Windows 上如果 `agentmemory connect codex --with-hooks` 不能自动完成，要继续手动检查 `~/.codex/hooks.json` 是否存在、是否指向 agentmemory 的绝对脚本路径。
2. 再用 recall 类能力找当前项目相关的记忆、结论、交接和历史约定。
   - 如果 recall 命中了别的项目 scope，要明确告诉用户这是“旧项目记忆”，不能当作当前项目上下文直接使用。
3. 再用 session-history 类能力追相关 session 和 provenance。
   - 如果 session 为空但 REST 手动写入可用，要说明问题在 hook 分发层，不在存储层。
4. 最后把结果整理成正常回答，说明：
   - 这个项目之前在做什么
   - 当前最相关的历史结论是什么
   - 哪些结论有 session 支撑
   - 现在最可能该接着做什么
5. 默认把这些信息压缩成一句话，不主动分段或展开。

## Codex Desktop 特别规则

- 在 Codex Desktop 上，插件安装成功不等于 lifecycle hooks 生效；要优先验证是否真的产生了 session 和 observation。
- 如果 `~/.codex/hooks.json` 不存在，而插件 README 或诊断提示需要 `--with-hooks`，应视为高概率未接通。
- 手动修复 `~/.codex/hooks.json` 时，优先写入 agentmemory 官方 hooks 对应的绝对脚本路径，而不是依赖 `${CLAUDE_PLUGIN_ROOT}`。
- 手动修复后，要提醒用户“通常需要开一个新会话再验证”，因为当前会话未必会重新装载全局 hooks。

## Project Scope 规则

- 恢复上下文时，不只要看有没有 memory，还要看 memory 的 `project` 是否属于当前仓库。
- 如果当前工作目录和最近写入 memory 的 project scope 不一致，要明确提示 scope 漂移。
- 对需要长期保留的记忆，优先显式写入稳定 project 标识，避免被当前活跃 workspace root 误带到别的项目。

## 写回行为

如果这次会话产出了值得沉淀的长期结论，这个 skill 可以继续调用 `remember`、`commit-context`、`commit-history` 或 `handoff` 来写回记忆。

## 回退策略

- 如果官方 `agentmemory` skills 不能成功安装，就继续使用当前可用的 `agentmemory` 集成，并明确说明限制。
- 如果 `agentmemory` 整体不可用，就明确告诉用户当前无法读取项目记忆，不要编造上下文。

## 输出要求

默认只输出一句话结论，优先包含：

- 之前发生过什么
- 现在下一步该做什么

只有在用户明确要求详细、完整、展开、列表或结构化总结时，才补充更多层次。
