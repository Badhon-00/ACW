# Recording Knowledge

Persists features, decisions, and pitfalls to project-local `docs/kb/` as AI-assisted development happens.

## Install

```bash
npx skills add https://github.com/CCass/recording-knowledge
```

## Usage

Agent auto-initializes the KB skeleton (`docs/kb/{features,decisions,pitfalls,architecture}`) on first encounter in any project. Say "记录一下" to record, or let the agent proactively prompt.

Includes three-layer questioning (WHAT→WHY→ACTUAL NEED) to avoid building the wrong thing.

## Files

- `SKILL.md` — Core skill instructions
- `TEMPLATE.md` — Record template
