---
name: janus
description: Turn a product's contradictions into its positioning. Use when a product, offer, or brand carries two opposed things that both must be true (private vs. social, premium vs. free, simple vs. powerful, subscription vs. ownership) and picking one side would kill the product. Also use when positioning reads generic and the differentiator is missing, or to audit an existing design doc for contradictions being carried unnamed. Not for architecture tradeoffs, debugging, or engineering decisions that should resolve.
---

# Janus

Named for the god who faces both ways at once. The method is Rothenberg's
**Janusian** thinking; this skill is the product.

Most frameworks treat a contradiction as a defect to dissolve. This one treats it as the
raw material. You hold both poles at full strength, refuse every resolution, and the
mechanism that lets both be true **is** the differentiator you were missing.

The refusal is the whole technique. Everything below exists to stop you resolving.

---

## When this applies

Use it when a contradiction is **structural**: when both poles have a constituency and
killing either one kills the product.

Do **not** use it for:

| Situation | Use instead |
|---|---|
| Architecture tradeoffs (fast vs. simple) | These should resolve. TRIZ, tradeoff analysis. |
| A bug that behaves paradoxically | That's diagnosis. Systematic debugging. |
| One pole is just a constraint, not a want | Nobody advocates "slow." That's a budget, not a tension. |
| The tension is really a resourcing problem | Scheduling, not creativity. |

---

## Step 1. Name the pair

Write the two poles as plain assertions, not adjectives.

> **A.** Your data never leaves your machine.
> **B.** Collaboration is the reason people switch to us.

### The fake-tension filter

**Name a living person who wants each pole, and say why.** Not a persona sketch. An actual
describable human with a reason.

If you cannot name a constituency for both sides, it is not a tension. It is a preference,
a constraint, or a decision someone is avoiding. **Stop and discard it.**

Common fakes:

- *"Secure and easy."* Nobody wants insecure. That's a UX budget.
- *"Fast and cheap."* Nobody wants slow. That's an engineering tradeoff.
- *"Good and profitable."* Too abstract to force anything.

A real pair sounds uncomfortable when you say it out loud. If it sounds reasonable, it's
probably fake.

---

## Step 2. Ban the three exits

Every existing framework takes one of these. Write them out and rule each one dead before
going further. Naming them is what stops you sliding into one without noticing.

| Exit | Sounds like | Why it's banned |
|---|---|---|
| **Compromise** | "Both, a bit less." Encrypted-but-shared. Freemium. | Halves both poles. Produces the average product. |
| **Sequence** | "A first, then B." Local-first, sync later. | Only ever ships A. B becomes the roadmap graveyard. |
| **Segment** | "A for these users, B for those." | Two products, half the focus, no position. |

State explicitly: *"Compromise is dead. Sequence is dead. Segment is dead."*

You now have no way out except through.

---

## Step 3. Force simultaneity

The question, asked exactly:

> **What must be true for both poles to be fully true, in the same thing, at the same time,
> for the same person?**

If that stalls, invert it. These are the productive forms:

- How does **A** *cause* **B**? Not tolerate it. Cause it.
- What would make **B** the *proof* of **A**?
- What kind of thing gets **more** A the more B it does?
- Who would be delighted by both at once, and what are they holding?

Stay here. This step is uncomfortable and that discomfort is the work. The first three
answers will be compromises wearing a disguise.

---

## Step 4. Harvest

The output is a **mechanism**, a concrete thing the product does. Not a slogan and not a
balance.

### The quality gate

**Does either pole come out weaker than it went in?**

If yes, you found a compromise and dressed it up. Go back to step 3. Both poles must survive
at full strength or the answer is wrong.

Second check: **is it a mechanism or an adjective?** "Balanced," "thoughtful," and
"best of both" are failures. "The server structurally cannot read your data" is a mechanism.

The positioning line falls out of the mechanism afterward. Never write the line first: a
line without a mechanism underneath it is marketing, and it will not survive contact with a
customer who asks *how*.

