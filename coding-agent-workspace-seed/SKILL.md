---
name: coding-agent-workspace-seed
description: Seeds a safe, reproducible workspace for coding agents contributing to open-source repositories. Sets up directory layout, context files, git branch, scope manifest, and verification commands.
---

# Coding Agent Workspace Seed

This skill bootstraps a contribution-ready workspace before a coding agent touches code. It creates the minimum structure and context an agent needs to work safely: where to edit, how to test, what to avoid, and how to hand off a reviewable patch.

## When to Use This Skill

- Starting a new OSS contribution session with Claude Code, Codex, or Cursor
- Spinning up a fresh clone for a single issue or micro-PR
- Onboarding an agent to a monorepo it has not seen before
- Parallel contributions where each task needs an isolated work folder
- After `git clone` and before any file edits

## What This Skill Does

1. **Workspace layout**: Creates a standard `.agent/` (or `agent-workspace/`) metadata folder
2. **Context harvest**: Reads README, CONTRIBUTING, CI config, and issue text
3. **Branch setup**: Creates an appropriately named feature branch
4. **Scope manifest**: Writes allowed paths, goals, and forbidden operations
5. **Command cheat sheet**: Records install, test, and lint commands
6. **Handoff template**: Prepares PR description skeleton for the end of work

## How to Use

### Basic Usage

```
Seed a coding agent workspace for issue #256 in this repo.
```

### Fresh Clone

```
I just cloned my fork. Seed workspace for a docs-only contribution
to the API reference.
```

### Multi-Repo Sprint

```
Seed workspace in repos/backend-service for bugfix scope:
only packages/auth/src/.
```

## Seed Workflow

### 1. Run Repo Safety Gate First

Before seeding, confirm GO status using the repo-safety-gate checks (or inline the same steps):

- Correct repository and remote
- Clean or intentionally stashed working tree
- Feature branch created (not default branch)

```bash
git checkout -b contrib/<issue-or-topic>
```

### 2. Harvest Project Context (read-only)

Read these files when present (skip gracefully if missing):

| File | What to extract |
|------|-----------------|
| `README.md` | Project purpose, quick start |
| `CONTRIBUTING.md` | PR rules, code style, CLA |
| `AGENTS.md` / `CLAUDE.md` | Agent-specific instructions |
| `.github/pull_request_template.md` | PR sections |
| `package.json` / `pyproject.toml` / `Makefile` | Test & lint scripts |
| CI workflow (`.github/workflows/*.yml`) | Commands maintainers expect |

### 3. Create Workspace Metadata

Create `.agent/workspace.json`:

```json
{
  "seeded_at": "2026-07-08T12:00:00Z",
  "repo": "owner/project",
  "branch": "contrib/fix-null-parser",
  "issue": "#256",
  "goal": "Fix null handling in parseConfig when input file is empty",
  "allowed_paths": [
    "src/parser/",
    "tests/parser/"
  ],
  "forbidden_paths": [
    ".github/",
    "package-lock.json",
    "migrations/"
  ],
  "commands": {
    "install": "npm ci",
    "test": "npm test -- parser",
    "lint": "npm run lint"
  },
  "review_skill": "micro-pr-reviewer",
  "safety_skill": "repo-safety-gate"
}
```

Create `.agent/NOTES.md` for running session log (empty template).

**Important**: Add `.agent/` to `.gitignore` locally if the project should not receive agent metadata. Never commit secrets into `.agent/`.

```bash
# If .gitignore exists and .agent/ is not listed:
echo ".agent/" >> .gitignore
# Only if not already tracked — do not commit local agent state upstream
```

### 4. Write Scope Manifest

Create `.agent/SCOPE.md`:

```markdown
# Contribution Scope

## Objective
[One sentence tied to issue]

## In scope
- [ ] File/path A — reason
- [ ] File/path B — reason

## Out of scope
- Refactors outside the bug
- Dependency upgrades
- CI changes

## Definition of done
- [ ] Tests added or updated
- [ ] `npm test -- parser` passes
- [ ] Micro-PR reviewer verdict: READY
- [ ] PR description filled from template
```

### 5. Generate PR Handoff Template

Create `.agent/PR_DRAFT.md`:

```markdown
## Summary
Fixes #256 — [one line]

## Problem
[What was broken]

## Solution
[What changed and why]

## How to verify
1. ...
2. ...

## Checklist
- [ ] Tests pass locally
- [ ] Scope limited to parser module
- [ ] No secrets or unrelated files
```

### 6. Record Verification Commands

Run a **read-only** smoke check when possible:

```bash
# Example — adjust per project
npm ci          # only if deps required and user approves network
npm test -- --listTests 2>/dev/null | head
```

Note failures in `.agent/NOTES.md` — do not fix unrelated broken baselines without user consent.

### 7. Seed Completion Report

```markdown
# Workspace Seed Complete

## Branch
`contrib/fix-null-parser`

## Metadata
- `.agent/workspace.json` — machine-readable scope
- `.agent/SCOPE.md` — human-readable boundaries
- `.agent/PR_DRAFT.md` — fill as you work
- `.agent/NOTES.md` — session log

## Commands
| Action | Command |
|--------|---------|
| Test | `npm test -- parser` |
| Lint | `npm run lint` |

## Next steps for agent
1. Implement only within allowed_paths
2. Re-run repo-safety-gate before commit
3. Run micro-pr-reviewer before push
4. Copy PR_DRAFT.md into PR description
```

## Directory Layout

```
repo-root/
├── .agent/                    # local agent metadata (usually gitignored)
│   ├── workspace.json
│   ├── SCOPE.md
│   ├── PR_DRAFT.md
│   └── NOTES.md
├── src/                       # project code — edit only in scope
└── tests/
```

For multi-task sprints, use sibling folders outside the repo:

```
~/contrib-sprint/
├── tracker.csv
└── repos/
    └── project/               # git clone here
```

## Example

**User**: "Seed workspace for good-first-issue: add unit test for `slugify()`"

**Output**:
```markdown
# Workspace Seed Complete

## Branch
`contrib/test-slugify`

## Metadata created
- `.agent/workspace.json`
- `.agent/SCOPE.md`
- `.agent/PR_DRAFT.md`

## Commands
| Action | Command |
|--------|---------|
| Test | `pytest tests/test_utils.py -k slugify` |

## Next steps
1. Add test in `tests/test_utils.py` only
2. Confirm test fails before implementation (if bugfix)
3. Safety gate → implement → micro-PR review → push
```

## Tips

- Keep `allowed_paths` as small as possible — agents drift without boundaries
- Prefer `contrib/<topic>` branch names; match upstream conventions if documented
- Store issue URL and acceptance criteria verbatim in `SCOPE.md`
- Re-seed (update manifest only) if scope changes mid-session
- Pair with **repo-safety-gate** at start and **micro-pr-reviewer** at end

## Common Use Cases

- Claude Code session in a newly cloned fork
- Batch OSS sprint with per-issue workspace manifests
- Teaching agents project-specific test commands
- Clean handoff from implementer agent to reviewer agent