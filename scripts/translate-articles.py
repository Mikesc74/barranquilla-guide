#!/usr/bin/env python3
"""
Bilingualize article bodies via the Anthropic API.

For each article HTML file: extract <div class="article-body">...</div>,
plus the article-header h1/label and the page <title> / meta description,
translate to Spanish via Claude, then insert as a parallel data-lang="es"
sibling block. The existing CSS rule html.lang-es [data-lang="en"]{display:none}
handles visibility.

Idempotent: skips files that already have data-lang="es" on .article-body.

Prereq:
  pip install anthropic
  export ANTHROPIC_API_KEY=sk-ant-...

Usage:
  python3 scripts/translate-articles.py            # all files
  python3 scripts/translate-articles.py PATH ...   # specific files
  python3 scripts/translate-articles.py --dry-run  # show what would change
  python3 scripts/translate-articles.py --limit 3  # process N files then stop
"""

import os, re, sys, time, pathlib, argparse, html as html_mod
from anthropic import Anthropic

# Resolve repo root from this script's location: scripts/translate-articles.py -> repo root
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE_NAME = REPO_ROOT.name  # e.g. "barranquilla-guide"

# Model. Sonnet is recommended for translation quality; switch to Haiku for cost.
MODEL = "claude-sonnet-4-5"

# Translation system prompt. Voice / style rules from CLAUDE.md.
SYSTEM_PROMPT = """You translate Colombian travel and expat-guide articles from English into natural, Colombian Spanish for a paisa or costeño reader.

Rules:
- Preserve all HTML tags, attributes, image src/srcset, link href, and id attributes EXACTLY.
- Translate visible text only: paragraphs, headings, figcaptions, alt attributes, link anchor text, list items, callout body text.
- Do NOT translate: city/place names (Barranquilla, Cartagena, El Prado, etc.), person names (Mike, Santiago, Benkos Biohó, etc.), brand names (Cabify, Nequi, Sura, etc.), or technical terms with no good Spanish equivalent (cédula, palenque, champeta, Lengua, EPS).
- Voice: insider, direct, specific. Same tone as the English. No marketing-speak. Slightly literary where the original is.
- NO em dashes (— is banned house-wide). Use commas, periods, colons, parentheses, " · ".
- Numbers in COP stay COP. USD references stay USD.
- Keep "Catalina" untranslated (it's the AI guide's name).
- Return ONLY the translated HTML. No preamble, no commentary, no markdown fences."""


def translate(client: Anthropic, html_fragment: str, what: str) -> str:
    """Translate a single HTML fragment via Claude."""
    resp = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Translate this {what} into Colombian Spanish. Preserve every HTML attribute and structural element. Return only the translated HTML.\n\n{html_fragment}",
        }],
    )
    out = "".join(b.text for b in resp.content if hasattr(b, "text")).strip()
    # Strip accidental markdown fences if the model added them.
    if out.startswith("```"):
        out = re.sub(r"^```[a-zA-Z]*\n", "", out)
        out = re.sub(r"\n```$", "", out)
    return out.strip()


# ─── HTML surgery ─────────────────────────────────────────────────────────────

ARTICLE_BODY_RE = re.compile(
    r'(<div class="article-body">)(.*?)(</div>\s*<!--\s*\.article-body\s*-->)',
    re.DOTALL,
)
TITLE_RE = re.compile(r'<title>([^<]+)</title>')
META_DESC_RE = re.compile(r'<meta\s+([^>]*?)name="description"([^>]*)/?>', re.IGNORECASE)
H1_RE = re.compile(r'(<header class="article-header">.*?<h1>)([^<]+)(</h1>)', re.DOTALL)
LABEL_RE = re.compile(r'(<span class="label">)([^<]+)(</span>)')


