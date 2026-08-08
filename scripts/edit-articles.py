#!/usr/bin/env python3
"""
Local, offline article text editor for the guide sites.

Run it from inside a repo (barranquilla-guide, medellin-guide, or
cartagena-guide):

    python3 scripts/edit-articles.py

Then open http://localhost:8765/ in your browser. It lists every article
on the site (anything with an .article-body block), and lets you edit the
text inside paragraphs, list items, headings, and blockquotes. Saving
writes straight back to the HTML file on disk, byte-exact except for the
block(s) you changed, no reformatting of the rest of the file.

No dependencies beyond the Python standard library. No network calls.
Nothing leaves your machine. Once you're happy with the changes:

    git add -A
    git commit -m "edit copy"
    git push

Cloudflare Pages auto-deploys ~30 seconds after the push.

Notes:
- This only edits TEXT inside .article-body. It won't touch nav, footer,
  head meta, or anything outside that block.
- Each box holds the raw HTML of one block (a <p>, <li>, <h2>, etc). If a
  block has inline tags like <strong> or <a> in it, keep those tags intact
  when you edit, just change the wording around them.
- Don't add or remove H2/H3 elements here, and don't delete an id="..."
  attribute on a heading, those anchors are relied on elsewhere (TOC,
  sitemap references, external links).
"""
import argparse
import html
import re
import http.server
import socketserver
import urllib.parse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

BLOCK_TAGS = ["h1", "h2", "h3", "h4", "p", "li", "blockquote", "dt", "dd", "td", "th"]


def find_article_files():
    files = []
    for p in REPO_ROOT.rglob("*.html"):
        if ".git" in p.parts:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if 'class="article-body"' in text or "class='article-body'" in text:
            files.append(p)
    return sorted(files)


def get_title(text):
    m = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S)
    if m:
        return re.sub("<[^>]+>", "", m.group(1)).strip()
    m = re.search(r"<title>(.*?)</title>", text, re.S)
    if m:
        return m.group(1).strip()
    return "(untitled)"


def find_article_body_spans(text):
    """Return a list of (start, end) character offsets, one per
    .article-body block on the page. Some pages (barranquilla/cartagena
    bilingual template) have TWO sibling .article-body divs, one per
    language, not one combined block. Matches div depth per span so
    nested divs don't truncate it early."""
    spans = []
    tag_re = re.compile(r"<(/?)div\b[^>]*>")
    search_from = 0
    for m in re.finditer(r'<div class="article-body"[^>]*>', text):
        if m.start() < search_from:
            continue  # inside a span we already captured
        start = m.end()
        depth = 1
        end = len(text)
        for tm in tag_re.finditer(text, start):
            depth += 1 if tm.group(1) == "" else -1
            if depth == 0:
                end = tm.start()
                break
        spans.append((start, end))
        search_from = end
    return spans


def extract_blocks(text):
    spans = find_article_body_spans(text)
    blocks = []
    tag_pattern = "|".join(BLOCK_TAGS)
    regex = re.compile(rf"<({tag_pattern})\b[^>]*>.*?</\1>", re.S | re.I)
    for body_start, body_end in spans:
        body = text[body_start:body_end]
        for m in regex.finditer(body):
            blocks.append(
                {
                    "tag": m.group(1).lower(),
                    "start": body_start + m.start(),
                    "end": body_start + m.end(),
                    "original": m.group(0),
                }
            )
    blocks.sort(key=lambda b: b["start"])
    return blocks


def preview_text(html_snippet, length=80):
    t = re.sub("<[^>]+>", "", html_snippet).strip()
    t = html.unescape(t)
    return (t[:length] + "...") if len(t) > length else (t or "(empty)")


PAGE_CSS = """
body{font-family:-apple-system,Helvetica,Arial,sans-serif;max-width:900px;margin:40px auto;padding:0 20px;color:#222;line-height:1.5}
h1{font-size:20px}
.block{margin-bottom:16px;border:1px solid #ddd;border-radius:6px;padding:10px}
.block label{display:block;font-size:12px;color:#888;margin-bottom:6px}
.block label b{color:#E8533A;text-transform:uppercase;font-size:11px;letter-spacing:.03em}
textarea{width:100%;box-sizing:border-box;font-family:inherit;font-size:14px;padding:8px;border:1px solid #ccc;border-radius:4px;resize:vertical}
.list a{display:block;padding:10px 0;border-bottom:1px solid #eee;text-decoration:none;color:#1B2A47}
.list a span{color:#999;font-size:12px}
button{background:#E8533A;color:white;border:none;padding:10px 18px;border-radius:4px;font-size:14px;cursor:pointer}
.save-bar{position:sticky;bottom:0;background:white;padding:12px 0;border-top:1px solid #ddd}
.msg{padding:10px 14px;background:#e6f7e6;border:1px solid #b7e3b7;border-radius:4px;margin-bottom:14px}
.hint{color:#888;font-size:13px;margin-bottom:20px}
"""


