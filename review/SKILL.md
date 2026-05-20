---
name: review
description: Code review the current branch's changes — check tests, security, placeholders, and patterns before suggesting merge.
---

# Review

Fork-aware code review checklist. Run before merging any branch. Catches missing tests, security issues, and half-finished work before they land on main.

## When to Use This Skill

- Before merging a feature branch
- When asked to review a PR or set of changes
- Before declaring a task complete

## Steps

1. **See the diff** — `git diff main...HEAD` for the full branch diff, or `git diff HEAD` for uncommitted changes.

2. **Check each changed file:**
   - Tests exist and pass for new behavior
   - No `TODO`, `TBD`, `not implemented`, `raise NotImplementedError`, or hardcoded placeholder values
   - No security issues: SQL injection, unvalidated external input, hardcoded secrets, path traversal
   - Follows existing patterns in this repo (naming, error handling, logging style)

3. **Run the tests** — run the relevant test suite. Report the result verbatim.

4. **Report the verdict:**
   - **Passed**: list what was checked, confirm green, suggest merge if appropriate
   - **Failed**: list specific files and lines that need fixing before merge

## Rules

- Never approve without running tests. "Looks right" is not a review.
- Security issues block merge. Always.
- Placeholders block merge. A `TODO` in merged code is a future bug.
- Patterns matter — code that works but doesn't fit the codebase creates drift.

## Tips

- Read the diff top-to-bottom once before forming opinions. First impressions from partial reads are noisy.
- Test coverage gaps are worth flagging even if they don't block merge — at minimum, note them.
- "Follows existing patterns" means look at adjacent code, not just the changed lines.
