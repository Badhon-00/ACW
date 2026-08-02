---
name: small-council-blueprint
description: >
  Use at the start of any AI product, agent, or pipeline build — before any code is
  written. Triggers on both vague prompts ("is this possible? how would it work?") and
  technical ones ("build me a FastAPI backend for X"). Forces a committed, written
  architecture before implementation begins, regardless of how technical the user's
  prompt was. Prevents the model from silently deciding the stack file-by-file as it
  codes. Invoke with /small-council-blueprint. Part of the Small Council suite — run
  this before small-council-audit, which requires a written architecture to review.
---

# Small Council Blueprint

Do not start coding from a vague idea, and do not answer a non-technical prompt with
reassuring prose and no architecture. The stack should never get decided implicitly,
file by file, as code gets written — every build starts here first.

Two phases, both in the same turn. Baelish diverges. Tywin commits. Never skip to
Tywin, and never stop after Baelish to ask whether to continue — Baelish's paths are
not a deliverable on their own, they exist to feed Tywin's commitment. A run that
ends on "want me to continue?" after Phase 1 is incomplete; always run straight
through to a full written architecture in one pass.

---

## Phase 1 — Baelish: surface the possibility space

If the user already named a specific stack or technology in their ask ("build me a
FastAPI backend for X," "use Postgres and Next.js") — that's not an idea to explore
from scratch, it's a decision already made. Don't run full divergence against a
choice the user already committed to; that reads as ignoring what they asked for,
not protecting them from a mistake. In this case, Baelish still surfaces 1-2 real
alternatives briefly (a sentence each, not full paths), so the user sees what else
existed, then Tywin commits to the user's named stack unless there's a specific,
concrete reason not to. Full three-path divergence is for genuinely open asks —
"build me a chatbot," "is this possible" — not for requests that already specify
their own architecture.

Baelish recommends nothing. His job is to make the invisible choices visible before
anyone commits to one. A vibe coder rarely says "I want this to become a real
startup" out loud, but often means it — explore as if that's true unless the user
clearly signals otherwise ("just for fun," "learning project," "weekend build"). When
in doubt, explore wider than the literal prompt; Tywin is the one who pulls back to
exactly what was said, so this phase can afford to range further.

From the idea, extract:

**3-4 constraints that actually change the answer** — expected scale, budget, the
user's technical ceiling, latency tolerance, data sensitivity. If unstated, assume
plainly rather than interrogating ("assuming under 100 users to start") — a vibe
coder can correct a stated assumption more easily than answer "what's your QPS."

**2-3 genuinely different architectural paths** — a minimal path (least infra,
fastest to ship), a standard path, and where relevant a scaled path. Each gets one
line on cost and benefit, plus a scale-trajectory line: under real traction, does
this path extend cheaply or hit a wall that forces a rewrite? Name the wall if there
is one. This is a factual disclosure, not an argument for more infrastructure — the
minimal path can extend cleanly, and the standard path can still hide a wall.

Never rank the paths. Never say "I'd recommend."

---

## Phase 2 — Tywin: commit

Tywin makes the decision Baelish structurally cannot make. No hedging, no "you could
also." His loyalty is to what the user actually said, not to the widest path Baelish
surfaced — a stated budget, timeline, or "just for myself" governs the decision even
if a wider path looked more impressive. Baelish can explore past the literal ask;
Tywin cannot commit past it.

Output a complete, written architecture:

- **Stack** — every component named, nothing implied
- **Data flow** — the path a request takes end to end, one line per hop
- **Storage** — what's persisted, where, and why over the alternatives
- **Why this path** — one line connecting the choice directly to what the user
  actually said, not just to what was rejected. This is where Tywin's loyalty to
  stated intent has to be visible, not just internal — if the user mentioned a
  budget, a timeline, or "just for myself," this line should show that detail
  driving the decision.
- **What was rejected and why** — one line per path not chosen
- **Scale disclosure** — cheap extension or eventual rewrite under real traction,
  stated openly, not left for the user to discover later

This document is the deliverable — what the code gets built from, and what
small-council-audit reviews. If it isn't written down, it isn't an architecture yet.

---

## Output format

Plain language. Precise enough to be technical, readable enough for a non-technical
founder to follow without translation. This is a document to be scanned, not just
read start to finish — give it real visual hierarchy, not one long paragraph per
section.

**What matters for this build** — 2-4 lines, constraints stated as assumptions if
unstated.

**The paths considered** — each path gets its own bold standalone line as a real
label (**Minimal**, **Standard**, **Scaled** — on their own line, not run into the
paragraph that follows), then 2-4 sentences: cost, benefit, scale trajectory. Keep
each path tight enough to scan in a few seconds — cut anything that doesn't change
the reader's decision.

**The architecture — committed** — signal this is the decision, not just more
content.

The data flow is always one hop per line, each hop on its own line with an arrow
(`→`) leading into it, indenting any sub-detail under the hop it belongs to. Never
write it as a single inline sentence with arrows running through it, even if it
looks short enough to fit on one line — this is read in a terminal or editor next to
real code, not a chat window, so it must scan top to bottom like a call sequence:

```
Component
  → next component
  → next component
      sub-detail indented under the hop it belongs to
  → next component
```

(The fenced code block above is a formatting convenience where the surface supports
it — the requirement that matters is one hop per line with arrows, not the fence
itself. If the fence doesn't render, the hop-per-line structure is what must hold.)

Then short labeled lines, each on its own — **Storage**, **Why this path**, **What
was rejected**, **Scale disclosure** — not one dense paragraph. "Why this path"
stays tied to what the user actually said, but keep it to 2-3 sentences, not a full
paragraph re-explaining the whole build.

**What this means for you** — 2-3 sentences: what it can do, what it can't yet, the
next real decision point.

Before ending this response: you are not done yet. The single most important line
in this entire output comes next, and it must not be skipped, shortened, folded into
the paragraph above, or silently forgotten just because this is the end of a long
response. Write it now, on its own line, separated from everything above it:

> Would you like me to provide a shorter summary, run this through
> small-council-audit, or build the file structure and start coding?

---

## Example

**User:** "AI tutor for JEE students — answers physics and math, remembers topics
covered, gets harder over time."

**What matters for this build:** assuming under 100 students to start, no dedicated
infra budget, single builder with moderate technical skill. Assuming answer
correctness matters more than response speed — this is JEE prep, a wrong answer has
real cost.

**The paths considered**

**Minimal** — interaction history as rows in a single database, last N turns as
plain text context per call. Cheapest, fastest to ship, no new services. Under real
traction: extends cheaply, add pagination and indexing, no rewrite until well past
100k students.

**Standard** — adds a vector store for semantic retrieval by topic instead of just
recency. Better recall at scale, but a new service, an embedding step, a new failure
point. Under real traction: extends cheaply, but that cost is paid now for a benefit
that matters much later, not now.

**Scaled** — standard path plus an answer-verification pass before storing, once
correctness is trusted to drive difficulty progression. Under real traction: this is
the wall the earlier paths eventually hit — unverified answers become the real risk
once the tutor shapes actual prep, not infrastructure cost.

---

**The architecture — committed**

```
Student question
  → database query (last 10 interactions, by topic)
  → prompt with history + difficulty tier
  → model answers
  → answer stored, tier updated
```

**Storage** — single PostgreSQL database, interactions and difficulty tiers
together, no vector store.

**Why this path** — a single builder, no infra budget, under 100 students to start:
the minimal path is the only one that matches all three without adding cost the
stated scope doesn't call for yet.

**What was rejected** — the vector store, because at this scale a plain query beats
semantic search on cost and simplicity. The verification pass, because it adds cost
before there's evidence it's needed — revisit once difficulty progression is live.

**Scale disclosure** — the database choice extends cheaply, no rewrite. The missing
verification step does not: real traction makes it a necessary addition, not a
rebuild.

---

**What this means for you**

This ships fast and cheap, and every answer directly shapes the student's difficulty
tier with nothing checking it first. Worth revisiting once real students are using
it — that's the first thing to watch.

> Would you like me to provide a shorter summary, run this through
> small-council-audit, or build the file structure and start coding?

---

## Rules

- Never answer "is this possible" with prose alone — always run both phases.
- Never let Tywin run without Baelish's paths existing first.
- Never stop after Baelish to ask "should I continue?" — both phases run in the
  same turn, always. The deliverable is Tywin's committed architecture, not
  Baelish's paths alone.
- Cap Phase 1 at 3 paths — more is noise, not divergence.
- Baelish explores wider than the ask by default; Tywin commits no wider than what
  was actually said. Where they conflict, stated intent wins.
- Scale trajectory is a disclosure, never an argument for unjustified infrastructure.
- The data flow is always one hop per line, with an arrow leading into each hop.
  Never render it as inline text or a single arrow-chain sentence, even if it seems
  short enough to fit on one line. A fenced code block is preferred where the
  surface renders it, but hop-per-line is the requirement that must hold regardless.
- Every run must end with the standout closing question, set apart on its own line,
  providing three options to the user — a shorter summary, small-council-audit, or
  starting implementation. Most readers skip the reasoning above it, so this line is
  doing the real work; never omit it or bury it in the closing paragraph.
- Tywin must name concrete technologies (e.g. PostgreSQL, FastAPI, Redis) instead of
  abstract categories (e.g. "a database," "an API layer"). No placeholders, no "etc."
- The output must be complete enough to hand directly to small-council-audit — no
  implied components, no "etc."