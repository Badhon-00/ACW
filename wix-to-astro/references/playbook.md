# Playbook: Duplicating a Website (Code-First Method)

Generalized from a real Wix → Astro migration. A site-agnostic method for rebuilding an existing
website in code with pixel/behavior fidelity — the source doesn't have to be Wix and the target
doesn't have to be Astro, but this is written with that pairing in mind since it's the most common
case: Wix's page-builder output makes naive approaches (copy the HTML, eyeball the styles) fail in
specific, recurring ways this playbook exists to catch.

## Method summary

**Code-first, not screenshot-first.** Screenshots are a secondary sanity check, not the primary
measurement. The primary source of truth is the live page's actual rendered DOM + computed CSS —
exact px, hex, font metrics, spacing — extracted per section and rebuilt from those real values.
A screenshot-diff approach is too slow and fuzzy for real fidelity: it tells you *that* something
looks different, not *which property* is wrong or by how much.

## Step 1 — Reconnaissance (before writing any code)

1. Map the site (all URLs, template count) — don't assume "it's just a landing page."
2. Scrape/read the target page for: section inventory + order, interactive elements, fonts,
   colors, dynamic/CMS-driven parts, third-party widgets, single vs multi-page scope.
3. Separate **design** (copy this) from **backend** (this is a data model, not a pixel — decide
   deliberately whether to snapshot it statically or model it properly, e.g. as an Astro content
   collection).
4. Check what's already reusable in-house before building anything new: existing brand kits,
   existing framework+deploy stack, existing i18n solutions. Don't rebuild solved problems.
5. Know the deploy target's hard platform limits up front (max asset size, request size, etc.) —
   e.g. Cloudflare Workers rejects any single static asset over 25 MiB. Check this before choosing
   media quality/resolution for anything heavy (video especially), not after a failed deploy. A
   five-minute check here avoids a rework cycle at the deploy step.

## Step 2 — Brand kit extraction

- Pull real values, not eyeballed ones: hex codes from computed styles, exact font-family names
  and weights from `getComputedStyle`, spacing rhythm from repeated measurements across sections.
- **Fonts: never trust a grep of raw HTML/CSS text for "what font does this site use."** Page
  builders (Wix, Squarespace, ...) ship a large global font library in every site's stylesheet —
  most of it declared but never assigned to any element. Grepping font-family strings out of the
  markup surfaces that whole unused library, not what's actually painted. The only reliable
  answer: walk the rendered DOM and read `getComputedStyle(el).fontFamily` on real elements
  (headings, body, buttons, quotes/emphasis). Cross-check a handful of element types before
  concluding — one element could be an outlier, four agreeing is a pattern.
  (Real example: a live-site scan initially reported "Helvetica Neue + Poppins" from a raw-HTML
  pass; the computed-style pass showed 100% of rendered text was actually a different family
  entirely, reversing a "must accept a font-license risk" decision into "no risk exists.")
- Once the real fonts are identified, extract the actual `.woff2` files from the site's own CDN
  (visible in `@font-face src` URLs) rather than substituting a Google Fonts / Fontsource lookalike
  — the site's own file IS the exact match, and is usually a direct, licensable download.
- Note where the live site uses baked images (e.g. gradient PNGs) vs live CSS — baked images are
  *easier* to reproduce (just re-host the asset) than reverse-engineering a CSS effect.

## Step 3 — Scaffold from an existing stack, don't start from zero

- If a matching framework+deploy pattern already exists elsewhere (a sibling project, a template),
  clone the config (build tool, deploy config, i18n plumbing) — not the components. Components are
  usually page-specific; config/tooling is usually fully reusable.
- Deploy target: stand up on a **staging URL** first. Never point new infra at a live domain's
  routes until an explicit, separately-approved cutover step. This is a hard rule, not a
  suggestion — the whole point of rebuilding in parallel is that the live site keeps serving
  traffic untouched until you're ready.

## Step 3.5 — Extraction hygiene

