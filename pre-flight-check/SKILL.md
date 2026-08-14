---
name: pre-flight-check
description: A mandatory quality gate your agent runs before it calls any work done — truth checks, copy review, link verification, breakpoint-by-breakpoint visual verification, and an honest delivery report. Use before delivering, shipping, deploying, or presenting any artifact as finished.
---

# Pre-Flight Check

Run every gate in order before delivering anything. A failing gate stops delivery — fix it or flag it, never ship past it. Full version with reference scripts lives at [MyAiFreedomSystems/pre-flight-check](https://github.com/MyAiFreedomSystems/pre-flight-check).

## When to Use This Skill

- Before telling the user any artifact is done: a website, page, image, document, or generated file
- Before deploying, publishing, or pushing work the user will see
- Whenever the user asks for a review, a QA pass, or a pre-launch check
- After any fix that claims to resolve a visual or content defect

## What This Skill Does

1. **Truth check**: Traces every name, quote, number, and factual claim to a real source from the current session. Anything that does not trace gets deleted or flagged — never patched over with invention. Blocks unauthorized hype ("free forever", "live now") and unapproved license claims.
2. **Copy pass**: Requires direct-response, human phrasing in headlines AND body copy, and Title Case for product names.
3. **Visual verification**: Screenshots rendered pages at desktop width, true phone width, the owner's actual window width, one width inside every gap between CSS breakpoints, and one pixel either side of each breakpoint. Verifies overlaps with geometry (`getBoundingClientRect()` intersection tests), not eyes. Takes two screenshots 2–3 seconds apart before judging, because occluded tabs freeze CSS animations mid-transition.
4. **Links and claims**: Fetches every href and matches every count in the copy against reality.
5. **Versioning**: Snapshots iterated projects to `versions/vN/` before changes, adds a CHANGELOG entry and bumps visible version footers after.
6. **Review team**: Dispatches a reviewer subagent with measurable acceptance criteria — exact viewport widths, element lists that must not overlap, pixel tolerances, required evidence — not "look it over."
7. **Delivery honesty**: The final report states what was done, what was verified and how, what failed, and what remains unverified.

## How to Use

### Basic Usage

```
Run a pre-flight check on this page before you show it to me.
```

```
This isn't done until it passes pre-flight.
```

### Advanced Usage

```
Add pre-flight-check to your standing rules: no delivery without it,
and include the measured evidence (widths tested, overlap results,
link statuses) in your final reply.
```

## Example

**User**: "Is the landing page ready to publish?"

**Output**:

```
Gate 1 Truth: PASS — 14 claims traced, 0 invented.
Gate 2 Copy: PASS — headline rewritten from "Live Now!" to the actual offer.
Gate 3 Visual: FAIL — at 690px the hero robot overlaps the sub-headline
  (rect intersection 38px). Fixed by un-pinning the robot at the same
  breakpoint where the stage stacks (720px, not 640px). Re-shot 8 widths:
  390, 640, 641, 690, 719, 720, 721, 1440 — clean at all.
Gate 4 Links: PASS — 22/22 hrefs return 200.
Verdict: SHIP. Evidence: /tmp/qa-*.png, geometry log attached.
```

**Credit:** Built from AI Freedom Systems' daily client-work workflow, after one too many "done" deliveries that were not done.

## Tips

- A page that passes at 390px and 1440px can still be broken at 690px. Mid-width bands between breakpoints are where absolute-positioned elements collide with stacked layouts — always test one width inside every gap.
- Never declare an element missing from a single screenshot; occluded tabs freeze frames.
- A review without measurable criteria is an opinion, not a gate.
- Invented example material (fake testimonials, demo people) is allowed only when openly labeled as invented on every surface where it appears.

## Common Use Cases

- Final QA pass on a generated website before the owner sees it
- Pre-publish check on a GitHub Pages / static site deploy
- Reviewing marketing copy for hype, AI-isms, and unearned claims
- Regression check after a responsive-layout bug fix
- Standing house rule for any agent that produces client-facing work
