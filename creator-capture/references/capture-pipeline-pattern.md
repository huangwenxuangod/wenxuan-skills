# Capture Pipeline Pattern

This document defines the common shape for all `capture.py`-style scripts.

## Goal

The job is simple:

> account -> content

Nothing else.

## Fixed Chain

```text
account input
  -> parse identifier
  -> choose one platform flavor
  -> fetch list page(s)
  -> paginate with cursor or page number
  -> fetch detail for each post
  -> normalize to CaptureBundle
```

## Platform Flavor Rule

For a given platform, pick one stable flavor only.

Examples:

- XHS: `app_v2` or `web_v3`
- Douyin: one documented API chain
- Bilibili: one documented API chain

Do not combine app and web in one job unless you are deliberately comparing them.

## Pagination Rule

Every adapter should expose:

- `limit`
- `page_size`
- `max_pages`
- `cursor` or page number
- dedupe by post id

Stop when any of these is true:

1. target count reached
2. pagination ends
3. cursor stops changing
4. the platform stops returning usable content

## Detail Rule

List data is index data.

Detail data is truth data.

Prefer detail fields for:

- title
- body
- metrics
- media urls
- author

Use list fields only as fallback.

## Output Rule

Adapters should output:

1. account profile
2. post items
3. media references
4. traffic hooks
5. monetization clues
6. capture metadata

The result should be ready for `account-brain` without extra guessing.
