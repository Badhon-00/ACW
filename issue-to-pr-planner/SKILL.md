---
name: issue-to-pr-planner
description: Convert issue descriptions into a concise execution plan, acceptance checklist, and PR scope map for coding agents.
---

# Issue to PR Planner

Use this skill when an issue needs to become implementation steps without broad interpretation drift.

## When to Use This Skill

- Converting bug reports into a fix plan.
- Turning feature requests into ordered delivery steps.
- Planning tests and documentation for merge-ready PRs.

## What This Skill Does

1. Extracts requirements from user problem text.
2. Builds a minimal implementation plan with milestones.
3. Defines acceptance criteria and test coverage.
4. Proposes a PR template that keeps merge scope controlled.

## Plan Process

### 1) Issue Parsing

- Pull explicit objective, expected behavior, and constraints.
- Identify assumptions and unknowns from user wording.
- Tag dependencies and stakeholders only if clearly relevant.

### 2) Scope Decomposition

- Break work into 3-6 tasks.
- Group tasks into:
  - fix path
  - validation path
  - docs/communication path
- Keep each task independently verifiable.

### 3) Risk and Boundary Definition

- Mark high-risk tasks:
  - API contract changes
  - shared utility changes
  - database or migration touchpoints
- Add "do not do" boundaries to prevent scope creep.

### 4) PR Construction

When generating the PR plan include:

- Title suggestion (small, specific)
- Summary paragraph with before/after behavior
- File-level scope list
- Test plan with command-level steps
- Rollback note for high-risk changes

### 5) Acceptance Criteria

Output explicit criteria:

- Functional criteria
- Non-functional criteria (performance, logging, safety)
- Edge-case criteria
- Review criteria

## Output Template

```
Objective:
Assumptions:
Scope:
Milestones:
- ...
Acceptance Criteria:
- ...
Risk Log:
- ...
Validation:
- ...
Merge Conditions:
- ...
```

## Useful Defaults

- Default to one PR per bounded issue.
- Default to adding at least one regression test for each behavior branch.
- Keep docs updates with behavior changes only.

