---
name: skillpack-forge
description: Create, compile, verify, and package portable AI coding-agent context from one skillpack.yaml when a repository needs synchronized AGENTS.md, CLAUDE.md, Claude/Codex Skills, Cursor rules, Copilot instructions, MCP resources, or MCPB bundles.
---

# Skillpack Forge

Skillpack Forge keeps AI coding-agent instructions in sync across tools. It turns one `skillpack.yaml` manifest into generated context files for Claude, Codex, Cursor, GitHub Copilot, AGENTS.md-aware agents, and local MCP clients.

## When to Use This Skill

- A repository needs `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, Cursor rules, or Claude/Codex Skill files.
- Existing agent instruction files are drifting and should be managed from one manifest.
- A project needs a local read-only MCP server or `.mcpb` bundle for repo context.
- A team wants CI to fail when generated AI-agent context is stale.

## What This Skill Does

1. **Scans or imports repo context**: Detects package managers, languages, scripts, docs, existing agent files, and automation entry points.
2. **Creates a portable manifest**: Uses `skillpack.yaml` as the source of truth for project identity, commands, docs, workflows, and targets.
3. **Generates agent outputs**: Compiles the manifest into AGENTS.md, CLAUDE.md, Claude Skills, Codex Skills, Cursor rules, GitHub Copilot instructions, MCP resources, and MCPB bundles.
4. **Verifies freshness**: Runs doctor, diff, and strict checks so generated files stay synchronized.

## How to Use

### New Repository Context

```bash
npx skillpack-forge@latest init .
npx skillpack-forge@latest compile . --dry-run
npx skillpack-forge@latest compile .
npx skillpack-forge@latest check . --strict
```

### Existing Agent Files

```bash
npx skillpack-forge@latest import .
npx skillpack-forge@latest compile . --dry-run
npx skillpack-forge@latest compile .
```

### Starter Templates

```bash
npx skillpack-forge@latest new automation .
npx skillpack-forge@latest new data-pipeline ./data-agent-context
```

Useful templates include `automation`, `browser-automation`, `playwright-browser`, `docs-automation`, `release-automation`, `ops-automation`, `data-automation`, and `data-pipeline`.

### MCPB Packaging

```bash
npx skillpack-forge@latest compile .
npx skillpack-forge@latest mcpb .
npx -y @anthropic-ai/mcpb validate .mcp
```

## Example

**User**: "Set this repo up so Claude, Codex, Cursor, Copilot, and MCP clients all use the same project instructions."

**Output**:

```text
skillpack.yaml
AGENTS.md
CLAUDE.md
.claude/skills/<project>/SKILL.md
.codex/skills/<project>/SKILL.md
.cursor/rules/<project>.mdc
.github/copilot-instructions.md
.mcp/manifest.json
.mcp/skillpack-server.mjs
<project>.mcpb
```

## Tips

- Inspect existing files before running commands that overwrite generated outputs.
- Edit `skillpack.yaml` instead of hand-editing generated agent files.
- Run `compile --dry-run` before writing outputs in unfamiliar repositories.
- Run `check --strict` before committing or opening a pull request.
- Keep secrets, private URLs, tokens, and local-only paths out of `skillpack.yaml`.
- Keep generated MCP servers read-only unless the user explicitly asks for a different design.

## Common Use Cases

- Standardizing agent instructions across several AI coding tools.
- Publishing a reusable Claude Skill and Codex Skill from the same repo manifest.
- Creating a repo-local MCP server and MCPB bundle from existing project context.
- Adding CI protection so generated AI-agent context cannot drift.

**Inspired by:** [Skillpack Forge](https://github.com/guorunjie/skillpack-forge), an open-source CLI and GitHub Action for portable AI coding-agent context.
