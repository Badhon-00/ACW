# Interactivity extraction: method + how to verify you got everything

How to reverse-engineer real interactivity/animation from a live Wix site and apply it to the
Astro rebuild, instead of guessing from `data-motion`-style attributes (which wildly overstate the
real animation surface — most instances are structural markers, not choreography).

## The method: `document.getAnimations()`, not attribute-counting

Wix pages carry attributes like `data-motion-part`, `data-animation-name`, `data-animation-state`
on hundreds of elements. Counting these overstates the real animation surface: most instances
(background-layer markers like `BG_LAYER` / `BG_MEDIA`) have no animation attached, not evidence
of choreography. A raw attribute count can suggest "hundreds of animated elements" when the real,
verified figure is far smaller and simpler.

The reliable method is the browser's own **Web Animations API**:

```js
document.getAnimations().length; // every real Animation object currently on the page
```

For each animation, `.effect.getComputedTiming()` gives real `duration`/`delay`/`easing`/`fill`,
and `.effect.getKeyframes()` gives the actual `from`/`to` property values — not an estimate, the
literal numbers the browser is using. Group by a signature (duration + animated properties +
from/to values) to find the real, distinct "recipes" in use:

```js
const recipes = new Map();
document.getAnimations().forEach((a) => {
  const t = a.effect.getComputedTiming();
  const kf = a.effect.getKeyframes();
  if (kf.length < 2) return;
  const key = `dur=${t.duration} props=${Object.keys(kf[0]).filter(k => !['offset','easing','composite','computedOffset'].includes(k)).join(',')} ${kf[0].opacity}->${kf[kf.length-1].opacity}`;
  recipes.set(key, (recipes.get(key) || 0) + 1);
});
Array.from(recipes.entries()).map(([k, v]) => `${v}x  ${k}`).join('\n');
```

This surfaces the dominant, real pattern by frequency instead of by attribute presence. Implement
the dominant recipe(s); small identity/reset animations (`transform: none → translate(0px)...`,
opacity `1 → 1`) are internal tooling artifacts, not visible choreography — safe to ignore.

**Caveat found in practice:** background/inactive browser tabs (common when driving a page via
browser automation with several tabs open) can silently throttle `IntersectionObserver` callbacks
and leave `getAnimations()`-based checks hanging indefinitely, or make a correctly-implemented
reveal system look broken in your own rebuild. If a check seems to hang, or a reveal system you
just built appears not to fire, force a real paint first (a screenshot action, or an actual
scroll) before concluding anything is broken — it may just be a throttled background tab.

## `getAnimations()` does NOT catch everything — check parallax separately

This is the most important gap to know about. `getAnimations()` only surfaces effects implemented
via CSS transitions/animations or the Web Animations API. **Parallax** (background moving at a
different rate than the foreground as the user scrolls) is typically implemented one of two other
ways, neither of which produces an `Animation` object:

- `background-attachment: fixed` — pure CSS, no JS, no Animation object.
- A scroll event listener directly mutating an element's `transform` on every scroll tick —
  imperative style mutation, not the Animation API.

**Don't conclude "no parallax" just because the `getAnimations()` sweep is fully explained by
scroll-reveal and dropdown recipes.** Check for it directly and separately:

```js
// Record position before/after a scroll, compare each element's movement to the page's own
// scroll delta. If any element moves a DIFFERENT amount, that's parallax.
window.scrollTo(0, START);
await new Promise(r => setTimeout(r, 150));
const imgs = Array.from(document.querySelectorAll('img, video')).filter(el => el.getBoundingClientRect().width > 40);
const before = imgs.map(el => el.getBoundingClientRect().top);
window.scrollTo(0, START + 300);
await new Promise(r => setTimeout(r, 150));
const after = imgs.map(el => el.getBoundingClientRect().top);
const scrollDelta = 300;
const nonMatching = before.map((b, i) => Math.round(b - after[i]) - scrollDelta).filter(d => Math.abs(d) > 3);
// nonMatching.length === 0 across a few ranges spanning the whole page -> genuinely no parallax.

// Also check for the pure-CSS version:
Array.from(document.querySelectorAll('*')).filter(el => getComputedStyle(el).backgroundAttachment === 'fixed').length;
```

Run this across several scroll ranges spanning the full page (not just one spot), on a fresh page
load. A real worked example: 55 `img`/`video` elements checked across four ranges spanning an
entire landing page, zero moved at a different rate than the page scrolled, zero elements used
`background-attachment: fixed` — genuinely no parallax existed on that site, confirmed by
measurement rather than assumed from an animation-object count.

**"No parallax measured" ≠ "no perceived parallax" — and the owner's perception decides.** On
that same site the owner later described a section as having "pictures with a parallax effect".
The measurement was correct (zero scroll-linked deltas); what the owner was perceiving was the
combination of float-in reveals (`translateY(-50%)→0` on entry) and two infinite slow rotations
on decorative layers, which together read as depth. Two consequences:

