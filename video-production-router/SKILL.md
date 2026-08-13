---
name: video-production-router
description: Classify and lock a video request as AI generation, designed composition, supplied-footage editing, or a mixed end-to-end workflow before production begins.
---

# Video Production Router

Choose the dominant production line before writing, generating, editing, or rendering media. Use this workflow for a real video brief so later work preserves a clear production promise.

## Gather the brief

Capture the topic, target audience, platform, duration, language, aspect ratio, supplied media, required visible copy, and delivery format. Ask only for missing facts that would change the route.

Classify every supplied reference as `reproduce` (match its content or structure), `edit` (change that source within an explicit preservation boundary), or `guide` (use only for style, pacing, or direction).

## Pick one primary line

- **Generate**: new photoreal, cinematic, talking-head, or other model-generated footage is the dominant object.
- **Compose**: designed HTML/SVG scenes, explainers, kinetic type, charts, captions, title cards, overlays, or motion graphics dominate. This is the default for explainer and animation briefs.
- **Edit**: supplied footage must be selected, trimmed, reframed, cleaned, captioned, mixed, localized, or changed. Keep Edit primary even when a bounded semantic pixel edit needs a generation provider.
- **AUTO**: two or more lines must be woven into one deliverable, such as editing source footage, composing callouts, generating an opener, and mixing narration.

Do not choose AUTO merely because a simple primary line needs captions or a title overlay.

## Lock the route

State the selected primary line and why it dominates. Record supporting lines separately. Do not silently change the primary line later; explain new evidence and obtain confirmation before switching.

Map common aspect ratios to a target canvas: 16:9 → 1920×1080, 9:16 → 1080×1920, and 1:1 → 1080×1080.

## Return a production proposal

Provide the primary and supporting lines; reference-media relationship; audience, platform, duration, language, aspect ratio, and export target; timed outline or shot list; supplied assets and missing inputs; local tools and optional provider-backed operations; review gates; and final playback checks.

Confirm before destructive edits, overwrites, paid provider calls, or publishing. Treat model-backed image, video, or speech generation as optional and identify which operation needs the user's provider credentials.

## Example

**User:** “Turn this interview into a 45-second vertical clip, remove pauses, add captions and a short animated title.”

**Route:** Edit primary, Compose supporting. Preserve the interview as the source, cut it deterministically, then add the designed title and captions on a 1080×1920 canvas.

If production tools are unavailable, return the complete unexecuted package—assumptions, script, timed storyboard, exact on-screen copy and captions, visual/audio direction, rights-safe asset notes, export settings, and QA checklist—and clearly label it as planned rather than rendered.

**Source and inspiration:** [OrkasVideoStudio `video-router`](https://github.com/Orkas-AI/Orkas-VideoStudio/blob/7387d99d468e0cce22508854ba8bca04e79657e1/packages/skills/video-router/SKILL.md), adapted under the [MIT License](https://github.com/Orkas-AI/Orkas-VideoStudio/blob/7387d99d468e0cce22508854ba8bca04e79657e1/LICENSE).
