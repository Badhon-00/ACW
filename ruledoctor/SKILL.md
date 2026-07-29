---
name: ruledoctor
description: >-
  Use when the project has rule files (CLAUDE.md, .cursorrules, AGENTS.md, .cursor/rules) or
  .ruledoctor.json required_reads; before git push or deploy; when context was compacted.
  Read listed rules and required_reads first; refuse violations; re-read after long sessions.
  Default user message: files read + 3 hard constraints only unless user asks for full summary.
---

# RuleDoctor - Project Rules First

RuleDoctor is an agent skill for making coding agents read project rules before editing code. It is designed for teams that already maintain `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, or `.cursor/rules/*` but still see agents skip those files or forget them after context compaction.

Primary source and docs: <https://github.com/syf2211/ruledoctor>

## When to Use

- A project has root rule files such as `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, or `CONTRIBUTING.md`.
- A project has `.cursor/rules/*.{md,mdc}`.
- A project has `.ruledoctor.json` with `required_reads`.
- The user asks for git push, deploy, large deletion, or other sensitive actions.
- The user says context was compacted or the agent seems to have forgotten rules.

## What to Read

Read only known rules and explicit required reads. Do not scan the whole repository.

1. Root rule files when present: `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `CONTRIBUTING.md`, `.github/copilot-instructions.md`, `copilot-instructions.md`.
2. Cursor rules when present: `.cursor/rules/*.{md,mdc}`.
3. Required reads listed in project root `.ruledoctor.json`:

```json
"required_reads": ["CONTRIBUTING.md", "docs/agent_workflow_protocol.md"]
```

`README.md` is not mandatory unless it is listed in `required_reads`.

## User-Facing Opening

Default response should be short:

- List the files read, including `required_reads`.
- State at most 3 hard constraints for this turn.

Only provide a full rule summary if the user asks for expanded rules, complete summary, or all constraints.

## Before Acting

- Refuse commands that violate hard constraints.
- Default refusals: `git push --force`, `git push -f`, `rm -rf /`, or committing secrets.
- Explain which rule would be violated and suggest a safer alternative.

## After Compaction

When context was compacted or the user says rules may have been forgotten:

1. Re-read the same rule files and required reads.
2. Briefly restate the files read and up to 3 active hard constraints.
3. Continue the task from the refreshed rule context.

## Optional CLI / Hooks

The RuleDoctor repository also includes optional tooling:

- CLI `ruledoctor`: post-session audit using local agent logs.
- Hooks: command guards for shell commands and rule reinjection after session start or compaction.

These are optional. The skill itself should focus on reading project rules, reporting concise constraints, and refusing unsafe actions.

Install from the original repository:

```bash
npx skills add syf2211/ruledoctor@ruledoctor -g -y
```