- **Resize the extraction viewport explicitly before measuring anything.** A browser tab's default
  window size is whatever the OS/display gives it, not a standard breakpoint. Every pixel
  measurement taken before resizing to your target breakpoint (1440, 390, etc.) is wrong. Resize
  first, confirm `window.innerWidth`, then measure.
- **Check actual scroll/interactive behavior, not just one element's own computed style.** A
  "sticky header" may report `position: relative` on the header itself while an ancestor wrapper
  actually does the pinning (common in page-builder output). Verify by scrolling and re-measuring
  `getBoundingClientRect()`, not by reading one property once.
- **For large inline assets (long SVGs, etc.) that a tool's output limit truncates:** don't burn
  many round trips reconstructing raw markup chunk by chunk. Check the project's own existing asset
  library for a match first — compare distinguishing features (exact color palette, aspect ratio)
  to confirm it's the same asset, then use that file directly.
- **Treat a prior brand-kit/design doc as a snapshot in time, not a permanent fact.** Section
  counts, row layouts, and structure claims can go stale between the doc's capture date and today.
  Re-verify against the live DOM rather than trusting the document — it's a hypothesis, the live
  page is ground truth.
- **When climbing the DOM to find "the card/section containing this element," scope by a
  structural signal, never a fixed hop count.** A fixed `for (i=0;i<N;i++) el = el.parentElement`
  that correctly reaches one card's container will silently over- or under-shoot on a
  differently-nested repeated item elsewhere on the same page — every item then returns the SAME
  (wrong) data, which reads as success (no error, plausible-looking output) until you check for
  duplicates. Scope instead by a real structural condition: "the closest ancestor containing
  exactly one of [the marker I'm querying for]." This is a recurring failure mode across sections
  with repeated card layouts (testimonials, meetup/event grids, team grids) — treat any fixed-hop-
  count DOM climb as a known trap to actively avoid, not a one-off mistake.
- **MD5-compare any batch of downloaded assets when there's any chance of a copy/transcription
  slip** (manually copying N extracted URLs into N download commands is exactly that chance). An
  off-by-one shift is invisible by eye in a list of hashes/filenames but immediately obvious the
  moment you diff file hashes and two match that shouldn't.

## Step 4 — Per-section, code-first rebuild loop

**Before rebuilding a section from scratch, check whether it already exists as a component from
an earlier page in this same migration.** Wix (and page builders generally) let an editor drop the
same visual block onto multiple pages — a conference promo banner, a partner-logo wall, a
cross-property card row — and each placement looks byte-identical on the live site even though
Wix's own internal representation treats them as independent instances with no shared source. If
page 2's Section C looks pixel-identical to page 1's Section C already built, don't re-extract and
re-build it as new markup: import the existing component and reuse it. Concretely:

- Before starting a section, scan already-built pages' sections for a visual match (same copy,
  same layout, same assets) — not just "looks similar," genuinely identical.
- If a match exists, confirm it's really the same content on live (not two sections that happen to
  share a layout but differ in copy/links) by diffing the actual text and hrefs, not just the
  screenshot.
