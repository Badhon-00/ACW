# AGENTS.md

Guidance for AI coding agents (Claude Code, Codex, Warp, Copilot, etc.) working in this repository.

## Project Overview

**awesome-claude-skills** — a curated catalog of Claude Skills for Claude.ai, Claude Code, and the Claude API.  
No traditional application stack; the primary artifact in every contribution is `SKILL.md`.  
Languages present: Markdown (skills), Python (MCP Builder eval harness), JavaScript/HTML (connect plugin, theme-factory).

## Key Commands

> Run from repo root (`/Users/elorm/awesome-claude-skills`) unless noted.

```bash
# Inspect working tree
git --no-pager status
git --no-pager diff

# Confirm PR scope (listing-only PRs must touch only README.md)
git --no-pager diff --name-only origin/main...HEAD

# Launch Connect apps plugin inside Claude Code
claude --plugin-dir ./connect-apps-plugin
# then inside Claude Code:
/connect-apps:setup

# MCP Builder evaluation harness
pip install -r mcp-builder/scripts/requirements.txt
python mcp-builder/scripts/evaluation.py \
  -t stdio -c python -a my_mcp_server.py \
  mcp-builder/scripts/example_evaluation.xml

# Install skill-local dependencies (only when working on that skill)
pip install -r slack-gif-creator/requirements.txt
```

## Project Structure

```
awesome-claude-skills/
├── README.md                  ← curated index; structured — edits must stay in Skills section
├── CONTRIBUTING.md            ← authoritative contribution guide
├── .github/workflows/         ← CI; label-ready-skill.yml enforces README format rules
├── template-skill/            ← canonical new-skill scaffold (copy this first)
├── composio-skills/           ← large generated collection; don't edit manually unless asked
├── document-skills/           ← bundled docx / pdf / pptx / xlsx skills
├── connect-apps-plugin/       ← Claude Code plugin for third-party app connections
├── mcp-builder/               ← MCP server scaffold + evaluation harness
└── <skill-name>/              ← any hand-authored skill
    └── SKILL.md               ← required artifact
```

## Skill Structure

Every skill is a folder containing `SKILL.md` plus optional support dirs:

```
skill-name/            ← lowercase, hyphens only
├── SKILL.md           ← required
├── scripts/           ← optional
├── reference/         ← optional
├── templates/         ← optional
└── resources/         ← optional
```

**Required SKILL.md frontmatter:**
```yaml
---
name: skill-name
description: One-sentence description of what this skill does and when to use it.
---
```

## Code Style

Follow `template-skill/SKILL.md` exactly. One example beats a paragraph of description.

**Good** (specific, actionable):
```markdown
## When to Use This Skill

- Generating weekly status reports from Jira exports
- Summarising long meeting transcripts into action items
```

**Bad** (too vague):
```markdown
## When to Use This Skill

- When you need to do something with text
```

**README listing format** (no deviations — CI validates this):
```markdown
- [Skill Name](./skill-name/) - One-sentence description. Inspired by [Person/Source].
```
Rules: alphabetical within category, no emojis, consistent punctuation, link to the skill folder.

## Git Workflow

```bash
git checkout -b add-<skill-name>
git commit -m "Add [Skill Name] skill"
# PR title: "Add [Skill Name] skill"
```

CI (`label-ready-skill.yml`) enforces strict rules on listing-only PRs:
- Changed files must be only `README.md`
- Edits must be within the `## Skills` … `## Getting Started` region
- New bullets must link to external URLs
- Entries must be in alphabetical order
- Blocked keyword list includes crypto/web3 terms

## Testing

No repo-wide test suite. Validation is structural:

| Contribution type | What to verify |
|---|---|
| New skill | `<skill-name>/SKILL.md` exists, frontmatter valid, README listing added |
| Listing-only PR | `git diff --name-only` shows only `README.md` |
| MCP server skill | Run evaluation harness before submitting |
| Connect plugin change | Test with `claude --plugin-dir ./connect-apps-plugin` |

Always inspect CI rules before opening a PR:
```bash
cat .github/workflows/label-ready-skill.yml
```

## Boundaries

✅ **Proceed without asking:**
- Edit content within an existing `SKILL.md`
- Add a new skill folder with `SKILL.md`
- Update the README Skills listing (correct category, alphabetical)
- Add/edit files inside a skill's `scripts/`, `reference/`, `templates/`, `resources/`
- Install skill-local Python deps with `pip install -r <skill>/requirements.txt`

⚠️ **Ask first:**
- Rename or delete any existing skill folder
- Edit README sections outside the Skills listing
- Add root-level tooling files (`package.json`, `Makefile`, etc.)
- Modify `.github/workflows/`
- Bulk-edit `composio-skills/`

🚫 **Never:**
- Commit secrets, API keys, or credentials
- Use emojis in README listings
- Add crypto, web3, or blockchain skills (blocked by CI)
- Submit skills that duplicate existing catalog entries
- Skip the CONTRIBUTING.md checklist for new skills

## Key Files for Orientation

1. `README.md` — catalog index and skill categories
2. `CONTRIBUTING.md` — full contribution checklist
3. `.github/workflows/label-ready-skill.yml` — CI rules (read before any README edit)
4. `template-skill/SKILL.md` — canonical skill template
