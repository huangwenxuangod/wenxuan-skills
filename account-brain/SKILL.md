---
name: account-brain
description: 从 `CaptureBundle` 推导可复用的学习资产和行为模型。
---

# Account Brain

这个 skill 读取 `creator-capture` 的输出，并生成学习资产。

当前主入口：

- `scripts/derive_learning_assets.py`

示例：

```bash
python scripts/derive_learning_assets.py capture-bundle.json --pretty
```

主要产物：

- `ContentKnowledgeKB`
- `VisualPromptKernel`
- `LearningAssetsBundle`

前提：

- 输入必须是 `CaptureBundle`
- 更完整的配置和流程见 `../README.md`
