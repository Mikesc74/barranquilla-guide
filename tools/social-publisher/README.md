# Barranquilla.Guide social publisher

Daily Cloudflare-Pages-friendly replacement for the old WordPress → FB/IG auto-post flow.

## What it does
1. Walks the repo for `<slug>/index.html` pages and pulls `og:title`, `og:description`, `og:image`, and the canonical URL out of each.
2. Loads `posted_history.json` from this folder. Filters out anything posted in the last 90 days and deprioritizes categories posted in the last 4 runs.
3. Picks one article (deterministic per calendar day so a retry on the same day hits the same pick).
4. Calls `claude-haiku-4-5-20251001` for platform-specific captions (Facebook keeps the URL, Instagram uses a "Link in bio" CTA plus hashtags, no emojis, evergreen phrasing).
5. Publishes the og:image + caption to the Facebook Page via Graph API, then to the Instagram Business account via the two-step container → publish flow.
6. Appends the run to `posted_history.json`.

## Required environment variables
| Var | What it is |
|---|---|
| `ANTHROPIC_API_KEY` | `sk-ant-...` for the caption model |
| `FB_PAGE_ID` | Numeric Page ID for the Barranquilla.Guide FB Page |
| `FB_PAGE_TOKEN` | Long-lived Page access token with `pages_manage_posts`, `pages_read_engagement` |
| `IG_USER_ID` | Instagram Business account ID linked to the FB Page |
| `IG_TOKEN` | Optional — defaults to `FB_PAGE_TOKEN` if the same long-lived token covers IG publishing |

## Running locally
```bash
pip install anthropic requests --break-system-packages -q
export ANTHROPIC_API_KEY=sk-ant-...
export FB_PAGE_ID=...
export FB_PAGE_TOKEN=...
export IG_USER_ID=...
python3 publisher.py
```

## Why it's in the repo
Scheduled-task sandboxes don't persist between runs, so `publisher.py` and `posted_history.json` need a durable home. The repo is the only durable store we already trust. The scheduled task clones this repo, runs the publisher, then commits and pushes the updated `posted_history.json` back to `main`.

`/tools/*` is 404'd on the live site via `_redirects` so these files aren't publicly served.
