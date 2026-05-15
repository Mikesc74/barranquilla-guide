#!/usr/bin/env python3
"""Re-fetch Google Fonts files from gstatic and write to /fonts/.
Run when the font selection changes. Updates fonts/google-fonts.css and
the woff2 files; you then re-run the @font-face generator (this script)
or manually paste new @font-face declarations into css/site.css.
"""
import re, urllib.request
from pathlib import Path

URL = 'https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Inter:wght@300;400;500;600&display=swap'
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'}

Path('fonts').mkdir(exist_ok=True)
req = urllib.request.Request(URL, headers=UA)
css = urllib.request.urlopen(req).read().decode()
Path('fonts/google-fonts.css').write_text(css)

blocks = re.split(r'/\\*\\s*([\\w\\-]+)\\s*\\*/', css)
for i in range(1, len(blocks), 2):
    subset = blocks[i].strip()
    if subset not in ('latin', 'latin-ext'): continue
    chunk = blocks[i+1] if i+1 < len(blocks) else ''
    for m in re.finditer(r'@font-face\\s*\\{([^}]+)\\}', chunk):
        body = m.group(1)
        fam = re.search(r"font-family:\\s*'([^']+)'", body)
        wt  = re.search(r'font-weight:\\s*(\\d+)', body)
        st  = re.search(r'font-style:\\s*(\\w+)', body)
        url = re.search(r"url\\(([^)]+)\\)", body)
        if not (fam and wt and url): continue
        fam_slug = fam.group(1).lower().replace(' ', '-')
        style_suffix = '-italic' if (st and st.group(1) == 'italic') else ''
        out = Path('fonts') / f'{fam_slug}-{wt.group(1)}{style_suffix}-{subset}.woff2'
        if out.exists(): continue
        req = urllib.request.Request(url.group(1), headers=UA)
        out.write_bytes(urllib.request.urlopen(req).read())
        print(f'  fetched {out.name}')
