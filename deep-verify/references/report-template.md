# Verification Report Template

Use this exact format for all verification reports. Consistency makes reports scannable
and actionable for the human reviewer.

## Report Structure

```markdown
# Deep Verify Report

## Overview
- **Files analyzed:** [count]
- **Lines changed:** [+additions/-deletions]
- **Dimensions checked:** All 6
- **Time spent:** [estimated minutes]

## Executive Summary
[2-3 sentences summarizing the most critical findings. Lead with the worst news first.
If there are CRITICAL issues, they MUST appear in the first sentence.]

## Overall Verdict
[One of the four verdicts below, with a brief justification]

🟢 **READY** — No issues found
🟡 **REVIEW** — Minor issues noted below, safe to merge after fixes
🟠 **WARNING** — Significant issues found, fix before merging
🔴 **BLOCK** — Critical issues found. Do NOT merge until resolved.

---

## Findings by Dimension

### Dimension 1: Intent vs. Implementation
[Findings or "No issues found"]

### Dimension 2: Edge Case Discovery
[Findings or "No issues found"]

### Dimension 3: Security Audit
[Findings or "No issues found"]

### Dimension 4: Performance Analysis
[Findings or "No issues found"]

### Dimension 5: Business Logic Integrity
[Findings or "No issues found"]

### Dimension 6: Error Handling & Resilience
[Findings or "No issues found"]

---

## Detailed Findings

### [CRITICAL] Finding Title
- **Dimension:** [1-6]
- **Location:** `filename.ts:42-47`
- **Pattern:** [Reference to ai-bug-patterns.md if applicable, e.g., "Pattern 4.1: N+1 Query"]
- **Description:** What's wrong and why
- **Failure Scenario:** Concrete scenario of how this fails in production
- **Fix:**
```language
// The corrected code
```

### [HIGH] Finding Title
[same format]

### [MEDIUM] Finding Title
[same format]

### [LOW] Finding Title
[same format]

---

## Severity Summary

| Severity | Count |
|----------|-------|
| CRITICAL | N     |
| HIGH     | N     |
| MEDIUM   | N     |
| LOW      | N     |
| **TOTAL**| N     |

---

## Recommended Actions

1. **[Priority]** Action item — what to fix first
2. **Action item** — what to fix next
3. **Action item** — nice-to-have improvements

---

## Positive Observations
[Brief: what was done well. Keep this section SHORT — the primary purpose is finding
bugs, not giving compliments. If you find yourself writing more than 2-3 items here,
you might not have been adversarial enough.]
```

## Severity Definitions

Use these definitions consistently:

| Severity | Definition | Example |
|----------|-----------|---------|
| **CRITICAL** | Will cause data loss, security breach, financial loss, or extended outage | SQL injection, missing transaction for payment, PII leak |
| **HIGH** | Likely to cause incorrect behavior in production, user-visible errors, or significant performance degradation | N+1 query on hot path, missing auth check, edge case that causes crash |
| **MEDIUM** | Code smell, maintainability issue, or potential future bug | Missing error handling for rare failure, unclear naming, missing test case |
| **LOW** | Style issue, minor improvement, or nitpick | Inconsistent formatting, missing comment, minor inefficiency |

## Writing Good Findings

A good finding tells a story: **what's wrong → how it fails → how to fix it.**

### Bad Example
```
The error handling is missing. Should add try/catch.
```
This is vague. The reviewer doesn't know WHERE the problem is, WHAT would fail,
or HOW to fix it.

### Good Example
```
CRITICAL: Missing transaction boundary in payment processing
- Location: `src/payments/processor.ts:142-158`
- Pattern: Pattern 1.1 (Missing Transaction Boundaries)
- Description: The `processPayment()` function performs three separate async database
  operations (create payment, save to database, send email) without a transaction
  wrapper. Each operation commits independently.
- Failure Scenario: If the network fails after `createPayment()` succeeds but before
  `saveToDatabase()` completes, the payment is charged but not recorded in the database.
  This would cause a production incident requiring manual reconciliation.
- Fix: Wrap all three operations in a database transaction with proper rollback:
  [code example]
```

## The "No Issues Found" Rule

If you find NO issues in a dimension, write "No issues found" — do NOT skip the
dimension. This proves you checked it. If you skip a dimension, the reviewer can't
tell if you forgot or found nothing.
