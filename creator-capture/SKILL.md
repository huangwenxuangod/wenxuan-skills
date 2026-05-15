---
name: creator-capture
description: Capture public assets from target creator accounts across XHS, Douyin, Bilibili, WeChat MP, WeChat Channels, Instagram, X, YouTube, and related platforms. Use when the user wants to fully benchmark a specific account, collect its profile, posts, titles, publish times, visuals, traffic hooks, comment signals, monetization clues, or build a machine-readable mirror of a creator account for later AI learning and generation.
---

# Creator Capture

Use this skill to turn a target creator account into structured assets that later skills can learn from.

This skill is not for writing polished competitor reports.

Its job is:

1. identify the account
2. capture public content and signals
3. normalize them into stable schema
4. record confidence, gaps, and platform limits honestly

## Read First

Before capturing, read:

1. `../MASTER-PLAN.md`
2. `../source-router/references/tikhub-endpoints.md`
3. `../source-router/references/browser-use-strategy.md`
4. `references/output-schema.md`
5. `references/platform-capture-policy.md`

If the request starts from a vague query rather than a confirmed account, use `source-router` first.

## When To Use

Use this skill when the user asks to:

- benchmark one specific creator account deeply
- capture an account's posts, visuals, publish rhythm, CTA, comments, or monetization signals
- learn "everything" about an account in a machine-readable way
- build a creator mirror for later AI training or generation
- gather raw assets for `account-brain`

Do not use this skill as the first step for broad discovery across many unrelated accounts.

## Default Workflow

### 1. Confirm capture target

Extract or confirm:

1. platform
2. account name / handle / link
3. scope: latest N / time range / all visible
4. content filter: all / topic-specific / post type
5. sort: newest / hottest / relevance

If the target account is not yet identified, route through `source-router`.

### 2. Choose one platform flavor

For each platform, prefer one stable capture flavor only.

Examples:

- XHS: use `app_v2` or `web_v3`, not both in one adapter
- Douyin: choose one documented endpoint chain and keep it consistent
- Bilibili: choose one stable list/detail pair

Do not mix `app` and `web` paths in the same capture job unless you are explicitly comparing them.

### 3. Choose capture path

Prefer this order:

1. confirmed TikHub API path
2. provider/API path already supported in scripts
3. public web extraction
4. browser-use fallback for JS-heavy or login-influenced public pages

Do not pretend browser fallback equals full structured platform access.

### 4. Capture assets

Try to collect:

- account profile
- post index
- post details
- visual references
- traffic hooks
- comment signals
- monetization clues

Capture what is visible and supported; record gaps explicitly.

### 4.1 Parallelizable capture units

When the platform and rate limits allow it, these units may run in parallel:

- detail fetches for multiple post ids
- media url collection
- comment signal sampling
- monetization clue scanning

Keep one capture job centered on one account, but do not serialize independent detail fetches unless the endpoint requires it.

### 5. Paginate safely

Pagination must be explicit and bounded.

Required controls:

- page cursor or page number
- page size
- max pages
- target limit
- dedupe by post id

Default pattern:

1. fetch one list page
2. collect candidate post ids
3. fetch details for each candidate
4. stop when the requested count is met or pagination ends

Never assume one page is enough unless the platform contract guarantees it.

### 6. Normalize output

All capture outputs must validate against the Pydantic schema in:

- `scripts/schemas.py`

Write structured JSON first. Human-readable markdown is secondary.

### 7. Report confidence and limits

Every capture should record:

- attempted sources
- successful sources
- failed sources
- completeness: `high | partial | low`
- why anything is missing

## Output Standard

Default outputs should be shaped around these objects:

1. `AccountProfile`
2. `PostItem`
3. `VisualAsset`
4. `CommentSignal`
5. `TrafficHook`
6. `MonetizationClue`
7. `CaptureBundle`

The exact schema lives in:

- `scripts/schemas.py`
- `references/output-schema.md`

## Platform Rules

### XHS / Douyin / Bilibili / WeChat / Instagram

Use confirmed TikHub endpoints first.

Only use documented endpoint chains recorded in:

- `../source-router/references/tikhub-endpoints.md`

Do not invent endpoint names.

## Canonical Capture Shape

Every capture adapter should follow the same chain:

```text
account identifier
  -> list endpoint
  -> cursor/page pagination
  -> detail endpoint
  -> normalize post records
  -> emit CaptureBundle
```

The adapter should focus on:

- account profile
- post list
- post detail
- media urls
- metrics
- captions / body text
- tags / topics
- signals for traffic and monetization

It should not branch into unrelated analysis workflows.

### X / YouTube / Reddit / Bilibili search-like cases

If true account capture is not available yet, keep the result marked as:

- `phase1_adapter`
- `partial`
- `search_url_only`

Do not package a search URL as if the account was fully captured.

### Browser fallback

Use browser fallback only when:

- the page is JS-heavy
- public information is visible but not extractable by plain HTTP
- a login-adjacent public page needs DOM inspection

Follow:

- `../source-router/references/browser-use-strategy.md`

## Minimum Quality Bar

Before finishing, ask:

1. Did I capture the account itself, not just search results?
2. Did I separate profile, posts, visuals, traffic, and monetization signals?
3. Did I validate output structure?
4. Did I mark missing data honestly?
5. Is this output ready for `account-brain`?

If not, keep iterating or clearly report the blocker.