1. Reproduce those float/rotation recipes faithfully — if they're skipped, the section feels
   flat and the owner reports "the parallax is missing" even though none existed.
2. If the owner explicitly asks for parallax, add a subtle scroll-linked drift (rAF, per-layer
   rate, centred on the section midpoint, disabled under `prefers-reduced-motion`) and log it as
   a **perception-matching deviation**, not a measurement. Don't argue the measurement at the
   owner; the measurement explains *why* they perceive it, it doesn't override what they want.

## Verifying a specific font "looks different" claim

If a rebuilt page's text looks visually different from live even though the computed
`font-family`/`size`/`weight` values match, don't guess — resolve the actual font identity:

1. Read `getComputedStyle(el).fontFamily` on the live element — it's usually a comma-separated
   fallback chain starting with a page-builder-generated hash name (e.g. `wfont_23c8a5_...`) and
   ending in a more human-readable fallback name.
2. Find the real font FILE: check `performance.getEntriesByType('resource')` for `.woff`/`.woff2`
   requests matching that hash — Wix serves custom/uploaded fonts from a `ufonts` CDN path.
3. Download the file and read its own internal name table (don't trust the CDN URL or CSS class
   name alone — those are opaque hashes) — e.g. with Python's `fontTools`:
   ```python
   from fontTools.ttLib import TTFont
   f = TTFont('downloaded-font.woff2')
   for rec in f['name'].names:
       if rec.nameID in (1, 4, 6, 16, 17):  # family, full name, postscript name, etc.
           print(rec.nameID, rec.toUnicode())
   ```
   This gives the font's own claimed identity (e.g. "Inter Medium"), which is authoritative —
   more reliable than any hash or filename.
4. Compare against what the rebuild actually has loaded: `document.fonts` lists every `FontFace`
   with its `family`/`weight`/`status` — confirm the matching weight shows `status: "loaded"`, not
   silently falling back to a system font.
5. If the font family, computed size/weight/line-height/letter-spacing, and loaded-font-status all
   match, the rebuild is correct — the visual impression of "different font" may be a false alarm
   (screenshot compression, a different scroll/animation state, viewing conditions) rather than a
   real gap. Report the verification data, don't silently "fix" something that measures identical.

## What a real migration found (worked example, for calibration)

On one real Wix → Astro migration: 152 real `Animation` objects present at page load. Grouped by
recipe, the dominant patterns were a scroll-triggered fade (opacity 0→1, 1200ms,
`cubic-bezier(0.445, 0.05, 0.55, 0.95)`, `fill: "backwards"` — paused until scrolled into view) and
a nav-dropdown reveal (`opacity` + `clip-path`, 0.4s, `cubic-bezier(0.645, 0.045, 0.355, 1)`,
confirmed by hovering live and reading both the closed and open computed styles — a single read
only gives you one side of a hover transition). No stagger delay on repeated grid items. No
scroll-jack. No parallax anywhere on the page, confirmed by direct measurement. The "hundreds of
motion-looking attributes" on the live DOM did not correspond to hundreds of real animations.

**A second page on that same site DID have real parallax** — this is why the parallax check must
run per page, not once for the whole site. The landing page had none; a secondary page's hero had
two flanking photos with a genuine scroll-linked `transform: matrix(...)` mutated by a scroll
listener (confirmed via `getBoundingClientRect()` inspection up the ancestor chain — no
`data-parallax`-style attribute exposed it directly). The movement-delta test gave a stable,
reproducible ratio per element (0.792 and 0.865 — i.e. each photo lags behind the page scroll by a
different amount), re-verified after a settle wait to rule out a load-in-animation artifact rather
than genuine scroll-linked movement. Implemented as `translateY` computed from each element's
scroll position *at mount* (not a live `getBoundingClientRect()` read on every frame, which would
include the transform this same script just applied and double-count it): `offset = (currentScrollY
- mountScrollY) * factor`, where `factor = 1 - measuredRatio`. The rebuilt result matched live's
ratio exactly, at every tested scroll position.

## Implementation checklist

1. Load the live page fresh (not a stale, heavily-scrolled tab — animations that already played
   once read as `finished`/`opacity: 1`, masking the real pre-reveal state).
2. Run `document.getAnimations().length` immediately after load. Group by recipe (script above).
   Implement the dominant recipe(s) by frequency, not every unique value.
3. For hover-triggered UI (dropdowns, accordions), search for `[data-animation-name]` /
   `[data-motion-enter]` attributes, then hover the live element and re-read `getComputedStyle` to
   capture both the closed AND open state.
