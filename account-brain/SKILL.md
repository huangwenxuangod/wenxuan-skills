---
name: account-brain
description: Encode creator accounts into structured AI learning models for benchmarking and generation. Use when the user wants AI to learn how a target account operates, not just see a human-readable report; use after creator capture when turning profile, posts, visuals, traffic hooks, publishing rhythm, and monetization clues into reusable behavior models such as title formulas, copy structure, visual style rules, conversion logic, and overall behavior DNA.
---

# Account Brain

Use this skill to convert captured creator assets into machine-readable behavior models.

This skill is not for writing polished competitor analysis articles.

Its purpose is:

1. read normalized creator assets
2. infer the account's operating logic
3. encode that logic into stable schemas
4. prepare downstream inputs for generation skills

## Read First

Before encoding, read:

1. `../MASTER-PLAN.md`
2. `../creator-capture/references/output-schema.md`
3. `references/behavior-encoding-rules.md`
4. `references/output-models.md`

If the account has not yet been captured into structured assets, go back to `creator-capture` first.

## When To Use

Use this skill when the user wants to:

- teach AI how a target creator account behaves
- convert captured content into reusable strategy models
- model titles, copy, visuals, conversion, and monetization in structured form
- create a behavior system that later image/text generation can use

Do not use this skill as the first step in discovery.

## Core Principle

Do not ask "is this account good?"

Ask:

- how does it position itself
- how does it title
- how does it structure copy
- how does it construct visuals
- how does it convert attention
- how does it hint monetization
- what repeatable rules describe the account

And split the source into two downstream tracks:

1. content knowledge extraction
2. visual style reverse-engineering

The output is for AI learning, not for manual admiration.

## Default Workflow

### 1. Validate inputs

Expect upstream structured inputs shaped by `creator-capture`.

Minimum useful inputs:

1. account profile
2. post list
3. visual asset hints
4. traffic hooks
5. monetization clues

### 2. Separate signal layers

Encode the account into these layers:

1. positioning
2. title system
3. copy system
4. visual system
5. publishing rhythm
6. conversion system
7. monetization system

Do not collapse everything into one prose summary.

Also emit two machine-friendly derivatives:

1. `content_kb`
   - concepts
   - background knowledge
   - topic clusters
   - reusable explanations
   - question space for topic mining

2. `visual_prompt_kernel`
   - palette tokens
   - layout grammar
   - typography feel
   - decorative language
   - prompt-ready style modifiers

### 2.1 Parallel derivation

These derivations can run in parallel after capture validation:

- `positioning`
- `title system`
- `copy system`
- `visual system`
- `posting rhythm`
- `conversion system`
- `monetization system`
- `content_kb`
- `visual_prompt_kernel`

### 3. Prefer rule extraction over commentary

Bad output:

- "This account uses strong titles."

Good output:

- what title formulas recur
- what promise style it uses
- what emotion level it prefers
- what opening components repeat
- what word density and instruction density show up

### 4. Produce machine-readable models

All outputs must validate against:

- `schemas/models.py`

Primary outputs:

1. `BehaviorDNA`
2. `PositioningModel`
3. `TitleModel`
4. `CopyModel`
5. `VisualStyleModel`
6. `PostingStrategyModel`
7. `ConversionModel`
8. `MonetizationModel`
9. `AccountBrainBundle`

Recommended derivative outputs:

- `ContentKnowledgeKB`
- `VisualPromptKernel`
- `LearningAssetsBundle`

### 5. Record confidence and uncertainty

Every encoded model should distinguish:

- observed recurring rule
- inferred likely rule
- unsupported guess

Do not overclaim precision where capture coverage is partial.

## Encoding Rules

### Positioning

Encode:

- display role
- audience
- promise
- authority style
- tone

### Title Model

Encode:

- recurring formulas
- opening components
- promise style
- urgency level
- emotion level
- instruction density
- common title lengths

### Copy Model

Encode:

- opening style
- structure template
- step density
- list density
- explanation style
- CTA style
- typical ending pattern

### Visual Style Model

Encode:

- color system
- material/background style
- border or decorative grammar
- layout grammar
- information density
- image subject type
- typography feel

### Content Knowledge KB

Encode:

- underlying knowledge domains
- recurring concepts
- topic clusters
- reusable explanations
- evidence points
- question-answer patterns
- expansion opportunities

### Visual Prompt Kernel

Encode:

- style tokens
- layout rules
- palette cues
- typography cues
- spacing rules
- negative constraints
- composition instructions

### Posting Strategy

Encode:

- publish rhythm
- content frequency
- topic cluster behavior
- time preference
- series behavior

### Conversion Model

Encode:

- follow hooks
- save/collect hooks
- comment prompts
- private-domain redirects
- homepage or DM pathways

### Monetization Model

Encode:

- visible offers
- inferred offer type
- trust-building content role
- acquisition content role
- conversion content role

## Minimum Quality Bar

Before finishing, ask:

1. Did I produce rules instead of vague praise?
2. Did I separate title, copy, visual, conversion, and monetization?
3. Did I mark uncertain inference honestly?
4. Is the output ready for `codex-image-studio`?
5. Could another agent use this without re-reading the original account manually?

If not, keep refining.
