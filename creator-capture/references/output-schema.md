# Creator Capture Output Schema

This skill writes machine-readable creator capture assets.

The canonical schema lives in:

- `scripts/schemas.py`

This file explains the intent of the main objects.

## Objects

### AccountProfile

Represents the creator account itself.

Core fields:

- `platform`
- `display_name`
- `handle`
- `bio`
- `profile_url`
- `follower_count`
- `following_count`
- `like_count`
- `verified`
- `external_links`
- `contact_methods`

### PostItem

Represents one post, note, article, reel, video, or thread item.

Core fields:

- `platform`
- `post_id`
- `post_type`
- `title`
- `cover_text`
- `body`
- `transcript`
- `published_at`
- `source_url`
- `media_urls`
- `hashtags`
- `metrics`
- `author`
- `metadata`

### VisualAsset

Represents one visual clue or asset group.

Core fields:

- `asset_type`
- `source_url`
- `dominant_colors`
- `layout_guess`
- `typography_guess`
- `decorative_elements`
- `visual_notes`

### CommentSignal

Represents comment-level patterns, not raw full comment dumps by default.

Core fields:

- `signal_type`
- `signal_text`
- `frequency_hint`
- `representative_examples`

### TrafficHook

Represents observable growth or funnel actions.

Examples:

- follow prompt
- collect/save prompt
- comment keyword prompt
- DM/private domain prompt
- homepage redirection

### MonetizationClue

Represents visible monetization signals.

Examples:

- course
- consulting
- community
- affiliate
- product
- sponsorship

### CaptureBundle

Represents the full capture result for one account.

Contains:

- account profile
- posts
- visuals
- comments
- traffic hooks
- monetization clues
- capture metadata

## Validation Rule

All outputs should validate through Pydantic before being treated as downstream inputs.