- Extract that section into a shared component (if it wasn't already one) and import it on the new
  page, rather than copy-pasting the component file. Copy-pasting means every future correction has
  to be applied twice (or drifts silently when it isn't) — one shared component means one fix
  location.
- If the sections are ALMOST but not quite identical (same layout, different copy/links per page),
  that's a parameterization signal, not a reuse-as-is signal: build one component that accepts the
  varying parts as props, rather than either duplicating the whole section or forcing a false
  "identical" merge that loses the real per-page differences.

For each genuinely new section, in order:
1. Extract the live section's DOM structure + computed CSS per element (not just a screenshot).
2. Rebuild the section from those exact values.
3. Confirm with a quick screenshot glance (secondary check, not the primary measurement).
4. If it doesn't match, correct the specific extracted value that's wrong and repeat.
5. Log the section in a build log: started-with delta, what changed, whether it helped. This log
   pays for itself the moment a later correction needs to explain *why* a value changed — "the
   first pass eyeballed it, the second pass measured it" is a very different situation from "we
   don't know why this value is what it is."

## Step 4.5 — Full side-by-side comparison pass (do this even after every section is "done")

Isolated per-section extraction is efficient but structurally blind to two classes of error a
dedicated final pass catches:

- **Gaps *between* sections.** A stray link, badge, or small element sitting in the "dead zone"
  between one obvious section and the next gets missed because no single extraction query's scope
  covers it — each section extraction correctly covers its own section and nothing sitting just
  outside it.
- **Wrong negative results.** "I checked for X and found none" needs the SAME scrutiny as a
  positive finding, not less — especially when a human glancing at the live site can see X right
  there. A query scoped too narrowly (e.g. `heroSection.querySelectorAll('video')` when the video
  element actually lives in a wrapper the query didn't include) silently returns an empty, falsely
  confident result.

Do a full scroll-through with the rebuild and the live site open side by side, at matching scroll
positions, after the section-by-section builds are complete. This is a distinct verification step,
not a redundant repeat of Step 4 — budget for it as a standard part of the process, not an optional
extra. If the live site ignores synthetic wheel-scroll/keyboard events (some Wix sites use a
custom scroll-jack mechanism that doesn't respond to automation-synthesized gestures even though
the page isn't frozen), drive scroll position via `window.scrollTo()` directly instead of
simulated input; confirm with `window.scrollY` that it actually moved before concluding a section
doesn't exist or a screenshot is stale.

## Step 4.6 — Dedicated typography audit (a third, distinct verification pass)

Neither the per-section code-first build (Step 4) nor the full-page visual scroll-through
(Step 4.5) reliably catches font-metric gaps — they're rarely visually obvious at normal reading
distance but are load-bearing for true fidelity. Run a dedicated pass, per section, checking all
six computed properties for every distinct text role: `font-family`, `font-size`, `font-weight`,
`font-style`, `line-height`, `letter-spacing`. Match live elements to rebuilt elements by visible
text content, not DOM position.

- **Never trust a framework's default line-height for an arbitrary font-size.** Setting an
  arbitrary size only sets size; line-height silently falls back to the framework default (e.g.
  Tailwind's 1.5), which is very often wrong. Live sites use different ratios per role (tight
  ~1.0 for large display headings, ~1.4 for labels/names, ~1.6 for body copy/buttons) — always
  pair an arbitrary size with an explicit, measured line-height.
- **Check letter-spacing explicitly, every time — don't wait for something to "look tight."** Real
  negative tracking on headlines/numbers/labels is easy to miss entirely if you only check it when
  a mismatch is visually suspected.
- **Re-verify every `clamp()`/fluid-size formula resolves to its intended value at the actual
  target viewport** — a coefficient that looks reasonable can silently fall short of (or overshoot)
  its own cap. This recurs across unrelated sections; treat it as a standing checklist item, not a
  one-off catch.
- **A platform's raw `font-weight`/`font-style` CSS properties may not be trustworthy signals.**
  Wix, for one, bakes real weight/style into which uniquely-named static font file gets loaded
  (`orig_inter_medium`, `orig_lora_semibold_italic`, etc.) and its literal CSS properties report
  generic values (`400`/`normal`) almost everywhere regardless of visual weight or slant. Diff on
  the font-family identity/suffix, not the numeric property, when the platform does this.
- **Don't assume one shared button/CTA class covers every context.** Different contexts on the
  same live site (e.g. a compact nav pill vs. an in-page marketing CTA) can genuinely use different
  font metrics for what looks like "the same button style." Confirm this with data before either
  (a) editing a shared/global style broadly or (b) concluding every instance needs its own
  bespoke fix — check enough distinct usages to tell whether the values cluster (one shared fix
  needed) or genuinely diverge by context (per-context scoped overrides are correct, not a
  workaround). Getting this backwards means either a wrong global change with wide blast radius or
  needless duplicated one-off overrides.
- **A window-resize automation call can silently no-op on a browser tab that's been reused across
  a long session** (window stuck at its original size regardless of the requested dimensions).
  Always confirm `window.innerWidth` actually changed after resizing before trusting any
  measurement taken in that tab; if it didn't change, abandon that tab and open a fresh one rather
  than debugging the resize.

Scope discipline: decide upfront which fidelity dimensions are in scope for this pass (e.g.
static layout/type/color now, animation later) and hold that line — don't let one section's
extra polish creep into every section's budget.

## Step 4.7 — Owner spot-check pass (the human verification layer — run it AFTER Step 4.8)

Steps 4, 4.5, and 4.6 are all automatable — DOM extraction, scroll-through, computed-style diff.
Even run well, they miss a real class of gap that only surfaces when the site owner compares the
rebuild against live with their own eyes, item by item. Budget for this pass explicitly rather
than treating owner feedback as a signal something upstream failed. Concrete, recurring failure
patterns from real rebuilds, generalized so the next one checks for them proactively instead of
waiting to be told:

- **Media frames: check for a fixed aspect ratio before assuming full-bleed or full-stretch.**
  A background video/image inset from the section edge (a rounded card) is one gap; a SEPARATE
  gap is whether that frame's height is a fixed aspect ratio (common on page-builder platforms) or
  genuinely stretches to fill its container. Measure both `width` and `height` of the frame, not
  just its inset from the edges — `aspect-ratio` in the live computed style is the direct signal;
  don't infer height from "fills the section."
- **A landscape "pill" shape is not a circle.** `border-radius` clamped to a huge value (e.g.
  9999px, or a platform's own huge px number) on a NON-square box produces a stadium/pill/oval —
  visually distinct from a circle. If a thumbnail's wrapper box isn't square (check computed
  `width` vs `height`, not just the class name), don't reach for a square-crop-plus-full-round
  utility by habit — measure the real aspect ratio and keep it non-square with the same rounding.
- **A decorative background can be a real `<img>` sibling, not a CSS `background-image`.** If a
  glow/wash/watermark is visible behind text but `getComputedStyle(el).backgroundImage` is `none`
  on every ancestor up to the section, don't conclude there's no background asset — search the
  section for `img`/`canvas`/`video` elements positioned behind the text by z-index or DOM order
  instead. Platforms differ in which mechanism they use for the "same-looking" effect.
- **`getComputedStyle(...).color` alone doesn't capture text styling — check `textDecorationLine`
  too.** A near-invisible "ghost" color and a genuine strikethrough can share the exact same color
  value; matching the color while missing `text-decoration-line: line-through` produces a visually
  very different (and wrong) result even though the one property that was checked matches exactly.
  When a text role looks unusually faint or stylized in a live screenshot, check the full
  text-decoration/text-transform property group, not just color and font metrics.
- **"No visible controls" on a carousel/rotator is a suspect finding, not a confident one.**
  Hover-revealed or focus-revealed controls (common for carousel arrows) don't exist in the DOM,
  or exist with `opacity:0`/`visibility:hidden`, until the live page is actually hovered/focused —
  a static `querySelectorAll` pass finds nothing and can wrongly conclude "static grid, no
  controls, build it as a static grid." If a section behaves like a carousel (auto-advancing
  content, one item visible at a time) treat it as one — with real prev/next controls, even if a
  static DOM scan reports none — rather than flattening it into a static multi-column grid.
- **Recount every CTA row against live before shipping it as "done."** It's easy to build the
  buttons/links you found and stop, without re-confirming the exact count and order against the
  live page one more time. A row with "1 button + 1 link" and a row with "2 buttons + 1 link" look
  similar enough in a quick pass to miss the difference; explicitly count and compare, per CTA
  row, as its own checklist item. This includes the actual `href` attribute-search — a grep for
  `href="..."` misses links whose destination is a runtime expression (e.g. an array-driven
  `href={item.url}` in a repeated card component), so also grep for the *pattern*, not just
  literal-string hrefs, before declaring a link inventory complete.
- **A `max-width` measured on one element doesn't necessarily apply to its siblings.** A heading
  and the body copy directly below it can legitimately have different container widths on live
  (e.g. a wide heading over a narrower paragraph) — measure each text role's own rendered width
  independently rather than reusing one "the text block is Npx wide" number for the whole group.

## Step 4.8 — Tweaking round (the last automated pass, before the owner sees it)

When the content migration and visual transition are finished, go again **sequentially, section
by section** — not spot-checking, a full ordered sweep. For each section:

1. **Content ↔ visual correspondence.** Does every string, image, and video that the original
   section shows appear here, in the same position? Verify at SOURCE level, not screenshot level:
   diff the rebuilt markup against the original section's DOM, including background media —
   images AND videos. Background media is where this round earns its keep: a `<video>` behind a
   headline, a wash `<img>` behind a card.
2. **Positioning, measured.** Re-measure the rendered boxes of the rebuilt section in a real
   browser and diff against the recon values. Do not trust that CSS which *encodes* the right
   numbers *renders* the right numbers — three real failure modes from one migration:
   - A square source video with `height: 100%` rendered 1287×1287 in a 710px box (intrinsic
     ratio won); the fix is a fixed height on both box and element. Measure the rendered box
     of every `<video>`/`<img>`, never assume the CSS constrained it.
   - Vertically centering a hero content column instead of using the measured page offsets
     drifted every element 20–40px. If the original positions content at absolute coords,
     reproduce the coords as explicit margins, then re-measure.
   - Two adjacent original sections merged into one component silently collapsed their summed
     paddings (29.9 + 28.1 ≈ 59px of air became 4px). **Inter-section spacing is the SUM of the
     lower section's top padding and the upper section's bottom padding** — when merging
     sections, transfer the sum, then re-measure the rendered gap.
3. **Interactivity, per element.** For each element and for the section as a whole, inspect the
   scrolling and interactive effects **in the original's source**: the `document.getAnimations()`
   recipes for that section, stacking order of decorative layers, scroll behaviour, hover/focus
   states. Rebuild what runs, not what the markup's attributes imply (see `interactivity.md`).
4. **When a recon table disagrees with a rendered box, the box wins.** A recorded padding of
   `9.36px 17.54px` alongside a recorded box of `327×84` cannot both describe the same element —
   the padding belonged to an inner span. Re-measure the outer element and derive the padding
   from the box.

Two content-parity items that hide in plain sight during this round:

- **The consent/cookie banner is content, not chrome.** If the original shows one, the rebuild
  ships one — same copy, same controls. A dismissal without an explicit choice must NOT be stored
  as consent.
- **Scattered decorative layers are load-bearing to the owner.** A composition of small photos /
  illustrations around a video may look skippable and will be flagged in the first owner review.
  Never simplify it silently: either rebuild it (convert absolute offsets to percentages of the
  measured stage so it scales) or defer it loudly per Step 5.

## Step 5 — Defer expensive fidelity dimensions explicitly, don't skip them silently

Some fidelity dimensions (exact scroll-animation choreography, complex gallery widgets) are
disproportionately expensive relative to their visual payoff in an early pass. When deferring:
- Say so explicitly and log it as a decision, not an oversight.
- Leave structural hooks (stable class/data attributes) so the deferred layer can attach later
  without reworking the markup.

**When it's time to stop deferring animation, use `document.getAnimations()`, not the source
site's `data-motion`-style attributes, to find the real choreography.** See `interactivity.md` in
this skill's references for the full method and a worked example.

## Step 5.5 — Check for a full-resolution-original URL trick before asking the owner

Some platforms serve a resized/cropped/compressed copy on the page but expose the untouched
original at a predictable, unauthenticated URL. **Wix:** strip the `/v1/fill/...` or `/v1/fit/...`
transform segment from any `static.wixstatic.com/media/<id>~mv2.<ext>` URL — what's left is the
original upload at full resolution, no login required. Check for an equivalent on other platforms
(Squarespace, Webflow, Shopify all have their own CDN URL conventions) before asking the site owner
for a manual media export — it may already be unnecessary for anything currently published.

## Step 6.5 — Parallelizing across sections with subagents

Once the method is proven on one section (build it yourself first — don't parallelize before you
know the loop works), the remaining sections are independent and can be dispatched in parallel,
one subagent per section, for large wall-clock savings. What makes this safe in practice:

- **Hard scope boundaries per agent.** Each agent may only create/edit its own new component file
  and its own new asset folder. It must never touch shared files: the page(s) that assemble
  sections, the shared build/change log, nav/footer, or any other agent's section. One coordinator
  (you) does the integration pass afterward. This is what makes lock-free parallel writes safe —
  there's no shared-file contention if no agent touches a shared file.
- **Own browser tab per agent.** If extraction needs a live browser, each agent creates its own new
  tab rather than reusing one — concurrent agents on the same tab will step on each other's
  navigation/state.
- **Don't rely on a shared long-lived dev server for verification.** A dev server is a mutable
  shared resource: one agent restarting it (e.g. to pick up new CSS classes) can break another
  agent's in-flight check. Prefer verifying against the **static build output** (e.g. `pnpm build`,
  then inspect the generated HTML/CSS) — every agent can run this independently without
  interfering with others.
- **Each agent returns a paste-ready log entry instead of writing to the shared log itself** —
  avoids concurrent-write races on one file. The coordinator appends them all in one pass afterward.
- **Give every agent the same structural reference** (e.g. "look at this already-built section,
  match its header-comment convention and code style") so parallel output is stylistically
  consistent without needing a cleanup pass.
- **After all agents land:** sweep for stray artifacts (`git status --porcelain`, leftover browser
  tabs pointing at deleted temp routes, stray dev-server processes on other ports) before
  integrating — parallel agents each doing their own verify-then-delete cycle can leave session
  debris even when each one individually cleaned up after itself.
- **Do ONE authoritative full-page structural pass yourself before integrating**, even though each
  agent verified its own section. A section-order or adjacency claim from a design doc (or from one
  agent's local context) is a hypothesis until a single walk of the whole live page confirms it —
  individual per-section checks can each be locally correct about their own boundaries and still
  collectively disagree about global order.

## Step 6 — What only the site owner can provide (ask early)

- Full-resolution original media (site's own CMS/media-manager export beats scraped/CDN-resized
  copies every time).
- Editor/source access for anything whose *exact* behavior isn't recoverable from rendered output
  alone (e.g. an animation editor's timing/easing values).
- Original design source (Figma, brand guide) if it exists — turns "measured approximation" into
  "exact value."

## Cutover considerations (once the rebuild passes owner review)

- Inventory the FULL live URL surface before assuming scope — sitemap XML files, robots.txt, and
  a raw page/template count from the source platform's own admin are all more reliable than
  guessing from the nav menu. A "just the landing page" migration often turns out to have a much
  smaller (or larger) real remaining URL surface than assumed once actually counted.
- Build a redirect map for every URL whose slug changes between old and new — this is not
  optional for SEO continuity. Page-builder platforms often generate slugs with different escaping
  rules than a hand-built router (e.g. keeping punctuation/apostrophes URL-encoded where a rebuild
  strips them) — diff the two slug sets programmatically, don't eyeball a sample.
  Numeric/ID-based aliases (e.g. `/post/42`) are worth keeping stable across rebuilds regardless of
  slug changes, since they're the most likely to be linked from outside the site.
  Also check the destination when following the *pattern* not just the literal string — see the
  CTA-row note in Step 4.7 about `href={item.url}`-style dynamic links.
- Check for existing routes already carved out of the source domain before adding new ones (a
  previous partial migration, a form handler, a subdomain) — a route that's too broad can
  accidentally swallow traffic meant for something already working.
- Stage the deploy with a redirect/route change that's reversible in seconds (e.g. deleting a
  Worker route reverts every request to the old origin) and keep the old platform live and paid
  for a soak period — don't cancel the old hosting the same day as cutover.
- Re-run the redirect map as an actual verification pass after cutover: curl every old URL and
  confirm it resolves to a 200, not just that the redirect rule exists.

## Open questions / not yet validated

- Best concrete tooling for "computed CSS per element" extraction at scale (one node at a time
  vs a bulk per-page dump) — case-by-case so far.
- How to handle CMS-driven sections (event feeds, galleries) generally — content-collection
  modeling vs static snapshot vs live API wiring — decide per-project based on how often the
  source content actually changes and who needs to edit it going forward.
