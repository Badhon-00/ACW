# SEO + AI SEO for a migrated site

The point of leaving Wix is not parity — it's advantage. A code-owned Astro site can beat the
builder original on every structural signal: paint speed, markup quality, schema, crawler
delivery. This file is the structural layer only; it deliberately involves **no keyword or query
research** — content strategy is a separate discipline.

Everything here is verifiable with curl or Lighthouse. Run the checks; don't assume.

## 1. Staging discipline: production canonicals + a noindex that actually delivers

Set `site` in `astro.config.mjs` to the FINAL production origin from day one, and build every
canonical/OG/sitemap URL from it. The markup then needs zero edits at cutover. Consequence: an
indexed staging copy would compete with the live original using its own canonical — so staging
must be provably unindexable:

- **On a fully static build, Astro middleware never runs for page requests** — Cloudflare's
  static-asset handler serves them and the Worker is not invoked. A middleware-based
  `X-Robots-Tag` silently does nothing. Put the header in `public/_headers` instead:
  ```
  /*
    X-Robots-Tag: noindex, nofollow
  ```
- Also ship a staging `public/robots.txt` with `Disallow: /`. Belt and braces: the header stops
  indexing, the robots stops crawling.
- Both are removed at cutover; removal is THE step that makes the site visible, so write it into
  the cutover checklist in capitals, with the verify command:
  `curl -sI https://<prod>/ | grep -i x-robots-tag` → must return nothing.
- Never submit staging URLs to any index or ping service. Indexing pings happen only after
  production returns 200 + indexable to bots.

## 2. Metadata

Per page: unique `<title>`, meta description, canonical (absolute, production origin), OG
(`og:type/site_name/title/description/url/image` + width/height 1200×630), Twitter
`summary_large_image`. Migrate the original's titles/descriptions verbatim where they exist —
inventing "better" ones mid-migration mixes two jobs. Where the original HAS no description,
assemble one from facts already on the page; never invent positioning copy.

Render the OG card from the site's real brand fonts with headless Chrome (an HTML file +
`--headless --screenshot`) rather than hand-drawing — it looks like the brand because it IS the
brand's CSS.

## 3. Structured data — a hard 5-type cap

One JSON-LD `@graph` per page containing at most: `Organization` (one, with `@id`, referenced by
the others — never restated per page), `WebPage`, `BreadcrumbList`, and where genuinely
applicable `Event` and/or `Person`. That's the whole list.

- **No `FAQPage`, no `HowTo`** — Google retired those rich results; a schema node describing
  content is now pure liability if the content isn't visible on the page.
- **Thin where the source is thin.** No published date → month-precision `startDate` or none. No
  price → no `offers`. A validator-pleasing invented date is a wrong answer served to every
  crawler and every AI engine.
- `Organization.logo` needs a real ≥112px logo image, not the OG card; render the wordmark on a
  background it survives (a cream logo vanishes on white).

## 4. Sitemap hygiene

- `@astrojs/sitemap` + a `filter` that excludes every noindex page. The generator crawls build
  output and knows nothing about your meta tags — a noindexed URL in the sitemap is a
  contradiction that gets the whole file distrusted.
- One sitemap per host. A sitemap may only list URLs on its own host.
- Post-action pages (thank-you, subscribed) are noindex AND filtered out.
- A sitemap URL must never redirect. Declare on whichever host the site canonicalizes to.

## 5. robots.txt — tiered, allow-by-default, and check who actually serves it

Production robots.txt names bots explicitly in tiers, all allowed: classic search (Googlebot,
Bingbot, regional engines your market needs), **AI retrieval bots** (OAI-SearchBot, ChatGPT-User,
Claude-SearchBot, Claude-User, PerplexityBot, Perplexity-User, Google-Extended…), AI training
bots (GPTBot, ClaudeBot, CCBot…), link unfurlers (facebookexternalhit, LinkedInBot, Slackbot…),
then `User-agent: *` + your genuine disallows (`/api/`, intake paths). Rationale: blocking AI
retrieval bots removes you from AI answers without stopping training; naming bots explicitly
makes a future block a deliberate one-line edit instead of a silent gap. Two traps:

- **Check which file actually serves the domain root.** A Worker route or another platform layer
  can shadow your repo's `public/robots.txt` — a repo edit is then a no-op. Verify with curl
  before AND after any change, never by reading the repo.
- `llms.txt` is referenced as a comment, never a `Sitemap:` line (it's markdown, not XML). Treat
  it as an optional agent-tooling surface, not a citation lever.

## 6. Crawler-delivery verification — the file is policy, the edge is law

A robots.txt that allows a bot means nothing if the edge (WAF, bot-fight mode, rate limits)
403/429s the actual fetch. After deploying to production, fetch the homepage + key deep URLs AS
each major bot and assert 200:

```bash
for UA in "Googlebot/2.1" "Bingbot/2.0" "GPTBot/1.0" "OAI-SearchBot/1.0" "ClaudeBot/1.0" "PerplexityBot/1.0"; do
  for P in / /key-page/; do
    printf "%-20s %-14s %s\n" "$UA" "$P" \
      "$(curl -s -o /dev/null -w '%{http_code}' -A "Mozilla/5.0 (compatible; $UA)" "https://<prod>$P")"
  done
done
```

Run it against staging before cutover and against production after — edge-level failures exist
that staging cannot reproduce.

## 7. Performance gates (this is where you beat Wix)

- **Lighthouse mobile ≥ 95 — treat as a gate, not a target.** A measured Astro rebuild of a Wix
  page routinely lands at 100/100/100 with LCP under 800 ms; Wix originals rarely clear 60.
- `build.inlineStylesheets: 'always'`; self-host the real font files (extracted in recon) with
  `font-display: swap` and preload the 1–2 above-the-fold faces.
- Build-time image optimization (sharp), NOT the adapter's runtime `/_image` route (it 404s on
  static Worker assets).
- **Never re-pipe an already-optimized asset through the image pipeline** — re-encoding a
  hand-tuned WebP can double its size. Serve those from `public/` with a cache rule.
- Media budget: every static asset under 25 MiB (Workers hard limit) and every video re-encoded
  (CRF ~28–31, `+faststart`, poster frame, `preload="none"` for anything heavy). Check whether a
  "silent" video actually has audio before stripping it.
- Verify weight after each build: `find dist -type f -size +400k` and justify every hit.

## 8. The scoreboard

Before cutover, capture for the report: Lighthouse (all four categories, mobile), LCP/CLS,
total page weight, and the same numbers for the live Wix original. The migration's pitch — to
the owner and to anyone reading the case study — is that delta.
