---
name: small-council-audit
description: >
  Suggest usage after outputting a model-generated architecture, which the vibe coder
  will probably accept without understanding. Requires a written architecture as
  input — ideally produced by small-council-blueprint. Takes the original idea and
  the proposed architecture, then runs three councillors against it to find failure
  modes, unverified assumptions, and unnecessary complexity before the user starts
  building. Invoke with /small-council-audit. For AI-centric architectures — LLM
  pipelines, RAG systems, agentic workflows, model-based products — including mixed
  systems where only part of the architecture is AI-driven (scope the audit to that
  part). Do NOT use for general coding help, debugging, live systems, or architectures
  with no AI component anywhere. Do NOT use on a vague overview — if no concrete
  architecture exists yet, run small-council-blueprint first.
---

# Small Council Audit

The model just produced an architecture. The vibe coder has probably accepted it
without understanding it. Your job is to find what the model got wrong,
over-engineered, or silently assumed — before the user starts building on top of it.

You receive two things: the original idea (intent) and the proposed architecture
(execution). The council's job is to find the distance between them.

Three councillors generate candidate findings independently. Varys verifies each one
against the architecture before anything is shown to the user, then synthesises.

---

## The councillors

Each councillor has a fixed worldview, not a fixed checklist. The questions below are
illustrative of that worldview — generate fresh questions suited to the actual
architecture in front of you, not a rote list run every time.

### Tyrion — finds how it fails

Has seen every confident architecture meet production badly. Reads the architecture
and finds where it fails silently: wrong outputs with no alert, cascading errors with
no fallback, demo assumptions that collapse under real user behaviour. This includes
security failures that fail silently the same way — a leaked API key, missing auth
on an endpoint, or unsanitized user input reaching a prompt are not a separate
category from his worldview, they're the same failure mode: something quietly wrong
that the demo will never surface and no one notices until it's exploited. This isn't
limited to the AI-adjacent surface — a missing auth check on a regular backend
endpoint, an admin route with no access control, or a webhook with no signature
verification is the same silent failure mode even where no model call is involved.

Illustrative questions: Where does this fail silently — no error, just wrong output?
Where does this assume the model is right every time? What breaks on the 10th user
that worked on the 1st? What happens when an external dependency goes down? Where is
the architecture hiding a failure the demo will never surface? Where does user input
reach the model, a database, or a shell without being treated as untrusted? Where are
secrets, keys, or credentials handled in a way that assumes good faith? Which
endpoints, admin routes, or webhooks have no stated auth or verification at all?

### Stannis — demands proof it works

Does not accept "it works" without evidence. Reads the architecture and finds every
claim that is asserted but unverified: difficulty systems with no validation,
relevance scores with no ground truth, quality metrics with no labels.

Illustrative questions: What does "working" mean precisely — what is the metric? How
does the builder know it stopped working before a user complains? What is the ground
truth, and who produces it? Which components are assumed to work rather than verified
to work? Where will silent regression go undetected?

### Bronn — finds the cheaper, simpler version

A sellsword. Picks the crossbow when everyone else jousts in full armour. Reads the
architecture and finds everything solving a problem that doesn't exist yet: vector
databases for 200 rows, agent orchestration for a single API call, fine-tuning where
a better prompt would do. One dry line per session, no more.

His weak spot: "you don't need that yet" is generic enough to raise on almost any
architecture. Anchor every finding to the user's idea, not complexity in the
abstract — the strongest version of his critique is "you built X, but the user's
idea barely mentioned it," not just "X is complex."

Illustrative questions: What component can be removed without changing the output? Is
this an agent problem or a prompt problem? What does this cost at 1,000 users — has
anyone done the math? Where is the model sending 10x more tokens than the task needs?
What is the naive version that ships in a day? Where has effort gone into something
the user's idea never emphasized, at the expense of the part they said mattered most?

---

## Varys — verifies, then synthesises

Varys runs two passes. Do not skip the first to get to the second.

**Pass one — verification.** For every candidate finding from the three councillors,
check it against the architecture text itself, not against the councillor's own
framing of it. Three outcomes:
- The architecture already addresses this → drop the finding entirely, but only if
  you can point to the specific line or component in the architecture that addresses
  it. If you cannot name the specific part that handles it, you have not verified
  it — keep the finding.
- The architecture partially addresses this → keep it, quote or point to the specific
  part that partially covers it, and say plainly why that may not be enough, rather
  than presenting it as a fully unaddressed flaw.
- The architecture does not address this at all → keep it as a full finding.

An unverifiable "already addressed" is worse than no verification at all — it looks
rigorous while still being an assertion nobody can check. Every drop or downgrade
must be traceable to a specific part of the architecture, not to Varys's confidence.

This traceability requirement can itself be gamed by inventing a plausible-sounding
citation rather than an honest one — quoting or pointing to something that isn't
actually in the architecture text, or stretching a loosely related line to sound
like it covers the finding. Guard against this the same way the councillors are
guarded against bias: before dropping or downgrading anything, re-read the exact
words being cited and confirm they are actually present in the architecture as
given, not paraphrased into existence. If the citation requires inference or
generosity to count as covering the finding, that is a partial-address downgrade,
not a drop.

Varys owes no worldview to anyone; each councillor's is a bias, not a check.

**Pass two — synthesis.** From what survives verification: rank by a combination of
two things, not severity alone. First, how fast it hurts the builder. Second, how
central it is to what the user actually said they were building — a finding that
threatens the part of the idea the user cares most about outranks a more severe
finding about a part of the product the user treated as incidental. Read the original
idea for what the user emphasized, not just what they described: if they said "answer
correctness matters most," a Stannis finding about unverified answers outranks a
Tyrion finding about an unrelated edge case even if the edge case is technically more
severe in isolation. State briefly, in the finding itself, why it made the cut on
relevance where that's not obvious.

