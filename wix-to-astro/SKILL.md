---
name: wix-to-astro
description: Migrate, rebuild, duplicate, or clone a website from Wix (or any page builder) into Astro on Cloudflare Workers — pixel-faithful, measured, and SEO-stronger than the original. Use this whenever the user wants to leave Wix, rebuild a builder-made site in code, match an existing page's look and feel exactly, extract real animations or interactivity from a live site, verify fidelity of a rebuild against an original, or plan a Wix-to-Astro cutover — even when they don't say "Wix" or "Astro", e.g. "rebuild our landing page so we can leave our page builder", "make the new page match the old one exactly, animations included", "move our site off Squarespace/Webflow into code". Also use it for any single phase alone: reconnaissance of a builder site, brand/design extraction, per-section rebuild, verification passes, or DNS/route cutover planning.
---

# Wix → Astro migration

Version 1.1 · 2026-08-09

> Distilled from two production migrations run with this exact method: engineeringleaders.io
> and elc-conference.io. The second rebuilt 51 URLs in one overnight run and landed Lighthouse
> 100/100/100 (performance / accessibility / best practices, mobile) with LCP under 800 ms —
> then the owner's morning review still found four fidelity gaps, which is why Step 4.8 exists.

Migrate a live Wix site into a code-owned Astro site on Cloudflare Workers, so faithfully that
the owner struggles to tell them apart — then beat the original on performance and SEO.

The core discipline: **code-first, not screenshot-first.** The primary source of truth is the
live page's rendered DOM + computed CSS — exact px, hex, font metrics, spacing — extracted per
section and rebuilt from those real values. Screenshots are a secondary sanity check. A
screenshot-diff approach tells you *that* something looks different, not *which property* is
wrong.

## Before starting

Read `references/setup.md` and confirm the required tools are installed (Node, wrangler, ffmpeg,
Python + fontTools/Pillow, a real-browser automation tool). Every phase below assumes they exist;
`setup.md` has one install line and one verify command per tool.

## Workflow

Each step below is a summary with a pointer. Load only the reference you are executing.

### 1. Reconnaissance — `references/playbook.md` Steps 1–2
Map every URL (sitemap.xml, don't assume "just a landing page"), inventory each page's sections /
interactive elements / fonts / colors / CMS-driven parts, and check the deploy target's hard
limits before choosing media quality (Cloudflare Workers rejects any static asset over 25 MiB).
The font trap: page builders ship huge unused font libraries — only `getComputedStyle` on real
rendered elements tells you what's actually painted; identify the real files by downloading them
and reading their name tables, never by grepping markup.

### 2. Scaffold — `references/playbook.md` Step 3
Reuse an existing Astro + Wrangler config if one exists; otherwise scaffold Astro 5+ with the
Cloudflare adapter. Deploy to a **staging URL (workers.dev) first** — never point new infra at a
live domain's routes until an explicit, separately-approved cutover. Set the staging host
`noindex` from the first deploy (`references/seo.md` — the static-build `_headers` trap).

### 3. Per-section, code-first rebuild loop — `references/playbook.md` Step 4
Extract the live DOM + computed CSS per section, rebuild from those exact values, glance-check
with a screenshot, log every delta. On a second or later page, check for reused sections FIRST
and extract shared components instead of duplicating. Once the loop is proven on one section by
hand, parallelize independent sections across subagents (Step 6.5 has the safety rules: hard
per-agent file scopes, own browser context per agent, verify against static build output).

### 4. Verification — four distinct passes, budget for all four
These catch non-overlapping error classes; skipping one ships its whole class:
- **Side-by-side scroll-through** (Step 4.5) — gaps *between* sections, over-narrow queries.
- **Typography audit** (Step 4.6) — all six computed text properties per role, not just
  size + family.
- **Interactivity extraction** (Step 5 + `references/interactivity.md`) — real animations via
  `document.getAnimations()`, never attribute-counting; parallax checked separately (it doesn't
  use the Animation API); the button interaction baseline.
- **Tweaking round** (Step 4.8) — after content + visual passes, a sequential section-by-section
  sweep at source level: content↔visual correspondence, positioning re-measured against recon
  (rendered boxes win over recon tables), ALL background media including videos, and per-element
  scroll/interactive effects against the original's source.

### 5. Owner review — `references/playbook.md` Step 4.7
Even four automated passes miss a class of gap only the owner's eyes catch. Step 4.7 lists the
recurring patterns (stretched media frames, pills built as circles, missed `<img>` background
layers, flattened carousels, undercounted CTA rows…). When the owner flags something, verify with
real data before changing code; when a claim doesn't hold up under measurement, show the evidence
— but on perception calls (e.g. "add parallax"), the owner's perception decides
(`references/interactivity.md`).

### 6. SEO + AI SEO — `references/seo.md`
Make the rebuild *outperform* the Wix original, not just match it: production canonicals from day
one, staging noindex that survives a static build (headers, not middleware, on static builds), a 5-type
schema cap, sitemap hygiene, a tiered robots.txt that allows AI retrieval bots, crawler-delivery
verification with curl, and a Lighthouse mobile ≥95 gate. No keyword research required — this is
structural SEO, not content strategy.

### 7. Cutover — `references/playbook.md` "Cutover considerations"
Redirect map from a programmatic slug diff, route-specificity verification with curl (not
assumption), staged + reversible route change, old platform kept live and paid through a soak
period. Indexing pings only AFTER production returns 200 + indexable to bots.

## Principles that cut across every step

- **Don't invent values.** Every color, font, spacing, copy string, and animation timing traces
  to something measured on the live site. If a value can't be recovered, ask the owner — never
  ship a guess. That includes copy: migrate typos verbatim and flag them; fixing content is the
  owner's call, not the migration's.
- **A "no evidence found" result deserves the same scrutiny as a positive one.** An empty query
  result means "doesn't exist" or "my query was too narrow" — indistinguishable until you widen
  the search or check by another method.
- **When a recon table and a rendered box disagree, the box wins.** Re-measure the built page in
  a real browser; CSS that encodes the right numbers does not guarantee rendering them.
- **Log corrections, not just successes.** Keep an append-only `BUILD-LOG.md` recording "first
  pass assumed X, measurement showed Y" — it turns the next correction into a lookup instead of a
  re-investigation, and stops later sessions from "fixing" verified-deliberate choices.
