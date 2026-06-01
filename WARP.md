# WARP.md

Warp agent guidance for the **awesome-claude-skills** repository.  
Complements `AGENTS.md`; read both before starting work.

## Repository at a Glance

| Property | Value |
|---|---|
| Type | Skill catalog — no root build system |
| Primary artifact | `SKILL.md` per skill folder |
| Languages | Markdown, Python (eval harness), JS/HTML (plugins) |
| CI enforcement | `.github/workflows/label-ready-skill.yml` |
| Contribution guide | `CONTRIBUTING.md` |

## Quick Commands

```bash
# Check what a PR touches
git --no-pager diff --name-only origin/main...HEAD

# Launch Connect plugin
claude --plugin-dir ./connect-apps-plugin

# MCP Builder evaluation
pip install -r mcp-builder/scripts/requirements.txt
python mcp-builder/scripts/evaluation.py \
  -t stdio -c python -a <server>.py \
  mcp-builder/scripts/example_evaluation.xml
```

## Skill Authoring Workflow

```
1. cp -r template-skill/ <skill-name>/
2. Edit <skill-name>/SKILL.md  →  fill in frontmatter + sections
3. Add listing to README.md    →  correct category, alphabetical order
4. git checkout -b add-<skill-name>
5. git commit -m "Add [Skill Name] skill"
6. Open PR: "Add [Skill Name] skill"
```

**SKILL.md frontmatter (required):**
```yaml
---
name: skill-name
description: One-sentence description of what this skill does and when to use it.
---
```

## Navigation Landmarks

| File/Directory | Purpose |
|---|---|
| `README.md` | Curated index — structured, do not free-edit |
| `CONTRIBUTING.md` | Full checklist for new skills |
| `template-skill/SKILL.md` | Canonical template to copy |
| `.github/workflows/label-ready-skill.yml` | CI rules for README edits |
| `composio-skills/` | Large generated collection — don't manually edit |
| `mcp-builder/` | MCP scaffold + evaluation harness |
| `connect-apps-plugin/` | Claude Code plugin for app connections |

## Boundaries

| Action | Policy |
|---|---|
| Edit existing `SKILL.md` content | ✅ OK |
| Add new skill folder + `SKILL.md` | ✅ OK |
| Update README Skills listing (alphabetical) | ✅ OK |
| Edit files inside skill support dirs | ✅ OK |
| Rename or delete a skill folder | ⚠️ Ask first |
| Edit README outside Skills section | ⚠️ Ask first |
| Modify `.github/workflows/` | ⚠️ Ask first |
| Bulk-edit `composio-skills/` | ⚠️ Ask first |
| Commit API keys / secrets | 🚫 Never |
| Add emojis to README listings | 🚫 Never |
| Add crypto / web3 skills | 🚫 Never (CI blocked) |
| Submit duplicate skills | 🚫 Never |

## Warp Agent Tips

- Use **terminal mode** to run git diff checks before any README edit.
- When authoring a skill, open `template-skill/SKILL.md` side-by-side to mirror the structure.
- Run `cat .github/workflows/label-ready-skill.yml` to understand CI constraints before touching `README.md`.
- Verify alphabetical placement with: `grep -n "^\- \[" README.md | less`
