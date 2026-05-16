#!/usr/bin/env node
// rotate-hero.mjs — cycles the barranquilla.guide homepage hero image
// Commits the change via GitHub API (no local git credentials needed).
// Reads GitHub token from ~/code/.github-token

import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dir = dirname(fileURLToPath(import.meta.url));
const ROOT   = resolve(__dir, '..');
const OWNER  = 'Mikesc74';
const REPO   = 'barranquilla-guide';
const FILE   = 'index.html';
const BRANCH = 'main';

// Token file lives one level above the repo (~/code/.github-token)
const TOKEN  = readFileSync(resolve(ROOT, '../.github-token'), 'utf8').trim();

// ── Image pool ────────────────────────────────────────────────────────────────
// Sequential rotation. Add/remove filenames freely — script detects current
// image from the live HTML and picks the next one.
const IMAGES = [
  'carnival1.webp',
  'carnival-barranquilla-dancer-face-1920x700.webp',
  'gran-malecon-barranquilla-waterfront-1.webp',
  'parquealegra-1920x1080.webp',
  'magdalena-malecon-1536x864.webp',
  'estadio-edgar-renteria-1920x1213.webp',
  'negra-pulida-carnival-barranquilla-1400.webp',
];

// ── GitHub API helpers ────────────────────────────────────────────────────────
const API = `https://api.github.com/repos/${OWNER}/${REPO}/contents/${FILE}`;
const headers = {
  Authorization: `Bearer ${TOKEN}`,
  Accept: 'application/vnd.github+json',
  'User-Agent': 'hero-rotation-script',
};

async function getFile() {
  const res = await fetch(`${API}?ref=${BRANCH}`, { headers });
  if (!res.ok) throw new Error(`GitHub GET failed: ${res.status} ${await res.text()}`);
  return res.json(); // { content (base64), sha, ... }
}

async function putFile(sha, content, message) {
  const res = await fetch(API, {
    method: 'PUT',
    headers: { ...headers, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      content: Buffer.from(content).toString('base64'),
      sha,
      branch: BRANCH,
    }),
  });
  if (!res.ok) throw new Error(`GitHub PUT failed: ${res.status} ${await res.text()}`);
  return res.json();
}

// ── Main ──────────────────────────────────────────────────────────────────────
const { content: b64, sha } = await getFile();
let html = Buffer.from(b64, 'base64').toString('utf8');

// Detect current hero image from the div style
const currentMatch = html.match(/id="hero-bg" style="background-image: url\('\/img\/([^']+)'\)/);
const current = currentMatch?.[1] ?? IMAGES[0];

const currentIdx = IMAGES.indexOf(current);
const nextIdx    = (currentIdx + 1) % IMAGES.length;
const next       = IMAGES[nextIdx];
const imgPath    = `/img/${next}`;
const absUrl     = `https://barranquilla.guide/img/${next}`;

console.log(`Rotating: ${current} → ${next}`);

// Swap OG / Twitter meta
html = html.replace(
  /(<meta property="og:image" content=")[^"]*"/,
  `$1${absUrl}"`
);
html = html.replace(
  /(<meta property="og:image:secure_url" content=")[^"]*"/,
  `$1${absUrl}"`
);
html = html.replace(
  /(<meta name="twitter:image" content=")[^"]*"/,
  `$1${absUrl}"`
);

// Swap preload href
html = html.replace(
  /(<link rel="preload" as="image" href=")[^"]*"/,
  `$1${imgPath}"`
);

// Swap hero-image div style
html = html.replace(
  /(id="hero-bg" style="background-image: url\(')[^']*(')/,
  `$1${imgPath}$2`
);

await putFile(sha, html, `chore: rotate hero → ${next}`);
console.log('Done. Cloudflare Pages will redeploy in ~30s.');
