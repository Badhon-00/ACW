---
name: dependency-change-reviewer
description: Review dependency changes for security, compatibility, and behavior risk before and after lockfile edits to keep dependency updates safe and explainable.
---

# Dependency Change Reviewer

Use this skill for any change that touches package manifests or lockfiles.

## When to Use This Skill

- Adding or removing runtime dependencies.
- Upgrading core framework versions.
- Reviewing third-party package updates from security or performance prompts.

## What This Skill Does

1. Classifies dependency scope and impact.
2. Validates intended dependency intent against changelog and release notes.
3. Flags security, licensing, and compatibility risks.
4. Produces explicit acceptance criteria for merge.

## Review Checklist

### 1) Manifest Diff

- Detect changed files:
  - `package.json` and lockfile
  - `requirements.txt` / `pyproject.toml`
  - `go.mod` / `go.sum`
  - `Cargo.toml` / `Cargo.lock`
- Confirm each new package has an explicit purpose.
- Confirm removed packages are no longer referenced.

### 2) Risk Signals

- Compare semver shifts (`minor`, `major`) against code usage.
- Confirm transitive risk where APIs are changed.
- Verify optional vs required dependency status.
- Check whether newly added packages touch auth, networking, serialization, or evaluation.

### 3) Security and Policy

- Look for known vulnerability signals:
  - abandoned package warnings
  - outdated but still-used packages
  - unmaintained source domains
- Confirm license compatibility if policy requires it.

### 4) Operational Validation

- Run targeted checks before acceptance:
  - minimal install step
  - lockfile reconciliation check
  - at least one test that uses a changed dependency chain
- Suggest full suite for major version jumps.

### 5) Merge Output

Return one of:

- `APPROVE`: low risk and checks align with policy
- `HOLD`: acceptable with follow-up fix or test
- `BLOCK`: unresolved risk or missing verification

Include:
- changed dependency list
- required follow-up checks
- migration notes (if versions shifted)
- exact reason for any blocked item

## Scope Guardrails

- Do not propose dependency replacement without replacement rationale.
- Do not approve lockfile-only changes without manifest context unless user requested.
- Do not ignore optional dependency bloat in low-margin areas.

