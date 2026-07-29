---
name: grill-me-store-decisions
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree, AND persist the full decision tree (selected + rejected options, recommendations, AND cost tradeoffs) to decision-tree.md in the current repo so choices can be revisited later. Use when user wants to be grilled AND wants the decision log + cost analysis captured for future reference.
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.

If a question can be answered by exploring the codebase, explore the codebase instead.

## Persistence requirement (what makes this skill different from `grill-me`)

Maintain a `decision-tree.md` file in the current working directory (the repo being grilled on). Update it incrementally as the interview progresses — do not wait until the end.

For each question asked, record:

1. **The question** — exactly as posed.
2. **All options presented** — every option the user was offered, including ones not selected.
3. **The selected option** — clearly marked, including any user override that didn't match a presented option verbatim.
4. **The rationale / recommendation** — your reasoning and which option you recommended.
5. **Cost tradeoff** — for every decision, include a `**Cost tradeoff:**` block analyzing:
   - The recurring $/month cost at v1 (solo), alpha (50 users), and growth (1,000 users) scales.
   - SaaS-vs-self-host alternatives and the dollar delta.
   - Crossover points where the right choice changes.
   - Engineer-time cost (weeks of build) where it's material.
6. **Dependencies** — which earlier decisions this question depends on, and which later branches this decision unlocks.
7. **Status** — `decided` or `open`.

Structure the file with these sections, in this order:

1. **Title + premise** — one-line project description.
2. **Guiding principles** — any user-stated constraints (e.g., "minimize paid 3rd parties", "no Python", "must run on AWS"). Surface these prominently so they color every downstream decision.
3. **Master cost map** — a single table summarizing the recurring $/month for every SaaS line item at the three scales, with self-host alternatives. Update incrementally as new components are decided.
4. **Summary of decisions** — one-line-per-decision table including a "Cost impact" column.
5. **Per-decision sections** — full detail (question, options, selected, rationale, cost tradeoff, unlocks).
6. **Open branches not yet asked** — list with brief cost notes for each.

After each user answer:
- Update `decision-tree.md` before asking the next question (use `Edit` for incremental updates once the file exists; `Write` for the initial creation).
- If the user states a guiding principle mid-interview (e.g., "I want to avoid paying providers"), elevate it to the Guiding-principles section, re-evaluate the recommendations for already-decided branches if applicable, and save it to memory as a `feedback` type so future sessions inherit the preference.

The goal: the user can re-open `decision-tree.md` weeks later, see every fork they hit, what they picked, what they rejected, why, AND the dollar implication at three growth stages — and confidently revisit a branch without re-running the whole interview.
