# Report Templates

Use the shortest template that satisfies the requested depth.

## Quick Report: Levels 1-2

```markdown
# POTATO Quick Review: [artifact]

**Verdict:** [ACCEPTED / REVISION REQUIRED / BLOCKED]
**Depth:** [1 or 2]
**Artifact Profile:** [profile]

## Blocking Issues
[None, or list with evidence.]

## Material Risks
[None, or list with evidence.]

## Bottom Line
[Short readiness judgment.]
```

## Standard Report: Levels 3-7

```markdown
# POTATO Review Report: [artifact]

**Verdict:** [ACCEPTED / ACCEPTED WITH MINOR RISKS / REVISION REQUIRED / BLOCKED]
**Depth:** [1-10]
**Artifact Profile(s):** [profiles]
**Harsh Mode:** Enabled. Findings lead; every pass and failure requires evidence.
**Governing Spec:** [prompt/rubric/checklist/user requirements]
**Artifact(s) Reviewed:** [files, versions, render outputs]
**Verification Limits:** [tools/files unavailable, if any]
**Date Checked:** [exact date]

## Blocking Issues
[None, or ordered list with evidence and fix.]

## Material Risks
[Deductible or operationally meaningful risks.]

## POTATO Findings
| Variant | Position | Dimension | Finding | Evidence | Status |
|---|---|---|---|---|---|
| Coursework artifact audit | P | Provenance | ... | ... | PASS/FAIL/N/A |
| Coursework artifact audit | O1 | Omissions | ... | ... | PASS/FAIL/N/A |
| Coursework artifact audit | T1 | Tensions | ... | ... | PASS/FAIL/N/A |
| Coursework artifact audit | A | Accuracy | ... | ... | PASS/FAIL/N/A |
| Coursework artifact audit | T2 | Transfer | ... | ... | PASS/FAIL/N/A |
| Coursework artifact audit | O2 | Organization | ... | ... | PASS/FAIL/N/A |

## Required-Spec Compliance
[Prompt/rubric/checklist coverage map.]

## Accuracy And Integrity Checks
[Citations, facts, source symmetry, metadata, render/layout, tests, or command evidence.]

## Prioritized Fix List
1. MUST-FIX: ...
2. SHOULD-FIX: ...
3. NICE-TO-HAVE: ...

## Bottom Line
[Short readiness judgment.]
```

## High-Rigor Additions: Levels 8-10

Add these sections when applicable:

```markdown
## Argument Quality
[Claim, grounds, warrant, backing, qualifier, rebuttal.]

## Source And Citation Integrity
[Citation-reference symmetry, source-to-claim trace, authority, recency, bias.]

## Methodology Or Evidence Strength
[Method fit, limitations, risk of bias, statistical/empirical discipline.]

## Memory Use
[Loaded profiles and active overrides only. Do not echo raw memory.]

## Dual-Pass Verification
| Pass | Focus | Result | Evidence |
|---|---|---|---|
| 1 | Structure/spec/readiness | ... | ... |
| 2 | Sources/references/accuracy | ... | ... |
```
