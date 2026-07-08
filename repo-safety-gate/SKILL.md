---
name: repo-safety-gate
description: Runs pre-flight safety checks before a coding agent modifies a repository. Verifies clean git state, branch isolation, secret leakage, destructive command risk, and contribution boundaries.
---

# Repo Safety Gate

This skill is a mandatory pre-flight checklist before any coding agent edits files, runs builds, or pushes changes. It prevents the most common OSS contribution accidents: working on the wrong branch, committing secrets, destroying local state, or modifying files outside the contribution scope.

## When to Use This Skill

- Before an agent starts work in an unfamiliar repository
- After cloning a fork but before creating a feature branch
- Before the first `git commit` or `git push`
- When resuming work in a repo with uncommitted changes
- Before running install scripts, migrations, or bulk refactors

## What This Skill Does

1. **Repository identity**: Confirms correct repo, remote, and working directory
2. **Git hygiene**: Checks branch, upstream, uncommitted changes, and detached HEAD
3. **Secret scan**: Flags likely credentials, tokens, and private keys in diffs
4. **Destructive command guard**: Blocks or warns on risky shell operations
5. **Scope boundary**: Defines which paths the agent may touch
6. **Go / no-go verdict**: Produces an explicit safety clearance or halt

## How to Use

### Basic Usage

```
Run the repo safety gate before we start. Target: fix issue #42 in docs/ only.
```

### With Explicit Boundaries

```
Safety gate for this workspace. Allowed paths: src/parser/, tests/.
Forbidden: migrations/, .github/, package-lock.json version bumps.
```

### Before Push

```
Re-run safety gate on staged changes before push.
```

## Safety Gate Workflow

Execute these steps in order. **Stop and report** on any hard failure.

### Step 1: Confirm Location

```bash
pwd
git rev-parse --show-toplevel
git remote -v
git config --get remote.origin.url
```

Verify:

- [ ] Current directory is inside the intended repository
- [ ] `origin` points to your fork or the correct upstream (not a stale clone)
- [ ] Not accidentally inside a parent monorepo root when targeting a subproject

### Step 2: Git State

```bash
git status
git branch --show-current
git rev-parse HEAD
git log --oneline -3
```

| Condition | Severity | Action |
|-----------|----------|--------|
| Detached HEAD | Hard fail | Checkout a named branch first |
| Uncommitted changes on `main`/`master` | Hard fail | Stash, commit, or discard before branching |
| Working on default branch | Warn | Create feature branch: `contrib/<topic>` |
| Untracked build artifacts | Warn | Add to `.gitignore` or clean before commit |
| Submodules dirty unexpectedly | Warn | Investigate before proceeding |

Recommended branch pattern for OSS work:

```bash
git checkout -b contrib/<short-topic>
```

### Step 3: Secret & Sensitive File Scan

Inspect staged and unstaged diffs:

```bash
git diff
git diff --cached
```

**Hard fail** if diff contains patterns like:

- `API_KEY`, `SECRET`, `PASSWORD`, `PRIVATE_KEY`, `BEGIN RSA PRIVATE KEY`
- `.env`, `credentials.json`, `*.pem`, `id_rsa`
- Cloud provider access tokens (AWS `AKIA...`, GitHub `ghp_`, Slack `xoxb-`)

Also check:

```bash
git status --short
```

Ensure no accidental staging of:

- Local config overrides
- IDE folders (unless project standard includes them — rare)
- Large binaries or datasets not required by the task

### Step 4: Destructive Command Policy

**Never run without explicit user approval:**

| Command pattern | Risk |
|-----------------|------|
| `rm -rf`, `del /s`, `Remove-Item -Recurse -Force` | Data loss |
| `git push --force`, `git reset --hard` | Remote/history damage |
| `git clean -fdx` | Wipes untracked work |
| `DROP TABLE`, `TRUNCATE`, schema migrations | Database destruction |
| `chmod -R 777` | Permission corruption |
| Publishing packages (`npm publish`, `pypi upload`) | Irreversible release |

**Prefer safe alternatives:**

- `git stash push -m "safety-gate"` instead of hard reset
- `git checkout -- <file>` for single-file revert
- `git restore` over destructive deletes

### Step 5: Scope Boundary

Define allowed edit surface before coding:

```markdown
## Contribution Scope

**Goal**: [one sentence]
**Allowed paths**:
- path/a/
- path/b/file.ts

**Forbidden without approval**:
- lockfiles (unless dep task explicitly scoped)
- CI/CD workflows
- license files
- unrelated refactors
```

During work, re-check:

```bash
git diff --name-only
```

**Warn** if changed files fall outside allowed paths. **Hard fail** if forbidden paths are touched.

### Step 6: Environment Sanity (lightweight)

```bash
# Examples — run only what the project uses
node --version 2>/dev/null || true
python --version 2>/dev/null || true
```

- [ ] Required runtime is available (or document missing tool)
- [ ] Not running as root/admin unless required
- [ ] Network installs are expected and permitted by user

### Step 7: Verdict

```markdown
# Repo Safety Gate Report

## Repository
- Path: ...
- Remote: ...
- Branch: ...

## Verdict: [GO | NO-GO]

## Checks
| Check | Status | Notes |
|-------|--------|-------|
| Correct repo | pass/fail | |
| Branch isolation | pass/fail | |
| Clean baseline | pass/fail | |
| Secret scan | pass/fail | |
| Scope defined | pass/fail | |

## Required actions before proceeding
1. ...

## Allowed operations
- Edit: `src/...`
- Run tests: `npm test`
- Do NOT: force push, edit `.github/`
```

## Decision Tree

```
Start task
    │
    ├─ Wrong repo or remote? → NO-GO (stop)
    │
    ├─ Secrets in diff? → NO-GO (stop)
    │
    ├─ On main with dirty tree? → NO-GO (branch + clean first)
    │
    ├─ Scope undefined? → WARN (define scope, then continue)
    │
    └─ All hard checks pass → GO
```

## Example

**User**: "Safety gate before fixing a typo in README.md"

**Output**:
```markdown
# Repo Safety Gate Report

## Repository
- Path: /home/dev/foss-lib
- Remote: git@github.com:myuser/foss-lib.git
- Branch: main

## Verdict: NO-GO

## Checks
| Check | Status | Notes |
|-------|--------|-------|
| Correct repo | pass | Matches user project |
| Branch isolation | fail | On `main` |
| Clean baseline | pass | Working tree clean |
| Secret scan | pass | No staged changes |
| Scope defined | pass | README.md only |

## Required actions before proceeding
1. `git checkout -b contrib/readme-typo`
2. Re-run gate → expect GO

## Allowed operations
- Edit: `README.md`
- Do NOT: modify source or CI files
```

## Tips

- Run the gate once at session start and again before every push
- Treat "probably fine" as NO-GO for secrets and branch safety
- Keep scope narrow — the easiest way to get a PR merged
- If the repo has `CONTRIBUTING.md` or `AGENTS.md`, read it during the gate
- Log the verdict in your PR notes so maintainers see you were deliberate

## Common Use Cases

- Agent session bootstrap in a fresh clone
- Fork sync workflow before new feature branch
- Pre-push checklist for automated coding tools
- Teaching contributors safe git habits