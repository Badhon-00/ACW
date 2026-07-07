---
name: micro-pr-reviewer
description: Perform fast, deterministic reviews for small pull requests by checking scope, risk, correctness signals, and merge-readiness in a compact pass.
---

# Micro-PR Reviewer

Use this skill when the diff is intentionally small (roughly under 250 lines of changed code) and a fast gate is needed before broader human review.

## When to Use This Skill

- Pre-merge review of short PRs, stacked PRs, or one-file edits.
- Triage of automated bot PRs with low blast radius.
- Early quality check before full test suite.

## What This Skill Does

1. Audits the diff boundary to confirm only intended files changed.
2. Checks for correctness risks with a compact checklist.
3. Identifies likely regressions and hidden coupling.
4. Produces a clear verdict with exact follow-up actions.

## Review Flow

### 0) Scope Lock

- Verify the PR has a clear ticket or user request.
- Confirm the PR title and description match the changed files.
- Flag if the change is broader than requested.

### 1) Diff Risk Triage

- Classify files by blast radius:
  - Low: docs, tests, comments, config
  - Medium: single module/service file
  - High: interfaces, shared types, data models, auth logic, build scripts
- Confirm no unrelated files were touched.
- Confirm no debug-only or temporary files are included.

### 2) Correctness Checks

- Confirm entry/exit conditions were preserved.
- Confirm naming and behavior changes are consistent with existing call sites.
- Confirm error handling was not reduced.
- Confirm test expectations were updated if behavior changed.

### 3) Safety and Observability Checks

- Search for hardcoded credentials, secrets, and endpoint changes.
- Confirm logging and error messages remain helpful, not noisy.
- Confirm migration or schema changes include fallback or rollback notes.

### 4) Validation and Confidence

- List the exact checks to run in order of confidence:
  1. Diff-level syntax/readability check
  2. Unit tests for touched units
  3. Focused integration check (if available)
- Require passing evidence before returning PASS.

## Output

Always return one of:

- `PASS`: low-risk and ready for merge with listed checks.
- `PASS_WITH_NOTES`: functional but with non-blocking follow-up.
- `BLOCK`: must fix before merge.

Use this compact JSON schema:

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | BLOCK",
  "scope": "short description",
  "risk_level": "low | medium | high",
  "blocking_items": [],
  "non_blocking_notes": [],
  "validation": [],
  "next_step": "concise recommendation"
}
```

## Rules

- Do not invent failures not visible in diff.
- If required checks are missing, return `BLOCK` and list exact missing checks.
- Keep review scoped to one PR only; do not open planning across PR boundaries.

## Example

**Input**: small API-only PR changing one endpoint parser.

**Output**:
`verdict: PASS_WITH_NOTES`
`scope: single parser module`
`blocking_items: []`
`non_blocking_notes: ["Add one regression test for malformed input case"]`
`validation: ["targeted tests", "smoke request"]`
