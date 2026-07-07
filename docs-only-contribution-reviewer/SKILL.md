---
name: docs-only-contribution-reviewer
description: Validate documentation-only PRs with style checks, cross-link health, terminology consistency, and clear merge criteria.
---

# Docs-Only Contribution Reviewer

Use this skill for pull requests where only documentation-like files are intended to change.

## When to Use This Skill

- Reviewing edits to `README`, guides, API docs, and changelogs.
- Enforcing doc quality before release notes or onboarding updates.
- Catching drift between examples and behavior before merge.

## What This Skill Does

1. Confirms scope is documentation-only.
2. Checks structure, clarity, and consistency against existing docs patterns.
3. Verifies examples and references remain valid.
4. Produces merge-ready status with exact follow-ups.

## Verification Steps

### 1) Scope Safety

- Confirm no source code files changed.
- Confirm no build or config files changed unless explicitly needed for docs.
- If non-doc files are touched, return `BLOCK` with re-route to code review flow.

### 2) Style and Structure

- Compare tone and formatting against nearby docs in repo.
- Verify heading structure is logical and searchable.
- Check glossary consistency for terms introduced.

### 3) Content Accuracy

- Validate commands against expected shell output syntax.
- Validate markdown tables, links, and anchor names.
- Check examples use realistic paths and current package/tool versions.

### 4) Link Integrity

- Spot obvious broken local links:
  - missing `./` or wrong relative path
  - wrong case in case-sensitive filesystems
- Flag any external link requiring access tokens or short-lived sessions.

### 5) Merge Decision

Return:

- `PASS`: documentation-only and coherent
- `PASS_WITH_NOTES`: stylistic cleanup only
- `BLOCK`: technical inaccuracies or scope mismatch

Include:
- changed docs files
- verification summary
- link checks
- required edits before merge

## Extra Rules

- For API docs, include at least one example input/output pair.
- For workflow docs, include one "what to do next" section.
- Keep diff small and avoid rewrites without value.