class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, body, status=200, ctype="text/html; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        if parsed.path == "/":
            self.list_page()
        elif parsed.path == "/edit":
            self.edit_page(qs.get("f", [""])[0])
        else:
            self._send("Not found", 404)

    def list_page(self):
        files = find_article_files()
        rows = []
        for p in files:
            text = p.read_text(encoding="utf-8", errors="ignore")
            title = html.escape(get_title(text))
            rel = p.relative_to(REPO_ROOT).as_posix()
            rows.append(
                f'<a href="/edit?f={urllib.parse.quote(rel)}">{title} '
                f'<span>({rel})</span></a>'
            )
        body = (
            f"<html><head><meta charset='utf-8'><style>{PAGE_CSS}</style></head><body>"
            f"<h1>Articles ({len(files)})</h1>"
            f"<p class='hint'>Repo: {html.escape(str(REPO_ROOT))}</p>"
            f"<div class='list'>{''.join(rows)}</div></body></html>"
        )
        self._send(body)

    def edit_page(self, rel, message=""):
        p = (REPO_ROOT / rel).resolve()
        if REPO_ROOT not in p.parents or not p.exists():
            self._send("Invalid file", 400)
            return
        text = p.read_text(encoding="utf-8", errors="ignore")
        blocks = extract_blocks(text)
        title = html.escape(get_title(text))
        fields = []
        for i, b in enumerate(blocks):
            preview = html.escape(preview_text(b["original"]))
            ta_value = html.escape(b["original"])
            rows = max(2, b["original"].count("\n") + 2)
            fields.append(
                f"""
            <div class="block">
              <label><b>{b['tag']}</b> &middot; {preview}</label>
              <textarea name="block_{i}" rows="{rows}">{ta_value}</textarea>
              <input type="hidden" name="start_{i}" value="{b['start']}">
              <input type="hidden" name="end_{i}" value="{b['end']}">
            </div>"""
            )
        msg_html = f"<div class='msg'>{html.escape(message)}</div>" if message else ""
        body = f"""<html><head><meta charset='utf-8'><style>{PAGE_CSS}</style></head><body>
        <p><a href="/">&larr; all articles</a></p>
        <h1>{title}</h1>
        <p class="hint">{html.escape(rel)} &mdash; edit the text in the boxes below, then Save. Keep any
        &lt;a&gt;/&lt;strong&gt;/&lt;em&gt; tags intact if present, just change the wording around them.</p>
        {msg_html}
        <form method="POST" action="/save?f={urllib.parse.quote(rel)}">
          {''.join(fields)}
          <div class="save-bar"><button type="submit">Save to file</button></div>
        </form>
        </body></html>"""
        self._send(body)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        if parsed.path != "/save":
            self._send("Not found", 404)
            return
        rel = qs.get("f", [""])[0]
        p = (REPO_ROOT / rel).resolve()
        if REPO_ROOT not in p.parents or not p.exists():
            self._send("Invalid file", 400)
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8")
        form = urllib.parse.parse_qs(raw)

        text = p.read_text(encoding="utf-8", errors="ignore")
        edits = []
        i = 0
        while f"start_{i}" in form:
            start = int(form[f"start_{i}"][0])
            end = int(form[f"end_{i}"][0])
            new_val = form.get(f"block_{i}", [""])[0]
            edits.append((start, end, new_val))
            i += 1
        # Apply from the end of the file backward so earlier offsets stay valid.
        edits.sort(key=lambda e: e[0], reverse=True)
        changed = 0
        for start, end, new_val in edits:
            if text[start:end] != new_val:
                changed += 1
            text = text[:start] + new_val + text[end:]
        p.write_text(text, encoding="utf-8")

        self.edit_page(rel, message=f"Saved. {changed} block(s) changed.")

    def log_message(self, format, *args):
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    with socketserver.TCPServer(("127.0.0.1", args.port), Handler) as httpd:
        print(f"Article editor running at http://127.0.0.1:{args.port}/")
        print(f"Repo root: {REPO_ROOT}")
        print("Press Ctrl+C to stop.")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
