---
name: wenxuan-skills-image-studio
description: 基于知识库和内容稿直接生成封面图和多页图文图像，同时保留 prompt 资产，最终结果统一落到 `wenxuan-output/image-studio/`。
---

# wenxuan-skills Image Studio

适用场景：

- 根据知识库和内容稿直接生成最终图片
- 自动输出封面图和分页图
- 同时保留 prompt 资产，方便复用和调优

主入口：

- `scripts/run_full_pipeline.py`
- `scripts/render_images.py`

输出目录：

- `./wenxuan-output/image-studio/`