def process_file(client: Anthropic, path: pathlib.Path, dry_run: bool) -> str:
    src = path.read_text(encoding="utf-8")

    # Idempotency: skip if a Spanish article-body sibling already exists.
    if 'class="article-body" data-lang="es"' in src or 'article-body" data-lang="es"' in src:
        return "skip:already-translated"

    # Find the article body. If missing, this isn't an article page.
    m = ARTICLE_BODY_RE.search(src)
    if not m:
        return "skip:no-article-body"

    open_tag, body, close_tag = m.group(1), m.group(2), m.group(3)

    # Skip extremely short bodies (probably stubs or index pages).
    if len(body.strip()) < 200:
        return "skip:body-too-short"

    if dry_run:
        return f"would-translate:{len(body)}b"

    # 1. Translate article body.
    try:
        body_es = translate(client, body, "article body fragment")
    except Exception as e:
        return f"error:body:{e}"

    # 2. Translate <title>.
    title_match = TITLE_RE.search(src)
    title_es = None
    if title_match and 'data-lang' not in src[title_match.start()-20:title_match.start()]:
        try:
            title_es = translate(client, title_match.group(1), "page title")
        except Exception as e:
            return f"error:title:{e}"

    # 3. Translate meta description.
    meta_match = META_DESC_RE.search(src)
    meta_desc_es = None
    if meta_match and 'data-lang' not in meta_match.group(0):
        # Extract content="..." from the existing tag.
        content_match = re.search(r'content="([^"]+)"', meta_match.group(0))
        if content_match:
            try:
                meta_desc_es = translate(client, content_match.group(1), "meta description")
            except Exception as e:
                return f"error:meta:{e}"

    # 4. Translate H1.
    h1_match = H1_RE.search(src)
    h1_es = None
    if h1_match:
        try:
            h1_es = translate(client, h1_match.group(2), "article H1 headline")
        except Exception as e:
            return f"error:h1:{e}"

    # 5. Translate label (e.g. "Things to Do" -> "Qué hacer"). Optional; many
    #    common labels are already in the chrome translation table from the
    #    earlier fan-out, but if the label sits inside .article-header it
    #    wasn't covered, so translate it.
    label_match = re.search(
        r'<header class="article-header">[^<]*<span class="label">([^<]+)</span>',
        src,
    )
    label_es = None
    if label_match:
        try:
            label_es = translate(client, label_match.group(1), "article category label")
        except Exception as e:
            return f"error:label:{e}"

    # ─── Apply edits ──────────────────────────────────────────────────────────
    new_src = src

    # Add data-lang="en" to the existing article-body opener, then append a
    # parallel data-lang="es" sibling block.
    new_open = '<div class="article-body" data-lang="en">'
    new_close = '</div><!-- .article-body -->'
    es_block = (
        f'\n\n<!-- Article Body (Spanish) -->\n'
        f'<div class="article-body" data-lang="es">\n{body_es}\n</div><!-- .article-body es -->'
    )
    new_src = new_src.replace(
        f'{open_tag}{body}{close_tag}',
        f'{new_open}{body}{new_close}{es_block}',
        1,
    )

    # Dupe <title>.
    if title_es and title_match:
        old_title = title_match.group(0)
        new_title = (
            f'<title data-lang="en">{title_match.group(1)}</title>\n'
            f'<title data-lang="es">{title_es}</title>'
        )
        new_src = new_src.replace(old_title, new_title, 1)

    # Dupe meta description.
    if meta_desc_es and meta_match:
        old_meta = meta_match.group(0)
        # Strip self-closing slash if present.
        en_meta = re.sub(
            r'<meta\s+',
            '<meta data-lang="en" ',
            old_meta.replace('name="description"', 'name="description"', 1),
            count=1,
        )
        es_meta = re.sub(
            r'content="[^"]+"',
            f'content="{html_mod.escape(meta_desc_es, quote=True)}"',
            en_meta.replace('data-lang="en"', 'data-lang="es"', 1),
        )
        new_src = new_src.replace(old_meta, f'{en_meta}\n{es_meta}', 1)

    # Wrap H1.
    if h1_es and h1_match:
        old_h1 = h1_match.group(0)
        new_h1 = (
            f'{h1_match.group(1)}<span class="pb-en">{h1_match.group(2)}</span>'
            f'<span class="pb-es">{h1_es}</span>{h1_match.group(3)}'
        )
        new_src = new_src.replace(old_h1, new_h1, 1)

    # Wrap label inside .article-header.
    if label_es and label_match:
        old_label = f'<span class="label">{label_match.group(1)}</span>'
        new_label = (
            f'<span class="label">'
            f'<span class="pb-en">{label_match.group(1)}</span>'
            f'<span class="pb-es">{label_es}</span>'
            f'</span>'
        )
        new_src = new_src.replace(old_label, new_label, 1)

    path.write_text(new_src, encoding="utf-8")
    return "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="Specific HTML files to translate (default: all)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    if args.files:
        files = [pathlib.Path(f).resolve() for f in args.files]
    else:
        files = sorted(REPO_ROOT.glob("**/*.html"))

    # Filter junk.
    files = [
        f for f in files
        if not any(p in {".git", "node_modules", "tools", "scripts"} for p in f.parts)
    ]

    client = Anthropic()

    ok = 0
    skip = 0
    err = 0
    for i, f in enumerate(files, 1):
        if args.limit and ok >= args.limit:
            break
        rel = f.relative_to(REPO_ROOT) if f.is_absolute() and REPO_ROOT in f.parents else f
        status = process_file(client, f, args.dry_run)
        if status == "ok":
            ok += 1
        elif status.startswith("skip"):
            skip += 1
        else:
            err += 1
        print(f"[{i}/{len(files)}] {status:<40} {rel}")
        # Gentle rate-limit pacing.
        if status == "ok" and not args.dry_run:
            time.sleep(0.3)

    print(f"\nDone. ok={ok} skip={skip} err={err}")


if __name__ == "__main__":
    main()
