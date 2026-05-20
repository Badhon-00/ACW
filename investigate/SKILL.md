---
name: investigate
description: Combined brainstorm + debug framework — use brainstorm mode when deciding how to build something, debug mode when something is broken.
---

# Investigate — Problem-Solving Framework

Two modes: design new solutions (brainstorm) or fix existing problems (debug). Use this when you need structured thinking before acting.

## When to Use This Skill

- **Brainstorm mode**: "How should we build this?" — designing a feature, choosing an approach, open-ended problem
- **Debug mode**: "Why is this broken?" — test failure, traceback, wrong behavior

---

## Brainstorm Mode

### Steps

1. **Search existing context** — grep the codebase, check docs and notes. Read before forming opinions.
2. **Search prior sessions** — check any notes, memory files, or session logs for prior work on this topic.
3. **State the problem** — one sentence. What are we solving?
4. **Generate 3 approaches** — for each: name it, state the core tradeoff in one sentence.
5. **Recommend one** — which approach and why, in 2 sentences.
6. **Flag constraints** — auth, migrations, external APIs, config files, hooks — note any known gotchas.
7. **Stop** — do not implement until the user confirms.

### Rules

- Context search first. Never brainstorm blind.
- Three approaches minimum. Two is lazy, four is stalling.
- Constraints are hard gates, not suggestions.

---

## Debug Mode

### Steps

1. **Search prior context** — grep for the error string or module name in codebase and notes. This bug may have been seen before.
2. **State the bug** — exact error, `file:line` if known, expected vs actual behavior.
3. **Identify reproduction** — what is the minimum input that triggers this?
4. **Hypothesize** — list 2–3 candidate causes, ranked by likelihood.
5. **Test the top hypothesis** — read the relevant file, check the line. Confirm or eliminate.
6. **Fix only what is broken** — no surrounding cleanup, no refactoring. One surgical change.
7. **Test the fix** — run the relevant test. If no test exists, write one first.
8. **Commit** — message: `fix(<module>): <what was wrong> — <why it was wrong>`

### Rules

- Never skip step 1. Prior context often contains the root cause.
- Never fix without a test. A fix without a test is just a guess.
- Step 6 is hard: surgical only. Bug fixes don't get free refactors.

---

## Tips

- If you're unsure which mode to use: brainstorm = multiple valid paths forward; debug = one specific thing that should work but doesn't.
- Both modes share the same first principle: look before you leap.
