---
name: deep-verify
description: >
  Deep adversarial verification of code changes, specifically optimized for catching
  AI-generated code issues that pass superficial tests but fail in production. Use this
  skill whenever the user wants to verify code, review AI-generated code, audit a PR or
  diff for hidden bugs, check edge cases, or validate code correctness beyond basic tests.
  Triggers on: "verify this code", "check this PR", "audit this diff", "review this
  change for bugs", "is this code production-ready", "deep review", "adversarial review",
  "find issues in this code", "check for AI bugs", "validate this implementation",
  "security audit this code", "edge case analysis". Also trigger when user is about to
  merge a PR, when they express uncertainty about code correctness, or when they say
  things like "looks right to me but can you double-check". The 66% of developers
  frustrated with "almost right" AI code need this — do not skip it when code quality
  verification is at stake.
---

# Deep Verify — Adversarial Code Verification for the AI Era

"Almost right" is the most dangerous kind of wrong. AI writes code that looks perfect,
compiles, passes tests, and explodes in production at 3 AM. This skill transforms Claude
into an adversarial code auditor that hunts for the hidden bugs AI reliably produces.

## When to Use This Skill

- You just generated code with an AI tool and want to verify it before merging
- You're reviewing a PR that was partially or fully AI-generated
- You're about to merge a change and want a second pair of adversarial eyes
- You suspect "something feels off" about a code change but can't pinpoint it
- You want a systematic security/performance/edge-case audit of a diff
- You're on call and need to quickly verify a hotfix before deploying
- You're doing code review and the volume of AI-generated code is overwhelming

## What This Skill Does

1. **Intent vs. Implementation Analysis**: Verifies the code actually does what it claims — not just what it looks like it does
2. **Edge Case Discovery**: Finds the null/empty/boundary cases AI systematically overlooks
3. **Security Audit**: Catches SQL injection, missing auth, exposed secrets, and OWASP Top 10 issues AI commonly introduces
4. **Performance Analysis**: Detects N+1 queries, O(n²) algorithms, and memory leaks that only surface at production scale
5. **Business Logic Verification**: Identifies technically-correct but business-wrong code — missing transactions, non-idempotent payments, float arithmetic for money
6. **Error Handling Review**: Finds optimistic code that assumes networks don't fail, databases don't restart, and inputs are always valid

## How to Use

### Basic Usage

```
Deep verify my last commit
```

```
Audit the diff in this PR for AI-common bugs
```

```
/verify this change — is it production-ready?
```

### Advanced Usage

```
Run a full six-dimension adversarial audit on src/payments/processor.ts.
Focus especially on transaction boundaries and idempotency — we process
real money through this path.
```

```
I just had an AI agent implement our user registration flow. The code
is in src/auth/register.ts. Deep verify it with special attention to
security (SQL injection, password handling) and edge cases (duplicate
emails, invalid inputs).
```

## Example

**User**: "Deep verify the payment processing code in my PR"

**Output** (excerpt):

> # Deep Verify Report
>
> ## Overall Verdict
> 🔴 **BLOCK** — 2 CRITICAL issues found. Do NOT merge.
>
> ### [CRITICAL] Missing Transaction Boundary
> - **Location:** `src/payments/processor.ts:142-158`
> - **Pattern:** Pattern 1.1 (Missing Transaction Boundaries)
> - **Description:** Three async database operations execute without a
>   transaction wrapper. Each commits independently.
> - **Failure Scenario:** Network fails after `createPayment()` succeeds
>   but before `saveToDatabase()` — customer charged, order lost.
>   This caused $12,400 in refunds at one company.
> - **Fix:**
>
>     const tx = await db.beginTransaction();
>     try {
>       const payment = await createPayment(order, tx);
>       await saveToDatabase(payment, tx);
>       await sendConfirmationEmail(order.email);
>       await tx.commit();
>     } catch (e) {
>       await tx.rollback();
>       throw e;
>     }
>
> ## Severity Summary
> | CRITICAL | 2 |
> | HIGH     | 3 |
> | MEDIUM   | 4 |
> | LOW      | 1 |

## The Six Dimensions

Run EVERY dimension. AI bugs hide between them.

| # | Dimension | Key Question |
|---|-----------|-------------|
| 1 | Intent vs. Implementation | Does the code actually do what it claims? |
| 2 | Edge Case Discovery | What happens with null, empty, extreme inputs? |
| 3 | Security Audit | SQL injection? XSS? Missing auth? |
| 4 | Performance Analysis | N+1 queries? O(n²)? Memory leaks? |
| 5 | Business Logic Integrity | Transactions? Idempotency? Money precision? |
| 6 | Error Handling & Resilience | What happens when the network fails at 3 AM? |

Read `references/verification-dimensions.md` for the complete framework with detailed
checklists. Read `references/ai-bug-patterns.md` first to calibrate detection instincts.

## Adversarial Mindset

**DO:**
- Assume the code WILL fail, and hunt for exactly how
- Think "what's the worst input I could feed this?"
- Imagine you're a malicious user trying to break it
- Question every assumption the code makes

**DON'T:**
- Compliment the code or say "this looks good overall"
- Skip a dimension because "this seems fine"
- Trust that passing tests means correct code

## Tips

- **Read the bug patterns catalog first.** `references/ai-bug-patterns.md` documents 10 categories of real AI-generated bugs. It calibrates your detection instincts.
- **Be specific with locations.** Every finding must include `filename:line` references. "This might have issues" is useless.
- **Show the fix.** Every issue gets concrete corrected code — not just "handle errors better" but the actual implementation.
- **When in doubt, flag it.** A false positive wastes 2 minutes. A missed critical bug costs $12,400.
- **Generate the structured report.** Use `references/report-template.md` for consistent, scannable output.
- **For large PRs**, use the Explore agent to find changed files, then audit them one by one against the six dimensions.

## Common Use Cases

- Verifying AI-generated code before merging (the #1 use case)
- Code review at AI scale — when PR volume exceeds human review capacity
- Pre-deployment safety check for critical paths (payments, auth, data mutations)
- Teaching junior developers what to look for during code review
- Security audit of new endpoints or user-facing features
- Production hotfix verification under time pressure
- Legacy codebase modification impact analysis

## Reference Files

- `references/ai-bug-patterns.md` — Catalog of 10 categories of real AI-generated bug patterns with code examples. **Read this first.**
- `references/verification-dimensions.md` — Complete six-dimension framework with detailed checklists for each dimension.
- `references/report-template.md` — Standardized output format with severity definitions and report structure.

## Credit

**Inspired by:** The collective experience of 49,000+ developers surveyed by Stack Overflow (2025), Ivan Turkovic's analysis in "Almost Solved Is the Most Dangerous Phase in Engineering," the 10x.pub engineering forum's deep-dive on AI code review bottlenecks, and countless 3 AM production incidents caused by "almost right" AI-generated code.
