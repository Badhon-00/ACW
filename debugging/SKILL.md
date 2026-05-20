---
name: debugging
description: Systematic bug hunt — search for prior context before reproducing, fix only what is broken, never ship a fix without a test.
---

# Debugging

Structured approach to finding and fixing bugs. Prevents guessing, scope creep, and fixes-without-tests.

## When to Use This Skill

- A bug is reported or a test fails
- Unexpected behavior occurs
- You're about to start changing code without a clear hypothesis

## Steps

1. **Search for prior context** — grep the codebase or your notes for the error message or module name. This bug may have been seen before.
2. **State the bug** — exact error, `file:line` if known, expected vs actual behavior.
3. **Identify the smallest reproduction** — what is the minimum input that triggers this?
4. **Hypothesize** — list 2–3 candidate causes, ranked by likelihood.
5. **Test the top hypothesis first** — read the relevant file, check the relevant line. Confirm or eliminate.
6. **Fix only what is broken** — no surrounding cleanup, no refactoring. One surgical change.
7. **Run the relevant test** — confirm the fix holds. If no test exists, write one first.
8. **Commit** — message: `fix(<module>): <what was wrong> — <why it was wrong>`

## Rules

- Never skip step 1. Prior context often contains the root cause.
- Never fix without a test. A fix without a test is just a guess.
- Step 6 is a hard constraint: surgical only. Bug fixes don't get free refactors.

## Tips

- If you can't reproduce it in step 3, you don't understand it yet. Don't fix what you can't reproduce.
- Two hypotheses is enough. Three is a sign you need more data, not more guesses.
- The commit message format (`fix(<module>): what — why`) is the most useful part of the git log six months from now.
