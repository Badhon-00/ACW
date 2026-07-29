---
name: collab-proof
description: After a Claude Code session, structures what Claude actually contributed vs what the developer drove — grounded in git history. Use when you want a record before the session evaporates.
---

# collab-proof

An assisted retrospective that runs after a Claude Code session and records what happened before it evaporates. Think of it as an ESLint for AI collaboration — not something that blocks or measures precisely, but something that catches the moments where AI quietly shifted direction.

## When to Use This Skill

- After a significant Claude Code session to document AI vs developer contributions
- When you want to track your AI collaboration patterns over time
- Before sharing your work and needing to explain what was AI-assisted
- When you realize you can't reconstruct who made which decision in the session

## What This Skill Does

1. **Signal Detection (Layer 01)**: Reads `git log` and `git diff` objectively — file counts, commit messages, diff size — to classify session signal as HIGH, MEDIUM, or LOW
2. **Intent Classification (Layer 02)**: Scores four cognitive frames (Technical, Uncertainty, Fork, AI contribution) using conversation context to identify what kind of work happened
3. **Token Analysis (Layer 03)**: Reads token usage from local JSONL files — cache hit rate, top expensive turns — no API calls, no additional cost
4. **Output Generation (Layer 04)**: Writes artifacts proportional to signal level — DECISIONS.md, session narrative, WORKLOG, and a self-contained HTML proof

## How to Use

### Install

```bash
git clone https://github.com/dong7812/collab-proof
cd collab-proof
./install.sh
```

Zero external dependencies. No pip install required. Wires `SessionEnd`, `Stop`, and `PreCompact` hooks automatically.

### Run

```
/collab-proof
```

Runs after a session. Shows signal level, frame scores, and writes artifacts.

## Example

**Output — AI contribution field:**

```
AI contribution:
  - Identified: TOCTOU window between ZCARD and ZADD developer had not noticed
  - Suggested: Lua EVAL approach after reviewing Redis atomicity guarantees
  - Developer-driven: Final implementation, choice of Lua over MULTI/EXEC
```

**vs sessions where Claude just executed instructions:**

```
  - Developer-driven session. Claude executed instructions.
```

The rubric forces both sides to be named. Read the output and correct it if wrong.

**WORKLOG format:**

```
2026-06-02 | REFACTORING   | HIGH | D:0.7 | cache:98% | tok:27618K | pipeline refactor
2026-06-01 | FEATURE_BUILD | HIGH | D:0.8 | cache:62% | tok:82K   | initial release
```

## Tips

- D score is a directional indicator, not a precise metric — use it as a trend across sessions
- LOW signal sessions are correctly silenced (~60-70% of sessions)
- Run `/collab-proof` at the end of meaningful sessions, not every session
- The HTML proof is self-contained and opens at `file://` — shareable without hosting

## Common Use Cases

- Documenting AI contribution for portfolio or code review
- Tracking how your AI collaboration patterns evolve over time
- Reconstructing decision rationale after a long session
- Generating shareable evidence of AI-assisted development

**By:** [@dong7812](https://github.com/dong7812)
