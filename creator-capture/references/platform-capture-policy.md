# Platform Capture Policy

## Goal

Define how `creator-capture` should behave across different platforms.

## Core Rules

1. Prefer confirmed API chains over speculative scraping.
2. Prefer account-level capture over keyword search result pages.
3. Treat search results as locator signals, not final capture.
4. Record capture completeness honestly.
5. Avoid pretending partial capture is full capture.

## Platform Strategy

### XHS

Preferred:

- `fetch_search_users`
- `fetch_user_info`
- `fetch_user_notes`

Optional deeper detail:

- note detail
- comments

### Douyin

Preferred:

- `handler_user_profile_v2`
- `fetch_user_post_videos`

### Bilibili

Preferred:

- user profile
- user videos

### WeChat MP

Preferred:

- official account search
- account article list
- article detail

### WeChat Channels

Preferred:

- user search
- home page
- comments when needed

### Instagram

Preferred:

- username -> user_id
- user profile
- user posts

### X / YouTube / Reddit

If full account capture is not yet available, mark results clearly as partial and record the next recommended capture path.
