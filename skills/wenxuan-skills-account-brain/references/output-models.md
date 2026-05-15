# Account Brain Output Models

The canonical schema lives in:

- `schemas/models.py`

This file explains the meaning of each output object.

## Core Objects

### PositioningModel

Represents how the account positions itself.

Examples:

- teacher
- curator
- operator
- storyteller
- mysterious expert
- practical explainer

### TitleModel

Represents the account's title system.

Examples of what to encode:

- recurring formula patterns
- time-compression cues
- authority cues
- low-barrier cues
- intensity level

### CopyModel

Represents the body/content structure.

Examples:

- result first
- steps then explanation
- list-heavy
- teaching-heavy
- short command style
- dense note style

### VisualStyleModel

Represents image-side behavior.

Examples:

- retro teaching poster
- modern note-card layout
- screenshot annotation format
- diagram-first educational poster

### ContentKnowledgeKB

Represents the knowledge layer extracted from posts.

It should capture:

- knowledge domains
- recurring concepts
- topic clusters
- reusable explanations
- question-answer patterns
- background context for topic mining

### VisualPromptKernel

Represents the reverse-engineered visual prompt layer.

It should capture:

- palette tokens
- layout grammar
- typography feel
- decoration language
- spacing logic
- prompt-ready modifiers

### LearningAssetsBundle

Represents the paired output of:

- `ContentKnowledgeKB`
- `VisualPromptKernel`

This is the best bridge object for downstream generation.

### PostingStrategyModel

Represents how the account publishes over time.

Examples:

- daily posting
- topic clusters
- recurring series
- timing preference

### ConversionModel

Represents visible growth or funnel logic.

Examples:

- follow for next part
- save this
- comment keyword
- DM for material
- homepage redirect

### MonetizationModel

Represents visible and inferred monetization behavior.

Examples:

- course
- community
- consulting
- affiliate
- sponsored mention

### BehaviorDNA

Represents the compressed account identity that generation should inherit.

This is the shortest, most reusable abstraction of the creator.

### AccountBrainBundle

Represents the full machine-readable encoding package produced by this skill.
