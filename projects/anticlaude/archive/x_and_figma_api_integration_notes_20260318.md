# X and Figma API Integration Notes 2026-03-18

## 1. Purpose

This document records how AITOS should integrate:
- X posting and analytics access
- Figma API access

Important:
- sensitive secrets should not be stored in markdown files
- store them in `.env`, secret manager, or OS-level secure storage instead

## 2. Security Status

The X credentials and Figma token were pasted in plaintext during planning.

Recommendation:
- treat them as exposed
- move them into secure environment variables
- rotate/regenerate them as soon as practical

Reason:
- once secrets appear in chat, notes, screenshots, or copied docs, they should be considered compromised

## 3. X API Integration Model

## 3.1 Two X auth modes you want

### A. User-context posting

Use case:
- publish posts on your behalf
- delete your own posts

Auth model:
- OAuth 1.0a User Context

Your intended env vars:
- `X_API_KEY`
- `X_API_KEY_SECRET`
- `X_ACCESS_TOKEN`
- `X_ACCESS_TOKEN_SECRET`

Best use in AITOS:
- final publishing step
- delete/cleanup step
- any user-owned write action

## B. App-only analysis

Use case:
- recent search
- keyword/trend monitoring
- public post analytics
- counts and volume tracking

Auth model:
- OAuth 2.0 App-Only Bearer Token

Your intended env var:
- `X_BEARER_TOKEN`

Best use in AITOS:
- Orio trend monitoring
- search-based topic discovery
- volume and trend analysis

## 3.2 Official X guidance

Useful official sources:
- Developer Console: https://docs.x.com/fundamentals/developer-portal
- OAuth 1.0a overview: https://docs.x.com/fundamentals/authentication/oauth-1-0a/overview
- API key / secret handling: https://docs.x.com/fundamentals/authentication/oauth-1-0a/api-key-and-secret
- App-only bearer token: https://docs.x.com/resources/fundamentals/authentication/oauth-2-0/bearer-tokens
- Create/delete posts quickstart: https://docs.x.com/x-api/posts/manage-tweets/quickstart
- Delete post endpoint: https://docs.x.com/x-api/posts/delete-post
- Recent search quickstart: https://docs.x.com/x-api/posts/search/quickstart/recent-search
- Recent counts quickstart: https://docs.x.com/x-api/posts/counts/quickstart/recent-tweet-counts

## 3.3 Practical AITOS role mapping

### Write path

Owner:
- Craft prepares content
- CEO approves
- publishing adapter posts to X

Recommended future env usage:
- `X_API_KEY`
- `X_API_KEY_SECRET`
- `X_ACCESS_TOKEN`
- `X_ACCESS_TOKEN_SECRET`

Recommended future module:
- `src/publishers/x_client.py`

Suggested functions:
- `create_post(text: str, media_ids: list[str] | None = None)`
- `delete_post(post_id: str)`
- `reply_to_post(post_id: str, text: str)`

### Research path

Owner:
- Orio for discovery
- Sage for analytics

Recommended future env usage:
- `X_BEARER_TOKEN`

Recommended future module:
- `src/social/x_search.py`

Suggested functions:
- `search_recent_posts(query: str)`
- `get_recent_counts(query: str)`
- `get_user_timeline(username: str)`

## 3.4 Recommended .env shape

Do not place real values in docs.
Store them like this:

```env
X_API_KEY=...
X_API_KEY_SECRET=...
X_ACCESS_TOKEN=...
X_ACCESS_TOKEN_SECRET=...
X_BEARER_TOKEN=...
```

## 3.5 Recommended usage policy

Use OAuth 1.0a credentials only for:
- posting
- deleting
- replying
- user-context actions

Use Bearer Token only for:
- public search
- trend discovery
- post counts
- public timeline/lookup scenarios supported by app-only auth

Do not mix them casually.

## 4. Figma API Integration Model

## 4.1 What you likely have

The token prefix you provided strongly suggests a Figma token.

Recommended env var name:
- `FIGMA_API_TOKEN`

Alternative naming:
- `FIGMA_PAT`

Do not store the raw token in docs.

## 4.2 Official Figma guidance

Useful official sources:
- Authentication: https://developers.figma.com/docs/rest-api/authentication/
- Scopes: https://developers.figma.com/docs/rest-api/scopes/
- Manage personal access tokens: https://help.figma.com/hc/en-us/articles/8085703771159-Manage-personal-access-tokens
- Rate limits: https://developers.figma.com/docs/rest-api/rate-limits/
- Changelog (PAT expiry/scopes updates): https://developers.figma.com/docs/rest-api/changelog/

## 4.3 Key security facts

Important notes from Figma docs:
- personal access tokens act as your account
- use a separate token per integration
- tokens are shown only once when created
- PATs now have a maximum expiry of 90 days
- use granular scopes such as `file_content:read`

This matters a lot for AITOS because:
- one leaked token can expose your files
- a PAT is not the same as a low-risk read key

## 4.4 Recommended AITOS use cases

Good use cases:
- Lumi reads file structure/content
- design-to-code workflows
- extracting node data or component references
- design review support

Avoid initially:
- write-capable automation
- broad, unattended design mutations

## 4.5 Recommended starting scope

Start with minimum viable read-only access.

Likely first scope:
- `file_content:read`

Add more only if needed.

## 4.6 Recommended request pattern

Store token in env:

```env
FIGMA_API_TOKEN=...
```

Use header:

```http
X-Figma-Token: <FIGMA_API_TOKEN>
```

Recommended future module:
- `src/integrations/figma_client.py`

Suggested functions:
- `get_file(file_key: str)`
- `get_file_nodes(file_key: str, node_ids: list[str])`
- `get_comments(file_key: str)`

## 5. Where These Should Fit In AITOS

## X integration

Recommended domain placement:
- `src/social/`
- or `src/publishers/`

Suggested split:
- `src/social/x_search.py`
- `src/publishers/x_client.py`

## Figma integration

Recommended domain placement:
- `src/integrations/figma_client.py`

Potential owner:
- Lumi

## Shared secrets/config

Current best fit:
- `.env`
- `src/config.py`

Do not place secrets in:
- strategy markdown
- sprint docs
- handoff logs
- screenshots

## 6. Recommended Immediate Next Steps

1. Move all X and Figma secrets into `.env`
2. Rotate the exposed secrets
3. Add env-variable placeholders to `.env.example` if missing
4. Create integration client stubs:
   - `src/publishers/x_client.py`
   - `src/social/x_search.py`
   - `src/integrations/figma_client.py`
5. Add a publishing approval rule so auto-posting cannot happen accidentally

## 7. Operational Warning

Auto-posting is powerful but risky.

Before enabling autonomous publish-to-X, add:
- final human approval
- dry-run mode
- audit logging
- delete/rollback procedure

For Figma access, add:
- least-privilege scopes
- token rotation reminders
- file allowlist if possible

## 8. Bottom Line

Yes, both X and Figma should be part of the system.

Recommended framing:
- X = publishing + trend sensing
- Figma = design intelligence and implementation support

But:
- do not store secrets in markdown
- rotate the secrets that were exposed in plaintext
- add approval controls before turning on autonomous publishing
