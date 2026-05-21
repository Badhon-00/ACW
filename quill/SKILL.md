---
name: quill
description: Two AIs in conversation — one does the work, the other gives perspective. Four thinking-partner skills for stuck, exploring, and high-stakes moments. Install via pip install quill-mcp.
---

# Quill — Thinking Partner for Claude Code

Quill runs a second AI alongside Claude so you get a second vantage point on your work. It ships four skills that cover different moments: stuck and frustrated, curious and exploring, surfacing hidden assumptions, and high-stakes decisions that need parallel review.

Research-tested: 4/4 wins on decisions-under-tension vs single AI.

Free on existing Claude Pro + ChatGPT Plus subscriptions — no extra API key needed. *By [@YG3-ai](https://github.com/YG3-ai)*

## When to Use This Skill

- You feel stuck or something about the current approach is off → `/quill:consult`
- You want a fresh angle without being stuck → `/quill:perspective`
- You want to surface what assumptions Claude made silently → `/quill:assumptions`
- High-stakes decision, architecture choice, or anything that needs parallel review → `/quill:mosaic`

## What This Skill Does

1. **`/quill:consult`**: Pause and reframe. Claude frames what it sees; Quill reframes it. You get a three-paragraph dialogue and one concrete thing to try.
2. **`/quill:perspective`**: Additive, not corrective. Brings in another vantage point when you're exploring, not when you're stuck.
3. **`/quill:assumptions`**: Surfaces what Claude decided silently — hidden constraints, skipped options, implicit trade-offs.
4. **`/quill:mosaic`**: Parallel work + mutual review. Both AIs draft independently, then critique each other. Best for high-stakes calls.

## How to Use

### Install

```bash
pip install quill-mcp
```

Then enable the Quill plugin in Claude Code.

### Basic Usage

```
/quill:consult the auth refactor feels off but I can't articulate why
```

```
/quill:perspective thinking about whether to split this into microservices
```

```
/quill:assumptions before we ship this migration
```

```
/quill:mosaic choose between REST and GraphQL for the new API
```

### Full Setup

See the [Quill GitHub repo](https://github.com/YG3-ai/quill) for complete installation, configuration, and Windows setup instructions.

## Example

**User**: `/quill:consult we've been chasing this bug for an hour and every fix creates a new problem`

**Claude** frames what it sees across the last session.

**Quill** reframes: surfaces the meta-pattern (fixing symptoms vs root cause, or wrong mental model of the system).

**Together**: one concrete thing to try — often stopping and re-reading the original spec, or checking an assumption neither party questioned.

## Tips

- Use `/quill:consult` when you feel friction, not just when there's an error
- Use `/quill:mosaic` before committing to any architectural decision
- Quill works on any backend: Claude CLI, Codex CLI, or API — configure via `.env`
- On Windows, start the bridge manually: `python bridge_server.py` in the server directory

## Common Use Cases

- Architecture decisions where you want independent analysis before committing
- Debugging sessions that have gone in circles
- Code reviews where you want a second perspective on approach, not just style
- Any moment where you suspect you might be in the wrong frame entirely
