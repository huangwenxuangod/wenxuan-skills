# Post Assembly Guide

## Goal

Describe how generated outputs should be assembled into a real image-and-text post package.

## Default Post Types

### 1. Single Poster

Best for:

- one-shot knowledge posters
- summary cards
- announcement-style educational visuals

### 2. Multi-page Carousel

Best for:

- explanation chains
- teaching breakdowns
- step-by-step educational content

Recommended page sequence:

1. cover / hook
2. setup / framing
3. core steps
4. examples or mapping
5. CTA / save / follow prompt

### 3. Topic Batch

Best for:

- generating multiple post ideas at once
- weekly content planning

## Output Layers

The skill should assemble or describe:

1. title candidates
2. main copy
3. page-level copy
4. image prompts
5. CTA
6. hashtags

## If the user already has one account JSON

Run this sequence:

1. validate the JSON structure
2. identify whether it maps closer to creator-capture output or account-brain output
3. if it is capture-like, derive both:
   - `ContentKnowledgeKB`
   - `VisualPromptKernel`
4. if it is already behavior-like, generate directly
5. emit a complete `GeneratedPostBundle`

The split matters:

- knowledge layer -> topic mining /选题挖掘
- visual layer -> prompt reverse engineering / style transfer
