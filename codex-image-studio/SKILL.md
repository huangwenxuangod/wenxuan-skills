---
name: codex-image-studio
description: Generate image-first social posts from creator behavior models for Chinese image-and-text content workflows. Use when the user already has captured creator data or an account-brain bundle and wants AI to produce benchmark-inspired titles, copy, image prompts, page structure, or final multi-page post assets that follow the learned style system.
---

# Codex Image Studio

Use this skill to generate images and image-first social content from learned creator behavior models.

This skill is the production layer.

It does not do source discovery and should not be the first step in a benchmarking workflow unless the user already has structured account data.

## Read First

Before generating, read:

1. `../MASTER-PLAN.md`
2. `../account-brain/references/output-models.md`
3. `references/generation-rules.md`
4. `references/post-assembly-guide.md`
5. `schemas/models.py`

If the user only has a raw account JSON and no encoded behavior models yet, either:

1. route through `account-brain`, or
2. build a temporary lightweight behavior model from the raw JSON before generating.

## When To Use

Use this skill when the user wants to:

- generate a single image sample
- generate benchmark-inspired image assets
- generate benchmark-inspired image-and-text posts
- turn behavior models into titles, copy, image prompts, and page plans
- create AI-native visual posts for XHS / image-first channels
- generate new topics while staying close to a target account's behavior DNA

Do not use this skill as a raw analysis tool.

## Core Principle

Do not copy one post literally.

Generate by inheriting:

- title system
- copy system
- visual system
- conversion system

The goal is style-system transfer, not blind duplication.

Default image generation endpoint:

- `http://107.172.148.170:8000/v1`

Default model:

- `gpt-image-2`

API key:

- use `OPENAI_API_KEY` or pass `--api-key`

For image-first benchmark workflows, also consume the reverse-engineered visual prompt layer when available:

- keep the palette logic
- keep the layout grammar
- keep the compositional behavior
- change the actual topic and content

## Default Workflow

### 1. Validate generation inputs

Preferred input:

- `AccountBrainBundle`

Acceptable fallback:

- structured creator JSON with enough title, copy, visual, and CTA information to derive a temporary generation plan

Best input for deep generation:

- `AccountBrainBundle`
- `ContentKnowledgeKB`
- `VisualPromptKernel`
- `LearningAssetsBundle`

Recommended script:

- `scripts/generate_image_via_local_api.py`

Default execution flow:

1. read the user's generation instruction
2. build a precise image prompt
3. call the local image API with `gpt-image-2`
4. save the generated image
5. return the saved path and prompt used

### 2. Choose generation mode

Main modes:

1. `single-poster`
2. `multi-page-carousel`
3. `topic-batch`

Default for current project:

- `multi-page-carousel`

### 3. Generate content stack

Produce these layers in order:

1. topic angle
2. title set
3. body copy
4. page plan
5. image prompts
6. CTA and hashtag layer

### 3.1 Parallel generation

If multiple pages or multiple variant prompts are requested, these may run in parallel:

- title candidates
- page prompts
- visual variants
- final image renders

Keep the output bundle unified after all workers finish.

### 4. Keep generation constrained by the learned system

Title generation should follow:

- `TitleModel`

Copy generation should follow:

- `CopyModel`

Visual prompt generation should follow:

- `VisualStyleModel`
- `VisualPromptKernel`

Conversion prompts should follow:

- `ConversionModel`

### 5. Return machine-readable outputs

All outputs should validate against:

- `schemas/models.py`

Primary outputs:

1. `GenerationRequest`
2. `GeneratedTitleSet`
3. `GeneratedCopySet`
4. `ImagePromptSet`
5. `PostLayoutPlan`
6. `GeneratedPostBundle`

## Generation Rules

### Title Layer

Generate titles that preserve:

- promise style
- complexity level
- time compression
- instruction framing
- topic clarity

Do not merely paraphrase the source title.

### Copy Layer

Generate copy that preserves:

- opening style
- structural rhythm
- step density
- CTA location

### Visual Prompt Layer

Generate prompts that preserve:

- visual archetype
- palette
- texture/material
- border/decorative grammar
- layout grammar
- information density

### Page Planning Layer

For multi-page image posts, define:

1. cover page
2. explanation pages
3. reference/diagram pages if needed
4. CTA closing page

## Minimum Quality Bar

Before finishing, ask:

1. Does this feel like a style system, not a copy paste?
2. Are title, copy, and image prompts aligned?
3. Is the visual prompt precise enough for image generation?
4. Is the CTA consistent with the learned account behavior?
5. Could this output be rendered into a real post immediately?

If not, refine before returning.