4. Separately, run the parallax movement-delta check (above) across a few scroll ranges spanning
   the whole page, and check for `background-attachment: fixed`. Do this even if step 2 already
   found and explained every `Animation` object — parallax uses a different mechanism entirely.
5. Implement with a progressive-enhancement guard: content visible by default (no-JS-safe), a
   script only opts elements into the pre-reveal hidden state once it actually runs. A script
   failure should never permanently hide real content.
6. Respect `prefers-reduced-motion` even if the source site doesn't — this is an accessibility
   default worth keeping regardless of source-site fidelity.
7. After implementing, verify against the live site's real behavior (not just "it fades in, looks
   about right") — compare duration/easing by eye at slow motion if needed, confirm hover states
   open AND close correctly, confirm the reveal fires once (not repeatedly) as content re-enters
   view unless the source site genuinely re-triggers.


## Buttons: the migration's most-missed interaction

Wix renders its own hover states from the page builder, so they exist on the live site but live
NOWHERE in anything you extract — `document.getAnimations()` will not report them (they are CSS
transitions on `:hover`, not Web Animations), and a DOM/computed-CSS dump taken at rest captures
the resting state only. The result is a rebuild that looks pixel-identical in a screenshot and is
completely dead to the pointer.

Do not try to extract them. Ship the baseline below on the canonical button class as part of the
rebuild, then compare against live by actually hovering, pressing and TABBING to a button on both.

### Button interaction baseline — NON-NEGOTIABLE, define once, never per component

A button with no states is a rectangle. Every button ships with FOUR states or it is not done,
and they are defined ONCE on the canonical class in global CSS, never per section.

Why this is a hard rule and not advice: an audit of engineeringleaders.io on 2026-08-06 found
**183 button instances across 47 files and not one `:hover`, `:active`, `:focus-visible` or
`transition` on either canonical class**. Every button on a whole production estate was inert,
including under keyboard focus. It passed every other gate. Nothing catches this unless it is
checked explicitly, because an inert button looks completely correct in a screenshot.

```css
.btn-primary, .btn-secondary {
  cursor: pointer;
  -webkit-user-select: none; user-select: none;  /* double-tap selecting the label reads as broken */
  transition:
    transform 180ms cubic-bezier(0.34, 1.4, 0.64, 1),   /* slight overshoot = "attached to the pointer" */
    background-color 220ms ease, border-color 220ms ease, color 220ms ease, box-shadow 220ms ease;
}

/* GUARD hover behind (hover: hover). Without it a tap leaves a touch device stuck in the hover
   state until the user taps elsewhere — the single most common mobile button bug. */
@media (hover: hover) {
  .btn-primary:hover  { transform: translateY(-2px); background: <one step brighter>;
                        box-shadow: 0 10px 22px -12px <fill colour at ~55%>; }
  .btn-secondary:hover{ transform: translateY(-2px); border-color: <text colour>;
                        background: <text colour at 7%>; }
}

/* :active is not optional — on touch it is the ONLY feedback, since :hover never fires. */
.btn-primary:active, .btn-secondary:active { transform: translateY(0) scale(0.97); transition-duration: 90ms; }

/* focus-visible, NOT focus: a mouse click must not leave a ring behind. Missing entirely is an
   accessibility failure, not a polish gap — a keyboard user cannot see where they are. */
.btn-primary:focus-visible, .btn-secondary:focus-visible { outline: 2px solid <accent>; outline-offset: 3px; }

.btn-primary[disabled], .btn-secondary[disabled],
.btn-primary[aria-disabled='true'], .btn-secondary[aria-disabled='true'] {
  opacity: 0.45; cursor: not-allowed; transform: none; box-shadow: none;
}

/* Drop the MOVEMENT only. Colour, ring and press feedback stay — a reduced-motion user still
   needs full affordance. Killing every state here is the common over-correction. */
@media (prefers-reduced-motion: reduce) {
  .btn-primary, .btn-secondary { transition: background-color 220ms ease, border-color 220ms ease, color 220ms ease; }
  .btn-primary:hover, .btn-secondary:hover,
  .btn-primary:active, .btn-secondary:active { transform: none; }
}
```

Define this on the canonical class and all N instances get it in one edit; per-component hover
classes guarantee drift and guarantee some component gets missed. If a section genuinely needs a
different size, override `font-size`/`padding` in that component and inherit every state.

**Verify before shipping — an inert button is invisible in review:**

```bash
# Against the BUILT html/css, not the source: catches states lost to a scoped-style mistake.
for s in ':hover' ':active' 'focus-visible' 'aria-disabled' 'hover: hover' 'prefers-reduced-motion'; do
  printf '%-24s %s\n' "$s" "$(grep -c -- "$s" dist/**/index.html 2>/dev/null | head -1)"
done
# Then tab to a button in a real browser. If you cannot see where focus is, it is not shipped.
```
