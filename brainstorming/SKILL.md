---
name: brainstorming
description: Structured brainstorm before any plan or implementation — search existing context first, generate three approaches, recommend one, stop until confirmed.
---

# Brainstorming

Use BEFORE entering plan mode or starting any implementation. Prevents building the wrong thing.

## When to Use This Skill

- Designing a new feature or behavior
- Deciding between approaches
- Any time the right solution isn't obvious

## Steps

1. **Search existing context** — grep the codebase, check docs, read relevant files before forming opinions. Never brainstorm in a vacuum when prior context exists.
2. **State the problem** — one sentence. What are we actually solving?
3. **Generate 3 approaches** — for each: name it, state the core tradeoff in one sentence.
4. **Recommend one** — which and why in 2 sentences.
5. **Flag constraints** — does this touch areas with known gotchas (auth, migrations, external APIs, hooks, config)? Note them.
6. **Stop** — do not implement until the user confirms the approach.

## Rules

- Context search first. Never brainstorm blind.
- Three approaches minimum. Two is lazy, four is stalling.
- Constraints are hard gates, not suggestions.
- Step 6 is not optional. "I'll just start" skips the whole point.

## Tips

- The tradeoff line in step 3 is the most important part. If you can't state the tradeoff in one sentence, you don't understand the approach yet.
- The recommendation in step 4 should be opinionated. "Either could work" is not a recommendation.
- If the user rejects all three approaches, that's data — ask what's missing before generating more.
