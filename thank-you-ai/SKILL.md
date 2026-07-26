---
name: thank-you-ai
description: Turn a genuine closing "thank you" into a brief reflection — triage whether it's passing, closing, emphatic, or hollow, then keep only the note that changes the next agent's first move.
---

# Thank You, AI

Most people already say "thank you" when an AI finishes something — not for efficiency, out of habit. This skill gives that habit a job. When the thanks is a genuine close (not attached to a new request), it reflects silently, writes at most one sharp note into whatever memory system the host already uses, and closes in two to four lines. Most of the time it decides there's nothing worth writing and does nothing at all — that restraint is the point, not a gap.

Full source, license (MIT), and the detailed triage / reflection / storage reference docs live at **https://github.com/hanpulse/thank-you-ai**.

## When to Use This Skill

- You want your agent to actually close a task instead of leaving the thread hanging after the final answer
- You keep re-explaining the same gotchas, decisions, or dead ends in new conversations because nothing from the last one got carried forward
- You want a lightweight alternative to manually running a retro or asking for a summary — something that triggers on a signal you already give for free
- You work across more than one agent host (Claude Code, Codex, etc.) and want memory writes to land wherever each host already keeps its notes, instead of a separate system per tool

## What This Skill Does

1. **Detects a genuine close**: recognizes gratitude in any language, or an explicit session-end phrase, and tells it apart from a passing "thanks" that's really part of a new instruction.
2. **Triages into one of four tiers**: passing (skip, no write), closing (reflect), emphatic (reflect plus log a reusable-procedure candidate), or hollow (the user gave up — capture the failure honestly, without cheerfulness).
3. **Reflects against a strict bar**: only writes a note if it would change a cold agent's first five minutes on a similar task tomorrow. Zero notes is a valid, common outcome — it does not force a note to exist.
4. **Writes into the host's existing memory**, never a competing system — it defers to whatever convention is already in place (a memory directory, `CLAUDE.md`/`AGENTS.md`, a project's own notes) rather than inventing a new one.
5. **Closes in two to four lines**: what got done, what was learned (or "nothing new worth saving"), and — rarely — whether a repeated procedure looks worth turning into its own skill. It always asks before doing that, never creates one unprompted.

## How to Use

### Basic Usage

```
(after finishing a task)
You: thanks, that worked!
```

The skill triggers automatically once installed — no explicit invocation phrase needed.

### Advanced Usage

```
You: thanks — that's everything for today, wrap up
```

Explicit session-close phrases, in any language, trigger the same closing flow as a standalone "thank you". A "thanks" with a new request attached ("thanks, now also add tests") does **not** trigger it — the skill stays silent and keeps working.

## Example

**User**: *(after 30 minutes debugging a flaky queue worker)* "thanks, that worked!"

**Output**:
```
Done: Fixed the race condition in the queue worker retry path
Learned: retries must be idempotent — the worker doesn't dedupe by job id yet
  → saved to project/queue-worker-notes.md
```

## Tips

- Say thanks the way you normally would — there's no special syntax or trigger phrase to learn or remember.
- The highest-value case is often the least pleasant one: "never mind, thanks" after a frustrating session is treated as a real failure signal, not a polite dead end.
- If you're not sure whether a note was worth writing, that's fine — "nothing new worth saving this time" is a normal, expected outcome, not a failure of the skill.

## Common Use Cases

- Long, multi-step debugging sessions that end with a plain "thanks, that worked"
- Recurring workflows on a project where the same lesson keeps getting rediscovered from scratch in new conversations
- Teams or solo developers running the same agent across multiple hosts who want consistent, non-duplicated memory
- Catching a frustrated sign-off ("never mind, I'll do it myself") as a failure worth analyzing instead of letting it pass silently
