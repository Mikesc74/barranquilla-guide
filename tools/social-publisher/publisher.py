#!/usr/bin/env python3
"""
Barranquilla.Guide daily social publisher.

Scans the repo's static HTML articles, picks one that hasn't been posted in the
last 90 days, generates platform-specific captions with Claude Haiku, and
publishes to the Barranquilla.Guide Facebook Page and Instagram Business account.

Credentials are read from environment variables (see SKILL.md or .env.example).
History is tracked in tools/social-publisher/posted_history.json and committed
back to the repo after each run (handled by the scheduled task wrapper).
"""

import json
import os
import random
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from html import unescape
from pathlib import Path

import requests

try:
    from anthropic import Anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic requests --break-system-packages", file=sys.stderr)
    sys.exit(1)


# --- config ---------------------------------------------------------------

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
HISTORY_PATH = HERE / "posted_history.json"

SITE_ORIGIN = "https://barranquilla.guide"
REPOST_COOLDOWN_DAYS = 90
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

# Folders in the repo that are NOT individual articles.
NON_ARTICLE_DIRS = {
    "css", "img", "js", "fonts", "section", "category", "tag",
    "about", "contact", "advertise", "tools", ".git", ".github",
    "barranquilla-guide",  # looks like a stray duplicate-home folder
}

# Category buckets for rotation.
CATEGORY_KEYWORDS = [
    ("Stay",       ["hotel", "hotels", "hostel", "hostels", "airbnb", "accommodation", "stay"]),
    ("Eat & Drink",["restaurant", "restaurants", "food", "cafe", "cafes", "coffee", "dessert", "desserts",
                    "bar", "bars", "drink", "drinks", "seafood", "breakfast", "brunch"]),
    ("Do",         ["tour", "tours", "museum", "beach", "beaches", "park", "parks", "mall", "malls",
                    "nightlife", "carnival", "festival", "walk", "walking", "bike", "biking",
                    "dance", "dancing", "ecopark", "bocas"]),
    ("Live",       ["cost-of-living", "expat", "moving", "banking", "coworking", "gym", "gyms",
                    "insurance", "visa", "dental", "wedding", "weddings", "kids", "family",
                    "medical", "networking"]),
    ("Know",       ["airport", "map", "safety", "weather", "climate", "neighborhood", "neighborhoods",
                    "transport", "taxi", "uber"]),
]


# --- data model -----------------------------------------------------------

def log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}", flush=True)


def load_history() -> dict:
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text())
        except json.JSONDecodeError:
            log("WARN: posted_history.json unreadable; starting fresh")
    return {"posts": []}


def save_history(history: dict) -> None:
    HISTORY_PATH.write_text(json.dumps(history, indent=2, ensure_ascii=False))


def categorize(slug: str) -> str:
    # Slugs are hyphen-separated, e.g. "best-bars-craft-drinks-barranquilla".
    # Match on exact tokens so "bar" doesn't match "barranquilla" and
    # "stay" doesn't match every other article.
    tokens = set(slug.lower().split("-"))
    for cat, kws in CATEGORY_KEYWORDS:
        for kw in kws:
            # multi-word keyword (e.g. "cost-of-living") -> substring check
            if "-" in kw:
                if kw in slug.lower():
                    return cat
            elif kw in tokens:
                return cat
    return "Know"


