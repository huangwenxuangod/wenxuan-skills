---
name: wenxuan-skills-codex-image-studio
description: 使用统一环境变量和图片接口生成图片，作为内容生产层的最小入口。
---

# Codex Image Studio

这个 skill 当前保留一个最小可运行入口：

- `scripts/generate_image_via_local_api.py`

它现在会自动读取仓库根目录 `.env`，不需要单独在 shell 里再手动导出。

最小示例：

```bash
python scripts/generate_image_via_local_api.py --prompt "极简中文知识海报，米白底，深棕标题，卡片布局" --out output/sample.png
```

关键环境变量：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_IMAGE_MODEL`

统一使用方式见 `../README.md`。
