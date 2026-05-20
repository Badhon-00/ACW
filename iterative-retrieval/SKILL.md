---
name: iterative-retrieval
description: Progressively refine context retrieval before reading files or writing code — use the fastest, cheapest source first and only read files as a last resort.
---

# Iterative Retrieval

Use when looking for context about a topic before reading files or writing code. The goal is to find the answer at the highest rung possible — files are slow, expensive, and noisy.

## The Retrieval Ladder

Run in order. Stop when you have enough context.

**Rung 1 — Memory and notes** (fastest):
Check any session memory, `CLAUDE.md`, project docs, or notes files for the topic. If 2+ relevant pieces found, you may have enough.

**Rung 2 — Codebase search** (targeted):
`grep -r "topic" src/` or use Glob/Grep tools to find where the topic appears. Read only the matching lines, not whole files.

**Rung 3 — Specific file section** (precise):
If search found a specific file, read only the relevant section — the function, class, or block. Not the whole file.

**Rung 4 — Web / docs** (when currency matters):
If the question is about a library, API, or external tool, check the official docs or changelog before assuming you know.

**Rung 5 — Full file read** (last resort):
Only read the full file if Rungs 1–4 returned nothing useful. Read the specific section, not the whole file, wherever possible.

## Rule

Never skip to Rung 5. The codebase search is the map. Files are the territory. Read the map first.

## Common Use Cases

- Before implementing a feature: check if it already exists somewhere (Rung 2)
- Before answering a question about a library: check the docs (Rung 4)
- Before editing a function: find its definition first (Rung 2–3), not by reading the whole module
- Before adding a dependency: check if it's already used (Rung 2)

## Tips

- The ladder saves tokens and time. A grep that finds the answer in 10 lines beats reading a 500-line file.
- If Rung 2 returns too many matches, narrow the query before going to Rung 3.
- Rung 4 (web/docs) is often skipped out of confidence. Don't — APIs change.
