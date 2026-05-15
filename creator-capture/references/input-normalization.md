# Input Normalization Logic

This document defines how `creator-capture` should read third-party creator exports and convert them into `CaptureBundle`.

The goal is not to preserve every raw field forever.

The goal is to:

1. detect the source format
2. extract the stable creator signals
3. normalize them into canonical schema
4. keep enough metadata to trace provenance

## 1. Think in Three Layers

Any incoming account JSON should be read as three layers:

### Layer A: capture metadata

This tells us:

- when the data was fetched
- from which provider / endpoint
- what platform it came from
- whether pages were truncated or partial

Typical fields:

- `meta`
- `page_summaries`
- `detail_errors`

### Layer B: content index

This is the lightweight post list.

It usually contains:

- post id
- title
- publish time
- list metrics
- preview images

Typical fields:

- `items[*].list_item`

### Layer C: content detail

This is the rich post payload.

It usually contains:

- full body
- hashtags/topics
- detailed metrics
- share link
- media gallery
- author object

Typical fields:

- `items[*].detail...note_list[0]`

## 2. Priority Rule

When both list-level and detail-level data exist:

1. prefer detail-level fields
2. fall back to list-level fields
3. keep the source path in metadata

This is the default rule for:

- title
- body
- metrics
- media urls
- author info

## 3. Normalize into Canonical Objects

The raw input must be split into the canonical `creator-capture` objects:

1. `AccountProfile`
2. `PostItem`
3. `VisualAsset`
4. `CommentSignal`
5. `TrafficHook`
6. `MonetizationClue`
7. `CaptureBundle`

Do not treat the entire raw payload as a single downstream object.

## 4. Current Generic Decision Tree

### Case A: raw account export

Example signal:

- top-level `meta`
- top-level `items`
- each item contains both list and detail blocks

Action:

- normalize into `CaptureBundle`

### Case B: already normalized creator assets

Example signal:

- already has `account_profile`
- already has `posts`
- already has `capture_meta`

Action:

- validate against `CaptureBundle`
- do not re-normalize unless upgrading schema

### Case C: behavior-level bundle

Example signal:

- has `behavior_dna`
- has `title_model`
- has `copy_model`

Action:

- this belongs to `account-brain`, not `creator-capture`

## 5. XHS Account Export Pattern

The current concrete adapter supports a source shape like:

```text
meta
page_summaries
items[]
  note_id
  title
  publish_time
  list_item
  detail
detail_errors
```

Read it like this:

1. `meta` -> `CaptureMeta` seed and provenance
2. root user from first usable `detail.note_list[0].user`
3. each `items[*]` -> one `PostItem`
4. each post gallery -> one `VisualAsset`
5. CTA phrases across posts -> `TrafficHook`
6. monetization phrases across posts -> `MonetizationClue`
7. visible comment counts -> `CommentSignal`

## 6. Provenance Rule

Every normalized post should preserve enough traceability to audit where it came from.

Minimum provenance:

- raw input file path
- provider / endpoint
- post id
- profile url or post share url if available

## 7. Completeness Rule

Completeness is judged by downstream usefulness, not file size.

### `high`

- profile exists
- posts exist
- full body exists
- media urls exist
- profile depth exists such as bio or follower stats

### `partial`

- profile exists
- posts exist
- body and metrics mostly exist
- some profile depth is missing

### `low`

- only search/index fragments exist
- or very few posts are usable

## 8. Future Common Logic

This should become the generic ingress path:

```text
raw export
  -> detect format
  -> choose platform adapter
  -> normalize to CaptureBundle
  -> validate with Pydantic
  -> pass to account-brain
```

Current script:

- `scripts/normalize_input.py`

Current first-class adapter:

- XHS account post export from TikHub-like payloads
