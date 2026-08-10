---
name: hol-guard
description: Protect local AI coding-agent workflows with HOL Guard, or scan skills, MCP servers, plugins, and agent packages before installation or release.
---

# HOL Guard

Use HOL Guard when a user wants to protect an AI coding workflow before tools run, review Guard approvals or receipts, or scan an agent skill, plugin, MCP server, or package before trusting it.

## When to Use This Skill

- Protect a local Claude Code, Codex, Cursor, Copilot CLI, Gemini, Cline, OpenCode, Kimi, Grok, OpenClaw, Hermes, Pi, Oh My Pi, ZCode, or Antigravity workflow.
- Scan a skill, plugin, MCP server, or agent package before installation.
- Review why Guard blocked or queued an action.
- Verify an agent package before release.

## Safety Rules

- Never read `.env` files or unrelated credential stores.
- Never bypass or weaken Guard approvals.
- Never execute code from a target repository just to scan it.
- Ask before installing `hol-guard` when it is not already available.
- Do not claim a workspace is protected until a Guard command proves it.
- Treat scanner findings as security evidence, not a guarantee that a package is safe.

## Install

Check whether the commands already exist:

```bash
command -v hol-guard
command -v plugin-scanner
```

If they are missing and the user wants Guard installed, prefer an isolated CLI install:

```bash
pipx install hol-guard
```

Then verify the local installation:

```bash
hol-guard status
hol-guard detect --json
```

## Protect a Local Agent

Start with detection, then install the Guard-owned integration for the agent the user is actually using:

```bash
hol-guard detect --json
hol-guard install <harness>
hol-guard status
```

Common harness names include:

- `claude-code`
- `codex`
- `copilot`
- `cursor`
- `cline`
- `gemini`
- `opencode`
- `kimi`
- `grok`
- `openclaw`
- `hermes`
- `pi`
- `omp`
- `zcode`
- `antigravity`

Prefer Guard-owned setup commands over editing agent configuration by hand.

## Scan an Agent Package

For a quick security scan:

```bash
plugin-scanner scan PATH --format markdown
```

For Agent Skill or plugin structure checks:

```bash
plugin-scanner lint PATH
plugin-scanner verify PATH
```

Use the narrowest path that contains the package the user asked to inspect. Do not run its install scripts, lifecycle hooks, or arbitrary commands first.

## Review a Blocked Action

If Guard queues or blocks work:

```bash
hol-guard approvals
hol-guard receipts
hol-guard diff <harness>
```

Only approve after reading the reason and understanding the requested scope.

## Example: Scan Before Install

**User:** "Scan this skill before I install it."

1. Check for `plugin-scanner`.
2. Ask before installing HOL Guard if the scanner is missing.
3. Run `plugin-scanner scan PATH --format markdown`.
4. Run `plugin-scanner lint PATH` and `plugin-scanner verify PATH` when release or package-structure checks matter.
5. Report the highest severity finding, affected files, and the recommended next action.

## Example: Protect Claude Code

**User:** "Protect this project while I use Claude Code."

```bash
hol-guard detect --json
hol-guard install claude-code
hol-guard status
```

Report what Guard detected, whether protection is active, and any remaining degraded checks.

## What to Report

When using Guard, summarize:

- what command ran;
- what Guard found;
- what remains blocked or risky;
- what proof exists;
- the exact next command if the user must act.

Do not claim protection, approval, or release readiness without command output proving it.

## Source

- HOL Guard: https://github.com/hashgraph-online/hol-guard
- Distribution companion: https://github.com/hashgraph-online/hol-guard-plugin
