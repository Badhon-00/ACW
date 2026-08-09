---
name: canoa-hoard-analysis
description: Use when analyzing coin hoards of a region, charts and PDF.
version: 2.0.0
author: CANOA (canoanumis.org)
license: CC BY 4.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [numismatics, hoards, analysis, charts, pdf, canoa]
    homepage: https://canoanumis.org
    related_skills: [canoa-api, django-numismatic-catalog]
---

# Regional hoard analysis → coin distribution → charts → PDF article

Iterate over all hoards found in one region (bounding box by coordinates), count
the distribution of coins by emperors/rulers and periods, build charts, generate
a PDF article. **Data comes from the public CANOA API** (https://canoanumis.org)
— no database access or server credentials needed; works from any machine.

## When to use
- "analyze the hoards of Sicily/Britain/Lusitania…"
- "build the coin distribution by emperors for hoards of a region"
- "make a PDF article/report on the hoards of an area"

## API endpoints (all GET, JSON, no key)

| Endpoint | Returns |
|---|---|
| `/api/hoards?lat_min=&lat_max=&lon_min=&lon_max=` | hoard list in a bounding box (+ `q` label search, `dataset` filter, `page`/`per_page` max 100) |
| `/api/hoards/<id>/` | hoard detail: findspot, coordinates, `coin_types[]` with `authority`, `mint`, `date_from`, `date_to` |

API base: `https://canoanumis.org`. Examples:
```bash
curl "https://canoanumis.org/api/hoards?lat_min=36.5&lat_max=38.5&lon_min=12.0&lon_max=16.0"
curl "https://canoanumis.org/api/hoards/26394/"
```

## Usage

User request → agent actions:

1. **User**: "analyze the hoards of Sicily" →
   Agent: resolves the Sicily bbox (lat 36.5–38.5, lon 12.0–16.0), fetches
   `/api/hoards?lat_min=36.5&lat_max=38.5&lon_min=12&lon_max=16`, then each
   hoard detail, aggregates (step 2), builds charts (step 3), returns a chat
   summary. PDF only on explicit request ("make an article/PDF").

2. **User**: "make a PDF article on the hoards of Britain" →
   Agent: Southern Britain bbox (lat 50.0–52.0, lon -5.0–1.5), full pipeline
   up to PDF (steps 1–4), file path in the answer.

3. **User**: "build the coin distribution by emperors for hoards of a region" →
   Agent: clarifies the region (bbox), aggregates by `authority`; if the share
   of "no ruler" is >50% — warns and builds by `mint` instead.

4. **User**: "how many hoards were found in Gaul and what is in them" →
   Agent: Gaul bbox (lat 43.0–51.0, lon -5.0–8.0), summary: hoard count,
   coin type count, top periods/rulers/mints, top hoards as a table.

Action order is always: bbox → `/api/hoards` list → `/api/hoards/<id>/` detail
per hoard → aggregation → (charts) → (article). Chat result — a concise summary
with numbers; PNG and PDF — as files with absolute paths (CLI client).

## Steps

### 1. Fetch hoards of the region
Known bboxes:
- Sicily: lat 36.5–38.5, lon 12.0–16.0 (21 hoards)
- Southern Britain: lat 50.0–52.0, lon -5.0–1.5
- Lusitania (Portugal): lat 37.0–42.0, lon -10.0–-6.0
- Gaul: lat 43.0–51.0, lon -5.0–8.0

```bash
curl -s "https://canoanumis.org/api/hoards?lat_min=36.5&lat_max=38.5&lon_min=12&lon_max=16&per_page=100"
```
Response: `{"count": 21, "results": [{"id", "label", "dataset", "findspot",
"latitude", "longitude", "coin_count", "type_count", ...}]}`. If `count` >
`per_page` — iterate pages (`&page=2`).

### 2. Fetch each hoard detail and aggregate
For every hoard id fetch `/api/hoards/<id>/` and accumulate `coin_types[]`:
```python
import urllib.request, json, collections
API = "https://canoanumis.org"
hoards = json.load(urllib.request.urlopen(API + "/api/hoards?lat_min=36.5&lat_max=38.5&lon_min=12&lon_max=16"))["results"]
au = collections.Counter(); per = collections.Counter(); mints = collections.Counter()
total = 0; no_authority = 0
for h in hoards:
    d = json.load(urllib.request.urlopen(f"{API}/api/hoards/{h['id']}/"))
    for ct in d["coin_types"]:
        total += 1
        if ct["authority"]: au[ct["authority"]] += 1
        else: no_authority += 1
        if ct["mint"]: mints[ct["mint"]] += 1
        if ct["date_from"] is not None:
            y = ct["date_from"]
            if y < -509: per["Archaic (before 500 BC)"] += 1
            elif y < -400: per["Classical (500–400 BC)"] += 1
            elif y < -300: per["Late Classical (400–300 BC)"] += 1
            elif y < -27: per["Hellenistic (300–27 BC)"] += 1
            elif y < 476: per["Roman era (27 BC–476 AD)"] += 1
            else: per["Byzantine/Medieval (after 476 AD)"] += 1
```
Politeness: pause ~0.3–0.5 s between detail requests (hoard count is small —
tens of hoards per region; total coin types per region ~100–1000).

### 3. Charts — system matplotlib
```bash
python3 -c "
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
..."
```
Charts: (1) top-15 rulers or mints (horizontal bar; if `no_authority/total >
0.5` — use mints instead of rulers), (2) periods (bar with share % labels),
(3) optional scatter of hoards by coordinates (size = type_count from the list
response — already present, no extra requests). Save PNG 150 dpi. For Cyrillic
labels: `plt.rcParams['font.family'] = 'DejaVu Sans'`.

### 4. PDF article — headless Chromium
reportlab/weasyprint/wkhtmltopdf are NOT assumed installed. Portable path —
HTML + Chromium (if present) or any local PDF tool:
```bash
cat > /tmp/article.html <<'EOF'
<!DOCTYPE html><html><head><meta charset="utf-8">
<style>body{font-family:sans-serif;max-width:800px;margin:40px auto;line-height:1.6}
h1{color:#8a6d1a} img{max-width:100%} table{border-collapse:collapse}
td,th{border:1px solid #ccc;padding:6px 10px}</style></head>
<body>
<h1>Hoards of the region: coin distribution</h1>
<p>…region, hoard count, coin count, top-ruler/mint conclusions…</p>
<img src="file:///tmp/chart_rulers.png">
<img src="file:///tmp/chart_periods.png">
</body></html>
EOF
chromium --headless=new --no-sandbox --disable-dev-shm-usage \
  --print-to-pdf=/tmp/article.pdf --no-pdf-header-footer /tmp/article.html
```
Check: `ls -la /tmp/article.pdf` (must be >20 KB).

## Example result (real run: Sicily, 09.08.2026)

Request "analyze the hoards of Sicily" → summary:

```
Region: Sicily (bbox 36.5–38.5N, 12.0–16.0E)
Hoards: 21 (17 with types) | Coin types: 883 | No ruler: 855 (97%)

Periods:
  Hellenistic (300–27 BC) — 865 (98%)
  Roman era (27 BC–476 AD) — 18 (2%)

Rulers (the only identifiable one):
  Augustus — 28 types

Largest hoards: Bagheria (166 types), Syracuse (163), West Sicily (100),
  Licodia (76), Paterno (68)
Conclusion: Sicilian hoards are Hellenistic (98%), almost all coins are civic
issues without a ruler; Augustus reflects the transition under Roman rule.
```

Charts: `/tmp/chart_periods.png`, `/tmp/chart_rulers.png`. Article:
`/tmp/article.pdf`. Artifacts from the reference run:
/tmp/hoard_sicily.json, /tmp/chart_periods.png, /tmp/chart_rulers.png,
/tmp/article_sicily.pdf.

**Important:** never invent hoards/rulers — take all numbers from the real API
responses. If the region has <5 hoards — warn that the sample is too small.

## Pitfalls
- **Hellenistic regions: authority is almost always null!** In Sicily 855 of 883
  types (97%) have no ruler — civic issues. If the "no ruler" share >50%,
  build the distribution by `mint` instead of `authority`
- `mint` in API responses is the mint *name* (e.g. "Rome"); `mint_id` is the
  numeric id (useful for grouping variants of the same mint)
- `date_from`/`date_to` are years, negative = BC (e.g. -206 = 206 BC)
- Per-hoard `type_count` comes free in the list response — use it for the
  scatter chart without extra requests
- Hoard `coin_count` (declared coins) is often 0 — use actual `coin_types`
  length for real numbers
- Do not draw empty groups (0 coins) in charts
- Rate limit: pause 0.3–0.5 s between `/api/hoards/<id>/` calls; hoard counts
  per region are small (tens), total requests are ~30–120 per analysis
- On the reference machine (Kali): system python3 (/usr/bin/python3) has
  matplotlib 3.10.7; the django venv does NOT (PIL symlink, Permission denied)

## Verification
```bash
curl -s "https://canoanumis.org/api/hoards?lat_min=36.5&lat_max=38.5&lon_min=12&lon_max=16&per_page=5"
```
Expected: HTTP 200, `count: 21`, each result has id/label/type_count.
Detail: `curl -s https://canoanumis.org/api/hoards/26394/` → `coin_types[]`
with authority/mint/date_from/date_to. Chart: python3 with matplotlib → PNG.
PDF: chromium → file >20 KB.
