---
name: oss-pr-triage
description: Triage open-source pull requests by checking template compliance, dependency risk, and maintainer-impact before in-depth review.
---

# OSS PR Triage

Use this skill when reviewing incoming PRs from outside contributors or automation bots.

## When to Use This Skill

- Before merging volunteer or bot-driven PRs.
- Before asking deeper reviewers to spend time on clearly low-signal PRs.
- For prioritizing PR queues with mixed quality.

## What This Skill Does

1. Classifies PR type and urgency.
2. Scores maintainer impact of changes.
3. Detects missing metadata and required checks.
4. Produces routing priority: quick reject, quick accept, or deep review.

## Triage Checklist

### 1) Metadata and Template

- Verify title clarity and scope.
- Confirm issue link or design note exists when change is behavioral.
- Confirm tests are included for non-doc changes.
- Confirm formatting and lint notes are present when available.

### 2) Scope and Risk

- Identify touched area:
  - docs
  - feature
  - tooling
  - dependency/security
- Flag cross-cutting or high-impact files.

### 3) Maintainer Friction

- Detect missing sign-offs, conflict risk, or style mismatch.
- Spot low-effort cleanup PRs that hide risky edits.
- Flag dependency or security changes for additional scrutiny.

### 4) Quality Signals

- Look for:
  - consistent naming
  - focused commit structure
  - minimal unrelated churn
  - clear test coverage

### 5) Final Routing

Return one priority:

- `low`: quick review and likely merge candidate
- `medium`: needs maintainer follow-up and maybe one focused revision
- `high`: requires deeper technical review or temporary hold

Include:
- one-line reason
- missing checks
- suggested assignee
- recommended response text

## Output Template

```text
PR: <link>
Priority: low | medium | high
Risk: low | medium | high
Decision: merge | conditional_merge | hold
Reasons:
- ...
Required actions:
- ...
```

