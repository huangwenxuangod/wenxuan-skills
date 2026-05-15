---
name: wenxuan-skills-creator-capture
description: 把已有账号导出结果规范化成 `CaptureBundle`，供后续学习和生成使用。
---

# Creator Capture

这个 skill 负责把已有原始导出结果整理成统一 `CaptureBundle`。

当前主入口：

- `scripts/normalize_input.py`

当前状态：

- 可以直接运行
- 当前明显支持小红书导出格式
- 更偏“规范化输入”，不是全自动在线抓取器

示例：

```bash
python scripts/normalize_input.py input.json --pretty
python scripts/normalize_input.py input.json --print-summary
```

输出目标：

- `AccountProfile`
- `PostItem`
- `VisualAsset`
- `TrafficHook`
- `MonetizationClue`
- `CaptureBundle`

统一使用方式见 `../README.md`。