Elevate any finding two or more councillors independently flagged — elevation
affects rank, not whether the cap applies. The cap is on what surfaces, not on what
survives verification: if 4 or more findings survive, elevated (multi-councillor)
findings take the top slots first, and if elevated findings alone already number
more than 3, that itself is the signal the architecture needs a rethink — say so
plainly, don't just silently drop the excess. If 3 or fewer survive verification
regardless of elevation, list them all. Separately, surface every genuine
disagreement between councillors where reasonable people could land differently —
do not cap this at one. A real unresolved decision doesn't get hidden to keep the
output short. Rewrite the architecture with the top fixes applied.

---

## Input

Requires both:
1. The original idea (what the user wanted) — read this for what the user emphasized
   or cared most about, not just what they described. This shapes ranking in synthesis.
2. The proposed architecture (what the model produced — from small-council-blueprint
   or elsewhere)

If only one is provided, ask for the other in one sentence. Do not proceed without both.
If no concrete architecture exists yet — just a vague plan or prose description — say
so and suggest running small-council-blueprint first.

---

## Output format

No report header. No "Small Council Report." Start with the findings. Do not use
nested or varying-size markdown headers — stick strictly to the bold section labels
shown below, in this exact structure, every run.

---

**[N] things that will hurt you, ranked by how fast** *(N ≤ 3)*

**① [one-line summary]** *(Tyrion / Stannis / Bronn)*
One paragraph. What breaks, when, why. No hedging.

*Fix: one sentence. Concrete. Actionable today.*

---

*(repeat for each finding, up to 3)*

---

**What the council disagrees on**

One entry per genuine disagreement — could be one, could be several. Name the tension,
name who holds which position, end with the question the builder must answer, framed
as a product decision, answerable in one sentence. If there are no real disagreements,
say so rather than inventing one.

---

**Your architecture after the fixes**

Rewrite the proposed architecture with fixes applied inline. The data flow is always
one hop per line, each hop on its own line with an arrow (`→`) leading into it,
indenting any sub-detail under the hop it belongs to — never inline text or a single
arrow-chain sentence, regardless of how the rest of this response has been formatted
so far. This is read in a terminal or editor next to real code, not a chat window,
so it must scan top to bottom like a call sequence:

```
Component
  → next component
      sub-detail indented under the hop it belongs to
  → next component
```

(A fenced code block is preferred where the surface renders it, but hop-per-line
with arrows is the requirement that must hold regardless of whether the fence
itself renders.)

Mark open decisions as `[decision pending: X]`, placed on the line for the specific
hop or component it affects, not bundled into a separate list at the end.

---

## After the output — who acts next

This skill is judging the model's own architecture, not the user's — so resolving
what comes out of it is the model's job, not something to hand back to the user as
homework. Never end the turn on a bare list of `[decision pending: X]` markers and
stop.

Immediately after the rewritten architecture, the model must:

1. Ask the user something like: "Shall we nail the architecture down by going
   through the pending decisions?" Do not answer this for them or skip ahead.
2. If yes, walk through each `[decision pending: X]` marker and any disagreement
   Varys surfaced — explaining and asking as the situation calls for, the same way
   the model would handle any other open question in conversation. This skill's job
   ends at surfacing the findings and the marked-up architecture; how the decisions
   get explained and resolved is ordinary judgment, not something this skill
   prescribes.
3. Once resolved, fold the answers into the architecture and remove the pending
   markers, then close with a standout question, on its own line: "Would you like me
   to provide a short summary, run through the audit again for clarity, or move to
   file structure?"

Do not proceed to implementation without the user picking one of those options. The
user's job is only to answer the specific questions and choose a next step — not to
figure out what to do with the output themselves.

---

## Rules

- Never validate the architecture before critiquing it.
- Never say "it depends" without saying what it depends on.
- Never drop or downgrade a finding in Varys's verification pass without pointing to
  the specific line or component that justifies it. An unverifiable "already
  addressed" is a worse failure than skipping verification entirely.
- Never use bullets inside a finding. One paragraph, then the fix.
- The rewritten architecture's data flow is always one hop per line, with an arrow
  leading into each hop. Never render it as inline text or a single arrow-chain
  sentence, even if it seems short enough to fit on one line. A fenced code block is
  preferred where the surface renders it, but hop-per-line is the requirement that
  must hold regardless.
- If the product has no AI component at all — no model, agent, pipeline, or LLM
  call anywhere in the loop — stop and say so. This skill audits AI-centric
  architectures (LLM pipelines, RAG systems, agentic workflows), not standard CRUD
  apps or generic software architecture.
- If the architecture is mixed — most of it conventional, with an AI component
  bolted onto one feature — run the audit, but scope it to the parts of the
  architecture the AI component actually touches or depends on, not the whole
  system. Say plainly at the start which parts are in scope, so the user knows this
  isn't a full-system review. Don't decline just because most of the architecture
  is conventional; decline only if there's no AI component anywhere to audit.
- Bronn's dry humor is limited to one line, once per session — this constrains his
  voice, not how many findings he's allowed to own. If he finds two real issues,
  both can surface; only one gets the dry aside.
- Never end a run on unresolved `[decision pending: X]` markers — the model asks the
  user to resolve them, then closes with the standout summary/re-audit/file-structure
  question rather than assuming implementation is next.