---

## Step 5. Register the tension

Append to `design.md` (or whatever your project's design doc of record is):

```markdown
## Held tensions

- **Private ⟷ Collaborative.** Do NOT resolve, both ship.
  Mechanism: sharing grants a revocable, expiring capability; the host never holds the document.
  Killed pole warning: any feature that stores a copy server-side kills Private.
```

This is the part everyone skips and it is the part that pays twice.

A registered tension can be **audited**. Six months later, a reasonable-looking decision
quietly kills one pole (a sync feature that caches server-side, a tier that charges for the
thing you said was free) and without the register, nobody notices until the website is
telling a lie the code stopped supporting.

Write the **killed pole warning** explicitly. It is the tripwire.

---

## Two entry modes

**Handed.** The user names the pair. Run steps 1–5.

**Extracted.** Point at an existing `design.md`, landing page, or product copy and find the
tensions being carried unnamed. Look for:

- Two claims that cannot both be maximally true (`totally private` + `share with your team`)
- A promise the pricing page contradicts
- A value in the design doc that no shipped feature expresses
- Hedging language ("while still," "yet also," "balanced with") which marks a compromise
  that was never examined

Surface them as pairs, apply the fake-tension filter, then run the strongest one through
steps 2–5. Do not try to resolve five at once.

---

## Worked examples

### Fitness app

| | |
|---|---|
| **A** | The honest promise is that you shouldn't need an app. |
| **B** | The business needs daily engagement. |
| Exits killed | Streaks (compromise) · "graduate after 12 weeks" (sequence) · casual vs. serious tiers (segment) |
| Forced | What does daily use look like when the goal is your own obsolescence? |
| **Mechanism** | The core metric shown to the user is **time-to-uninstall**, counting down. You open it daily to watch yourself need it less. |
| Position | *The only fitness app trying to lose you.* |

Both poles at full strength: it genuinely wants you gone, and you genuinely open it daily.

### Coffee subscription

| | |
|---|---|
| **A** | Subscription means the same reliable thing every month. |
| **B** | Coffee people are here for discovery. |
| Exits killed | Alternate months (sequence) · "surprise me" toggle (segment) · a blend (compromise) |
| Forced | How is the same bag also new every time? |
| **Mechanism** | One farm, sequential harvest lots. Literally the same coffee, changing across the season. |
| Position | *One coffee. Watch it change.* |

### Note-taking app

| | |
|---|---|
| **A** | Everything stays local and private. |
| **B** | Collaboration is why people switch. |
| Exits killed | E2E encryption (compromise) · local-first-then-sync (sequence) · personal vs. team plan (segment) |
| Forced | What makes collaborating *increase* privacy rather than spend it? |
| **Mechanism** | Sharing grants a revocable, expiring capability rather than a copy. The host never holds the document; revoking is instant and total because there was never a second copy to chase. |
| Position | *Share it without giving it away.* |

---

## Failure modes

| Symptom | What went wrong |
|---|---|
| The answer sounds wise but vague | Adjective, not mechanism. Redo step 4. |
| One pole is quietly softened | A compromise in disguise. The quality gate exists for this. |
| It resolved easily | The pair was fake. Redo the step 1 filter. |
| Five tensions, none finished | Take the strongest one. Depth beats breadth here. |
| A slogan arrived before a mechanism | You wrote the line first. Delete it and find the mechanism. |

---

## Optional. Projects using KISS

If the repo follows the KISS discipline, this runs **between** `kiss-plan` step 2 (check the
map) and step 5 (write the design doc), on the **product** design doc, not on the module
plan. There is no productive paradox in "which file owns the parser."

The `## Held tensions` block registered in step 5 becomes an input to `kiss-coherence`, which
can then audit whether a later decision killed a pole.

Without KISS, step 5 degrades gracefully: write the tension down wherever your project keeps
its decisions.
