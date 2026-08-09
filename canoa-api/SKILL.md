---
name: canoa-api
description: Use when researching ancient coins via the CANOA API.
version: 1.1.0
author: CANOA (canoanumis.org)
license: CC BY 4.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [numismatics, history, research, education, api, ancient-coins, canoa]
    homepage: https://canoanumis.org
    related_skills: [arxiv, open-access-papers]
---

# CANOA API — how to use (numismatics, history, education)

CANOA (https://canoanumis.org) is an open corpus of ancient world coinage: Greece, Rome, Persia, Carthage, Byzantium and more.
Scale: ~128,500 coin types, 540,000+ museum specimens, 9,833 hoards, 17,074 dies, 2,600+ mints.
Type data — ODbL (source numismatics.org); images belong to the holding museums (many allow non-commercial use only, with attribution). Before publishing results, check /LICENSES.md and the license of the specific collection.

## Site facts (2026-08-08)
- Accessibility: the site conforms to WCAG 2.2 AA (and WCAG 2.1 AA), EN 301 549 V3.2.1 and Section 508 (2017 Refresh) — automated audit with axe-core 4.10.2, 08.08.2026: 0 violations on all key pages, both themes; manual screen-reader testing (NVDA, VoiceOver) is planned. Declaration on the homepage (sidebar card «доступность»).
- Contacts: accessibility complaints (per US education accessibility standards, Section 504 / ADA) — accessibility@canoanumis.org; privacy — privacy@canoanumis.org; suggestions — info@canoanumis.org; general complaints — abuse@canoanumis.org.

## When to use
- Find coins by ruler, mint, denomination, metal, period, dataset
- Get the card of a specific coin type (legends, description, dating, metrology)
- Build lists/statistics for articles, lessons, reports, research papers
- Build maps of mints (GeoJSON)

## Endpoints (all — GET, JSON, no key)

| Endpoint | Returns |
|---|---|
| `/api/search?q=<text>` | autocomplete: rulers, mints, denominations, coins |
| `/api/coins` | coin list with filters (see below) |
| `/api/coins/<slug>/` | coin card (e.g. `/api/coins/ric-i-second-edition-nero-1/`) |
| `/api/coin/<id>/` | card by numeric id (+ `specimen_count`, `specimens_url`) |
| `/api/coins/<id>/specimens` | museum specimens with metrics: weight, diameter, axis, collection |
| `/api/coins?hoard_id=<id>` | coin types of a specific hoard |
| `/api/hoards` | hoards in a region — bbox: `lat_min/lat_max/lon_min/lon_max` (+ q, dataset, page, per_page) |
| `/api/hoards/<id>/` | hoard detail with its coin types (authority, mint, dates) |
| `/api/authorities` | full list of rulers/emperors with type counts (q, has_types, page/per_page) |
| `/api/authorities/<id>/` | ruler detail + his coin types (paged) |
| `/api/mints` | full list of mints with coordinates and type counts |
| `/api/regions` | regions/civilizations with type counts |
| `/api/dies` | coin dies (Republican Die Project); filters q, die_type |
| `/api/denominations`, `/api/materials` | full reference lists with type counts |
| `/api/stats` | catalog statistics (types, specimens, hoards, mints, authorities…) |
| `/api/filter-options?field=mint` | filter reference values (mint, authority, denomination, material) |
| `/api/mints.geojson` | mints as GeoJSON (filters: authority, denomination, material, dataset, q, has_coins) |
| `/llms.txt`, `/llms-full.txt` | documentation for LLM/agents |
| `/LICENSES.md` | per-collection licenses |

### /api/coins filters
- `q` — free text (AND tokens over label, catalog number, legends)
- `authority`, `denomination`, `material` — **URIs** from nomisma.org, e.g. `http://nomisma.org/id/nero`
- `mint` — **numeric id** (not slug! get it from `/api/filter-options?field=mint`)
- `dataset` — ocre, crro, pella, iris, sco, pco, bigr, agco, aod, lco, coi, cm, do_byzant, oscar, chre, chrr, coinhoards, iacb
- `has_image` — `1` (with photos only) / `0` (all)
- `date_from`, `date_to` — years: coins whose period overlaps the range (negative = BC)
- `sort` — name, -name, date, -date
- `page`, `per_page` — pagination (per_page max 100)
- `format=html` — the same list as plain HTML (for JS-free linking)

## Quick examples

```bash
# Coins of Nero struck in Rome (mint id 36):
curl "https://canoanumis.org/api/coins?authority=http://nomisma.org/id/nero&mint=36&per_page=100"

# Coins of Rome 54–68 AD (period):
curl "https://canoanumis.org/api/coins?date_from=54&date_to=68&mint=36"

# With photos only:
curl "https://canoanumis.org/api/coins?q=denarius&has_image=1&sort=date&per_page=50"

# Coin card:
curl "https://canoanumis.org/api/coins/ric-i-second-edition-nero-63/"

# Filter reference values (mint ids, ruler URIs):
curl "https://canoanumis.org/api/filter-options?field=mint"
curl "https://canoanumis.org/api/filter-options?field=authority"

# Autocomplete:
curl "https://canoanumis.org/api/search?q=trajan"

# Mints as GeoJSON (for maps):
curl "https://canoanumis.org/api/mints.geojson?has_coins=1"
```

## Recipes

### 1. For kids and schools (simple and visual)
- `/api/search?q=<name>` — find a ruler (type `ruler`, url leads to the catalog)
- `/api/coins?q=<name>&has_image=1&format=html` — a page with pictures, no programming needed
- Exercise: "find 5 coins of Nero with photos and give their catalog numbers"

### 2. For hobbyists: "gold of Rome in the 2nd century"
```python
import urllib.request, json
url = "https://canoanumis.org/api/coins?material=http://nomisma.org/id/av&date_from=96&date_to=192&per_page=100"
data = json.load(urllib.request.urlopen(url))
for c in data["results"]:
    print(c["ocre_id"], "|", c["label"], "|", c["mint"], "|", c["date_from"], "-", c["date_to"])
print("total:", data["count"])
```

### 3. For researchers: export to CSV
```python
import urllib.request, json, csv
def fetch(page):
    u = f"https://canoanumis.org/api/coins?authority=http://nomisma.org/id/nero&per_page=100&page={page}"
    return json.load(urllib.request.urlopen(u))
first = fetch(1)
with open("nero_coins.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ocre_id", "label", "mint", "date_from", "date_to", "url"])
    for page in range(1, first["num_pages"] + 1):
        for c in fetch(page)["results"]:
            w.writerow([c["ocre_id"], c["label"], c["mint"], c["date_from"], c["date_to"], c["url"]])
print("exported:", first["count"])
```
- Negative `date_from/date_to` = years BC (e.g. -27 = 27 BC)
- `label_ru` fields in responses — Russian labels (material/denomination/ruler) for Russian-language publications

### 4. Research: hoards of a region
```python
import urllib.request, json
API = "https://canoanumis.org"
# 1. hoards of Sicily (bbox)
lst = json.load(urllib.request.urlopen(
    API + "/api/hoards?lat_min=36.5&lat_max=38.5&lon_min=12&lon_max=16"))
print("hoards:", lst["count"])
# 2. per hoard: coin types (authority, mint, dates) — pause 0.3 s between calls
d = json.load(urllib.request.urlopen(API + "/api/hoards/" + str(lst["results"][0]["id"]) + "/"))
for ct in d["coin_types"][:5]:
    print(ct["label"], "|", ct["authority"], "|", ct["mint"], "|", ct["date_from"], "-", ct["date_to"])
```
For the whole region iterate hoard details and aggregate by `authority` /
`mint` / period (`date_from`). Note: Hellenistic hoards mostly have `authority:
null` (civic issues) — aggregate by `mint` in that case. For the full pipeline
(aggregation → charts → PDF article) use the canoa-hoard-analysis skill.

### 5. Research: metrology (weights of a type)
```python
import urllib.request, json, statistics
d = json.load(urllib.request.urlopen(
    "https://canoanumis.org/api/coins/168481/specimens?per_page=100"))
w = [s["weight"] for s in d["results"] if s["weight"]]
print("specimens:", d["count"], "| mean weight:",
      round(statistics.mean(w), 2) if w else "-", "g | n with weight:", len(w))
```
`/api/coins/<id>/specimens` gives weight/diameter/axis per museum specimen —
enough for metrological analysis. `/api/stats` gives catalog totals for the
article header ("the catalog contains 128,862 types and 540,692 specimens").

### 6. Citation and licenses (required for publications)
- Types/data: ODbL 1.0 — credit CANOA (canoanumis.org) and numismatics.org
- Images: © holding museum, collection license in /LICENSES.md (many are NC — non-commercial only)
- Standard attribution: "Data: CANOA (canoanumis.org), ODbL; image: © <museum>"

## Pitfalls
- `mint` filter takes a numeric id, not a slug (slug only in /mints/<slug>/ URLs)
- `authority/denomination/material` — full nomisma.org URIs, not short names
- per_page max 100 — iterate pages for full dumps (num_pages in the response)
- Images: the API returns `image` / `obverse_image` / `reverse_image` only for files that actually exist. For lost sources (Gallica, PAS) the fields are empty strings — do not fetch dead URLs (404s pollute your crawl)
- Banners (for third-party sites): `/banner/<slug>/` (preview + HTML/Markdown/BB-code embed codes) and PNG files `/banner/<slug>/<WxH>.png` / `<WxH>-light.png` (sizes 970x90, 728x90, 468x60, 320x100, 320x50; dark/light themes; `Cache-Control: max-age=86400`). Banner pages are not in the sitemap — do not index them
- CANOA Edu (/edu/): school section with LTI 1.3 assignments (Canvas/Schoology/Moodle). PUBLIC and indexable: /edu/, /edu/how-it-works/, /edu/demo/, /edu/legal/privacy/. CLOSED to automated access (anti-cheating; only via an LTI session from an LMS — never crawl): /edu/assignment/*, /edu/my/, /edu/teacher/*, /edu/lti/*. LTI JWKS: /edu/.well-known/jwks.json. No student personal data is stored (opaque sub only); coin images are never copied by the Edu module
- Restricted collections (abc_exemplars, rutgers, ashm_ocre, ashm_pella) are not exposed via the API
- Be polite: pause between requests for large dumps
- /search/ is cached for 60 s — filter updates may lag briefly

## Verification
```bash
curl -s "https://canoanumis.org/api/search?q=nero" | head -c 400
curl -s "https://canoanumis.org/api/coins/ric-i-second-edition-nero-63/" | head -c 400
curl -s -o /dev/null -w "%{http_code}\n" "https://canoanumis.org/api/coins?per_page=1"
```
Expected: HTTP 200, valid JSON, `count` field in lists (to inspect the structure, save the response to a file and open it separately, without piping into an interpreter).
