---
name: micro-pr-reviewer
description: Performs fast, focused reviews of small pull requests and patches for open-source contributions. Checks scope, correctness, tests, docs, and maintainer-friendly presentation without blocking on style nitpicks.
---

# Micro PR Reviewer

This skill reviews small, focused changes before you open or respond on a pull request. It is optimized for micro-contributions — typo fixes, docs updates, test additions, and single-file bugfixes — where a full senior review would be overkill but shipping sloppy work still wastes maintainer time.

## When to Use This Skill

- Before opening a small OSS pull request
- After an agent finishes a patch and you want a sanity check
- When a maintainer asks for changes on a micro-PR
- When you need a second pass on your own diff before pushing
- When deciding whether a change is "too big" and should be split

## What This Skill Does

1. **Scope check**: Confirms the diff matches the stated intent (issue, commit message, PR title)
2. **Correctness scan**: Looks for obvious logic errors, edge cases, and regressions
3. **Test coverage**: Verifies tests exist, run, and actually exercise the change
4. **Docs & changelog**: Flags user-facing changes missing documentation
5. **Maintainer ergonomics**: Reviews commit message, PR description, and diff noise
6. **Risk rating**: Labels the change as trivial / low / medium and recommends next steps

## How to Use

### Basic Usage

```
Review my staged changes for a micro-PR. Issue: fix null check in parseConfig.
Run git diff and tell me if this is ready to open.
```

### With PR Context

```
Review PR #142 in this repo. Focus on scope creep, missing tests, and
anything that will make a maintainer ask for another round.
```

### Post-Fix Verification

```
I addressed review comments on my docs PR. Re-review only the changed files
and confirm each comment is resolved.
```

## Review Workflow

When asked to review a micro-PR, follow this sequence:

### 1. Gather Context (read-only first)

```bash
git status
git diff
git diff --stat
git log --oneline -5
```

If a PR exists, also note: title, description, linked issue, and CI status.

### 2. Scope Gate

Ask and answer explicitly:

| Question | Pass criteria |
|----------|---------------|
| Does every changed file belong to this fix? | No drive-by refactors |
| Is the diff under ~200 lines (guideline)? | If not, recommend splitting |
| Does the PR title match the diff? | No bait-and-switch |
| Are unrelated formatting changes avoided? | Whitespace-only churn flagged |

**Block** if scope creep is detected. Recommend a separate PR for unrelated improvements.

### 3. Correctness Pass

Review for:

- Off-by-one, null/undefined, empty collection handling
- Error paths and logging (not swallowed silently)
- API contract changes without migration note
- Security: injection, path traversal, secret leakage, unsafe defaults
- Backward compatibility for public APIs

Cite specific files and lines when flagging issues.

### 4. Test Pass

```bash
# Run the narrowest relevant test command first
npm test -- path/to/test
pytest tests/test_module.py -q
go test ./pkg/... -run TestName
```

Checklist:

- [ ] New behavior has a test OR change is docs-only with justification
- [ ] Tests fail without the fix (when feasible)
- [ ] No flaky sleeps, hardcoded timestamps, or machine-specific paths
- [ ] CI commands match what maintainers run (read CONTRIBUTING.md / CI config)

### 5. Maintainer-Friendly Presentation

Evaluate:

- **Commit message**: imperative mood, explains why not just what
- **PR description**: problem, approach, how to verify, linked issue
- **Diff hygiene**: no debug prints, commented code, or `.env` files
- **Screenshots**: included for UI changes

### 6. Verdict Template

Always end with this structured verdict:

```markdown
# Micro-PR Review: [title]

## Summary
[1-2 sentences on what the change does]

## Verdict: [READY | NEEDS WORK | SPLIT PR]

## Scope
- Files changed: N
- Lines changed: +X / -Y
- Scope assessment: [focused | borderline | too broad]

## Findings

### Blockers (must fix)
- [ ] ...

### Suggestions (nice to have)
- [ ] ...

### What's good
- ...

## Tests
- Command run: `...`
- Result: [pass | fail | not run]

## Recommended next step
[Open PR | Fix blockers | Split into N PRs | Ask maintainer first]
```

## Severity Rubric

| Level | Examples | Action |
|-------|----------|--------|
| **Blocker** | Broken tests, security issue, wrong behavior | Do not open PR |
| **Major** | Missing test for logic change, unclear PR description | Fix before open |
| **Minor** | Naming, comment clarity, optional refactor | Note in PR or follow-up |
| **Nit** | Style preference without project rule | Skip unless CONTRIBUTING mandates |

Do not block micro-PRs on nits. Mention them only if the project enforces them in CI.

## Example

**User**: "Review my one-file fix for issue #88 — handle empty array in `formatItems`."

**Process**:
1. Run `git diff src/formatItems.ts tests/formatItems.test.ts`
2. Confirm only formatter + test files changed
3. Check empty array, single item, and null input cases
4. Run `npm test -- formatItems`
5. Produce verdict

**Output**:
```markdown
# Micro-PR Review: Handle empty array in formatItems

## Summary
Adds early return for empty arrays and a regression test.

## Verdict: READY

## Scope
- Files changed: 2
- Lines changed: +14 / -2
- Scope assessment: focused

## Findings

### Blockers
- None

### Suggestions
- Add issue link `#88` in PR description

### What's good
- Test covers empty and populated cases
- No unrelated changes

## Tests
- Command run: `npm test -- formatItems`
- Result: pass

## Recommended next step
Open PR with title: "fix: return empty string for empty array in formatItems"
```

## Tips

- Prefer `git diff` over reading entire files when the change is small
- Read `CONTRIBUTING.md` and one recent merged PR for project norms
- If CI is available, wait for green before calling READY
- When unsure about API design, flag as "ask maintainer" instead of redesigning
- Split docs-only and code changes when either side is non-trivial

## Common Use Cases

- Agent-generated patch review before push
- First-time contributor pre-flight check
- Quick re-review after addressing maintainer comments
- Deciding if a "small fix" grew into a refactor