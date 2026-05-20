---
name: learn
description: Extract a reusable pattern discovered during work and save it as a structured note with connections to related context — prevents rediscovering the same thing next session.
---

# Learn — Extract and Record

Use when something non-obvious was discovered: a workaround, a subtle invariant, a constraint that affects future work. Patterns that aren't written down get rediscovered — expensively.

## When to Use This Skill

- A workaround for a library or API quirk was found
- A version-specific fix or incompatibility was encountered
- An architecture pattern or gotcha emerged from debugging
- A constraint was discovered that would cost an hour if missed next time
- An integration pattern saved significant time

## What NOT to Learn

- Code patterns derivable by reading the repo
- Git history (that's what `git log` is for)
- Task state or in-progress work from this session
- Anything already documented in README or CLAUDE.md

## Steps

1. **Name the pattern** — one short title. Examples:
   - "SQLite WAL mode required for concurrent reads"
   - "Auth token expires after 15min, not 1hr as documented"
   - "Nested async context managers cause event loop deadlock in Python 3.11"

2. **Search existing notes** — check memory files, `CLAUDE.md`, and project docs for this pattern. If it exists, update instead of duplicating.

3. **Identify related context** — what does this pattern connect to?
   - The problem it solves
   - The module or system it affects
   - Similar patterns or constraints
   - Use cases that trigger it

4. **Write the pattern** — add to your memory system (memory file, `CLAUDE.md`, or project notes):
   ```markdown
   ## Pattern: <name>
   **Constraint**: <one-sentence summary of what's true>
   **Why it matters**: <what goes wrong if you ignore it>
   **Where it applies**: <module, library, version, context>
   **Discovered**: <date or session>
   ```

5. **Link related notes** — reference the related context so the pattern is discoverable from multiple directions.

6. **Confirm** — report where the pattern was written and what it connects to.

## Rules

- One pattern per note. Keep it focused.
- Links are what make patterns discoverable later. Write at least two.
- If a pattern already exists, add to it — don't duplicate.
- Patterns are active knowledge, not passive references. Write them as if explaining to a future you who has forgotten everything.

## Tips

- The "why it matters" line is the most valuable part. A constraint without consequence is trivia.
- Date-stamp patterns that are version-specific — they may stop being true.
- The test of a good pattern note: can a cold reader act on it without any other context?
