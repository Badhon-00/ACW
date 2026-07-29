---
name: product-branding-video
description: Turn a product (a few UI screenshots/mockups plus a one-line value proposition) into a 60-second vertical brand promo video, end to end and fully local, with no video editor. Use when someone wants a product promo video, brand video, launch teaser, or vertical short from their app's UI, or wants to rebrand an existing product demo and re-export it.
---

# Product Branding Video

Produce a 60-second, 1080×1920 vertical promo video for a software/SaaS product from just its UI screenshots and a one-line pitch — script, animated UI, real-person B-roll, captions, voiceover, and music — assembled locally with `ffmpeg` and a headless browser. No timeline editor required.

The guiding idea: product demos are bought on *credibility*. Rather than motion-tweening static PNGs, the product's UI is reproduced as a small interactive HTML prototype that genuinely animates, so the footage looks like the real app in use.

## When to Use This Skill

- "Make a promo/launch video for my product from these UI screenshots."
- "Turn this app mockup into a 60-second vertical short for social."
- "Rebrand this existing demo video with a new name/logo and re-export."
- Trust-heavy B2B / medical / SaaS products where a believable, on-brand demo matters.

## What This Skill Does

1. **Script** — a 60s six-segment structure: real-person painpoints → product "登场"/reveal → 2–3 capability "hero shots" → a trust close-up (compliance/security). Each segment gets one caption line focused on a felt benefit.
2. **UI prototype** — reproduces the product's real design language as a single-file HTML page per screen with a `?rec=1` recording mode (1080×1920 stage) and hero animations exposed as `window.fn()` (ask→answer, long-press→auto-generate, number rolls, progress fills).
3. **Real-person B-roll** — generates believable painpoint footage via image + image-to-video models (portrait → subtle motion), vertical, with no readable brand logos/text.
4. **Screen recording** — records each UI segment to video with a headless browser and renders each caption as a transparent PNG (works even when ffmpeg lacks `drawtext`/`libass`).
5. **Assembly** — trims each segment (probing frames to find where animations actually complete), overlays captions, normalizes to 1080×1920/30fps, and concatenates with `ffmpeg`.
6. **Audio** — synthesizes a per-segment voiceover (TTS), aligns it to segment starts, and mixes a background track (ducked, with fades).
7. **Delivery** — hands off the finished MP4 (e.g. as a playable chat message), plus a cover frame.

## Prerequisites

`ffmpeg` (with libx264), Node with a headless browser (Playwright or system Chrome), and API keys for the image/video and TTS providers you use — all read from environment variables, never hardcoded.

## Gotchas worth knowing

- Many `ffmpeg` builds lack `drawtext`/`subtitles` — render captions as transparent PNGs from HTML and overlay them (also looks better).
- Headless-record video duration metadata can be inflated; pick trim points by probing frames, not by the millisecond timings you set in code.
- Overlay a caption PNG as a looped input (`-loop 1 -t`), or a single still won't fill the segment.
- On fast-cut montages, use one continuous voiceover line for the whole section — per-clip lines overlap into mush.
- Desensitize everything that enters a model or the final cut: real names, competitor model numbers, prices → fictional values; watermark the film.

## Full implementation

Working script templates (image/video generation, headless capture, ffmpeg assembly, TTS, voiceover+BGM mux), reference docs, and a hard-won gotchas write-up live in the canonical repo:

**https://github.com/X-RayLuan/awesome-ceo-stack/tree/main/ceo-skill/Openclaw-Product-Branding-Skill**

MIT licensed.