META_RE = re.compile(
    r'<meta\s+[^>]*(?:property|name)=["\']([^"\']+)["\']\s+content=["\']([^"\']*)["\']',
    re.I,
)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
CANONICAL_RE = re.compile(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', re.I)


def parse_article(index_html: Path):
    """Return dict with slug, url, title, description, image, published, modified — or None."""
    try:
        html = index_html.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        log(f"WARN: unreadable {index_html}: {e}")
        return None

    metas = {name.lower(): unescape(val) for name, val in META_RE.findall(html)}

    canonical_match = CANONICAL_RE.search(html)
    canonical = canonical_match.group(1) if canonical_match else None

    title = metas.get("og:title") or (TITLE_RE.search(html).group(1).strip() if TITLE_RE.search(html) else None)
    description = metas.get("og:description") or metas.get("description")
    image = metas.get("og:image")
    published = metas.get("article:published_time")
    modified = metas.get("article:modified_time")

    slug = index_html.parent.name
    url = canonical or f"{SITE_ORIGIN}/{slug}/"

    if not title or not image:
        return None

    return {
        "slug": slug,
        "url": url,
        "title": unescape(title),
        "description": unescape(description or ""),
        "image": image,
        "published": published,
        "modified": modified,
        "category": categorize(slug),
    }


def scan_articles() -> list:
    """Walk the repo root for <slug>/index.html pages that carry article metadata."""
    articles = []
    for child in sorted(REPO_ROOT.iterdir()):
        if not child.is_dir() or child.name.startswith(".") or child.name in NON_ARTICLE_DIRS:
            continue
        idx = child / "index.html"
        if not idx.exists():
            continue
        a = parse_article(idx)
        if a:
            articles.append(a)
    return articles


def pick_article(articles: list, history: dict):
    """Pick the best unposted article. Rotate categories, avoid 90-day repeats."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=REPOST_COOLDOWN_DAYS)
    recent_slugs = set()
    recent_categories = []
    for post in history.get("posts", []):
        try:
            posted_at = datetime.fromisoformat(post["posted_at"].replace("Z", "+00:00"))
        except (KeyError, ValueError):
            continue
        if posted_at >= cutoff:
            recent_slugs.add(post.get("slug"))
        recent_categories.append(post.get("category"))

    # Most recently posted categories (last 4) — avoid if possible.
    recent_cats_set = set(recent_categories[-4:])
    eligible = [a for a in articles if a["slug"] not in recent_slugs]
    if not eligible:
        log("All articles posted within 90 days; resetting and picking any.")
        eligible = articles[:]

    fresh_cat = [a for a in eligible if a["category"] not in recent_cats_set]
    pool = fresh_cat or eligible

    # Prefer articles that have never been posted over ones we're re-posting after cooldown.
    never_posted = [a for a in pool if a["slug"] not in {p.get("slug") for p in history.get("posts", [])}]
    chosen_pool = never_posted or pool

    random.seed(datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    return random.choice(chosen_pool)


# --- caption generation ---------------------------------------------------

CAPTION_PROMPT = """You write social copy for Barranquilla.Guide, the English-language city guide for Barranquilla, Colombia.

Write Facebook and Instagram captions for this article.

Article:
- Title: {title}
- URL: {url}
- Category: {category}
- Description: {description}

Rules:
- Facebook: 1–2 short sentences, friendly and curious, include the URL at the end, no hashtags.
- Instagram: 1–3 short sentences, evocative, include a soft CTA like "Link in bio" (do NOT paste the URL), end with a line of 8–12 relevant hashtags separated by spaces. Mix broad (#Barranquilla #Colombia #VisitColombia) with specific ones based on the topic.
- NO emojis anywhere in either caption.
- Evergreen phrasing only — prefer "typically runs in October" over "October 2026". Do not mention the current year unless the article title already does.
- Use American English.
- Do NOT invent facts beyond the description.

Return STRICT JSON only, no prose around it:
{{
  "facebook": "...",
  "instagram": "..."
}}"""


def generate_captions(client: Anthropic, article: dict) -> dict:
    prompt = CAPTION_PROMPT.format(
        title=article["title"],
        url=article["url"],
        category=article["category"],
        description=article["description"] or "(no description)",
    )
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(block.text for block in resp.content if getattr(block, "type", None) == "text").strip()
    # Strip code fences if present.
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.M).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Claude returned non-JSON: {text[:300]}") from e
    if not data.get("facebook") or not data.get("instagram"):
        raise RuntimeError(f"Missing caption fields: {data}")
    return data


# --- publishers -----------------------------------------------------------

GRAPH_VERSION = "v21.0"


def post_facebook(page_id: str, token: str, image_url: str, caption: str) -> dict:
    """Post a photo with caption to the FB Page. Returns API response."""
    endpoint = f"https://graph.facebook.com/{GRAPH_VERSION}/{page_id}/photos"
    r = requests.post(
        endpoint,
        data={"url": image_url, "caption": caption, "access_token": token},
        timeout=60,
    )
    if not r.ok:
        raise RuntimeError(f"FB publish failed {r.status_code}: {r.text}")
    return r.json()


def post_instagram(ig_user_id: str, token: str, image_url: str, caption: str) -> dict:
    """Two-step IG publish: create container, then publish it."""
    base = f"https://graph.facebook.com/{GRAPH_VERSION}/{ig_user_id}"

    create = requests.post(
        f"{base}/media",
        data={"image_url": image_url, "caption": caption, "access_token": token},
        timeout=60,
    )
    if not create.ok:
        raise RuntimeError(f"IG container create failed {create.status_code}: {create.text}")
    container_id = create.json().get("id")
    if not container_id:
        raise RuntimeError(f"IG container missing id: {create.text}")

    # Wait briefly for container to be READY.
    for _ in range(10):
        time.sleep(3)
        status = requests.get(
            f"https://graph.facebook.com/{GRAPH_VERSION}/{container_id}",
            params={"fields": "status_code", "access_token": token},
            timeout=30,
        )
        if status.ok and status.json().get("status_code") == "FINISHED":
            break

    publish = requests.post(
        f"{base}/media_publish",
        data={"creation_id": container_id, "access_token": token},
        timeout=60,
    )
    if not publish.ok:
        raise RuntimeError(f"IG publish failed {publish.status_code}: {publish.text}")
    return publish.json()


# --- main -----------------------------------------------------------------

def require_env(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        raise SystemExit(f"ERROR: missing required env var {name}")
    return val


def main() -> int:
    anthropic_key = require_env("ANTHROPIC_API_KEY")
    fb_page_id    = require_env("FB_PAGE_ID")
    fb_token      = require_env("FB_PAGE_TOKEN")
    ig_user_id    = require_env("IG_USER_ID")
    ig_token      = os.environ.get("IG_TOKEN", "").strip() or fb_token  # usually same long-lived page token

    log(f"Scanning articles in {REPO_ROOT}")
    articles = scan_articles()
    log(f"Found {len(articles)} articles")
    if not articles:
        log("ERROR: no articles found")
        return 1

    history = load_history()
    article = pick_article(articles, history)
    log(f"Picked: [{article['category']}] {article['title']}")
    log(f"  URL: {article['url']}")
    log(f"  Image: {article['image']}")

    client = Anthropic(api_key=anthropic_key)
    captions = generate_captions(client, article)
    log(f"Generated captions (FB {len(captions['facebook'])} chars, IG {len(captions['instagram'])} chars)")

    fb_result = post_facebook(fb_page_id, fb_token, article["image"], captions["facebook"])
    log(f"✅ Facebook Page: published (id={fb_result.get('post_id') or fb_result.get('id')})")

    ig_result = post_instagram(ig_user_id, ig_token, article["image"], captions["instagram"])
    log(f"✅ Instagram: published (id={ig_result.get('id')})")

    history.setdefault("posts", []).append({
        "slug": article["slug"],
        "url": article["url"],
        "category": article["category"],
        "posted_at": datetime.now(timezone.utc).isoformat(),
        "fb_id": fb_result.get("post_id") or fb_result.get("id"),
        "ig_id": ig_result.get("id"),
        "captions": captions,
    })
    save_history(history)
    log(f"History updated: {HISTORY_PATH}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        log(f"FATAL: {e}")
        sys.exit(1)
