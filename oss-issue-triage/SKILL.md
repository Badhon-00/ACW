---
name: oss-issue-triage
description: Triages open-source repository issues to find contribution-ready work. Classifies difficulty, estimates scope, detects duplicates, and recommends whether to claim, ask questions, or skip.
---

# OSS Issue Triage

This skill evaluates open issues (or a single issue URL) and decides whether they are good candidates for a safe, mergeable contribution. It helps agents and developers avoid trap issues: vague reports, upstream design debates, missing reproductions, and duplicates that will stall a PR.

## When to Use This Skill

- Picking a first contribution in an unfamiliar repo
- Filtering a list of "good first issue" labels before starting work
- Deciding if an issue is too large and should be proposed as smaller sub-issues
- Checking if someone already opened a PR for the issue
- Preparing clarifying questions before claiming an issue

## What This Skill Does

1. **Issue intake**: Parses title, body, labels, comments, and linked PRs
2. **Reproducibility check**: Determines if the bug or feature is actionable
3. **Scope estimate**: Classifies size (micro / small / medium / large)
4. **Duplicate scan**: Finds related issues and open PRs
5. **Contributor fit**: Rates suitability for first-time vs experienced contributors
6. **Action recommendation**: Claim, ask, split, or skip — with rationale

## How to Use

### Basic Usage

```
Triage open issues labeled "good first issue" in this repo.
Rank top 3 for a micro-PR contribution today.
```

### Single Issue

```
Triage issue #412. Should I work on it or skip?
```

### Sprint Planning

```
Review these 5 issue URLs and output a priority table for a 2-hour sprint.
```

## Triage Workflow

### 1. Gather Issue Data (read-only)

For each issue, collect:

- Title, body, labels, milestone, assignee
- Comment thread (especially maintainer responses)
- Linked PRs (`Fixes #`, `Closes #`, cross-references)
- Age and last activity date

```bash
# GitHub CLI examples (when available)
gh issue view 412 --json title,body,labels,comments,closed,state
gh pr list --search "412" --state open
```

Without `gh`, use the hosting UI or API — do not fabricate issue content.

### 2. Classification Rubric

| Signal | Interpretation |
|--------|----------------|
| `good first issue` label | Likely suitable — verify anyway |
| Maintainer says "PRs welcome" | Positive |
| `needs reproduction` / `needs info` | Skip until clarified |
| `question` / `discussion` | Not a code task |
| Assigned to someone active | Skip or coordinate |
| Open PR linked | Skip duplicate work |
| Breaking API change requested | Large — propose design first |

### 3. Scope Estimate

| Size | Typical footprint | Sprint fit |
|------|-------------------|------------|
| **Micro** | Docs, typo, single test, <30 LOC | < 1 hour |
| **Small** | Isolated bugfix, 1-3 files | 1-3 hours |
| **Medium** | Feature with tests + docs | Half day+ |
| **Large** | Cross-cutting, design needed | Not for quick contrib |

If **medium or large**, recommend splitting:

```markdown
## Suggested sub-issues
1. [test-only] Add failing case for X
2. [impl] Fix handler in module Y
3. [docs] Update API section
```

### 4. Reproducibility & Clarity Checklist

- [ ] Clear expected vs actual behavior (bugs)
- [ ] Reproduction steps or failing test named
- [ ] Affected version / environment stated
- [ ] Acceptance criteria defined (features)
- [ ] No unresolved design disagreement in comments

**Skip** if reproduction is missing and maintainers have not confirmed the bug.

### 5. Duplicate & Collision Scan

Search for:

- Same error message or component name in other issues
- Open PRs touching same files
- Closed issues with "won't fix" or duplicate resolution

Report:

```markdown
## Related items
- #398 (closed duplicate) — same root cause
- PR #405 (open) — already addresses this
```

### 6. Contributor Fit Score

| Factor | Points |
|--------|--------|
| Micro/small scope | +2 |
| Tests/documented area | +1 |
| Maintainer engagement in last 30 days | +1 |
| `help wanted` label | +1 |
| Needs design approval | -2 |
| Flaky CI history on related PRs | -1 |
| Security-sensitive area | -2 (flag for experienced only) |

**Score ≥ 3**: Good candidate  
**Score 1-2**: Proceed with clarifying questions  
**Score ≤ 0**: Skip

### 7. Output Template

For each issue:

```markdown
# Issue Triage: #412 — [title]

## Recommendation: [CLAIM | ASK | SPLIT | SKIP]

## Summary
[1-2 sentences]

## Scope: [micro | small | medium | large]
- Estimated files: N
- Estimated LOC: ~N
- Areas: `src/...`

## Signals
| Signal | Value |
|--------|-------|
| Labels | bug, good first issue |
| Last maintainer reply | 3 days ago |
| Open PRs | none |
| Repro quality | strong / weak / missing |

## Fit score: 4/6 — Good candidate

## Risks
- ...

## If claiming, first comment to post
> I'd like to work on this. Plan: add failing test in X, fix Y.
> Unless someone is already on it, I'll open a PR in [timeframe].

## Clarifying questions (if ASK)
1. ...

## Sub-issues (if SPLIT)
1. ...
```

### 8. Ranked List Template (multiple issues)

```markdown
# OSS Issue Triage — Top picks

| Rank | Issue | Size | Score | Action |
|------|-------|------|-------|--------|
| 1 | #412 Fix slugify empty input | micro | 5 | CLAIM |
| 2 | #388 Add export to CSV | small | 3 | CLAIM |
| 3 | #401 Refactor auth module | large | -1 | SKIP |

## Recommended for this sprint
Start with #412 — smallest blast radius, tests exist nearby.
```

## Decision Tree

```
Issue opened
    │
    ├─ Open PR already fixes it? → SKIP (link PR)
    │
    ├─ needs-info / no repro? → ASK or SKIP
    │
    ├─ Scope medium+? → SPLIT or defer
    │
    ├─ Maintainer hostile / wontfix? → SKIP
    │
    └─ Micro/small + clear acceptance → CLAIM
         └─ Seed workspace → safety gate → implement
```

## Example

**User**: "Triage #88 and #99 for a beginner-friendly docs contribution."

**Output**:
```markdown
# OSS Issue Triage — Top picks

| Rank | Issue | Size | Score | Action |
|------|-------|------|-------|--------|
| 1 | #88 Typo in install guide | micro | 6 | CLAIM |
| 2 | #99 Rewrite entire docs site | large | -2 | SKIP |

# Issue Triage: #88 — Typo in install guide

## Recommendation: CLAIM

## Scope: micro
- Estimated files: 1 (`docs/install.md`)
- Areas: documentation only

## If claiming, first comment to post
> Opening a small PR to fix the typo in the install step 3 command.

# Issue Triage: #99 — Rewrite docs site

## Recommendation: SKIP

## Scope: large — multi-week effort, no acceptance criteria.
Suggest asking maintainers to break into epics before contributing.
```

## Tips

- Prefer issues with recent maintainer replies — stale threads often mean stale priorities
- Read closed PRs on similar issues to learn what maintainers rejected
- ASK before CLAIM on ambiguous features — one comment saves hours
- After CLAIM, run **coding-agent-workspace-seed** before editing code
- Never start code on `question` issues without maintainer buy-in

## Common Use Cases

- Good-first-issue filtering for hackathons
- Agent routing: which issue to pick autonomously
- Weekly maintainer-style triage for a fork you steward
- Pre-contribution due diligence on bug bounty / internship tasks