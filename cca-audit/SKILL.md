---
name: cca-audit
description: "Run a 6-layer parallel code audit pipeline with non-overlapping scopes — zero duplicate findings, auto-fix, test gate, architect review."
---

# CCA-Audit — 6-Layer Parallel Code Audit Pipeline

A production-grade audit pipeline that runs 6 specialized LLM auditors in parallel on your codebase. Each auditor owns an exclusive scope so findings never overlap or contradict.

## When to Use This Skill

- Before merging a feature branch — catch security, bugs, and quality issues
- After a large refactor — verify nothing broke across 6 dimensions
- During code review — get structured, deduplicated findings with priority levels
- For compliance — ensure security is reviewed by a single authority agent

## What This Skill Does

1. Detects changed files and auto-detects language (Python, TypeScript, Go, Rust, Java, Ruby)
2. Launches 6 auditors in parallel, each with a non-overlapping scope
3. Deduplicates findings across auditors (same file:line → merge, keep highest severity)
4. Prioritizes: P1 Critical (security, data corruption) → P2 High → P3 cosmetic
5. Auto-fixes P1 and P2 findings with minimal diffs
6. Re-verifies by running your test suite and linter
7. Gates through an architect review agent (APPROVED / REVISE / BLOCKED)
8. Commits with a structured message listing all fixes

## How to Use

### Basic Usage

```
/audit-fix              # audit + fix P1+P2, defer P3 cosmetic
/audit-fix deferred     # second pass to close out deferred P3 items
/audit-fix no-fix       # report only, no fixes
```

### Advanced Usage

```
/audit-fix p1-only      # fix only critical findings
/audit-fix commit 3     # audit last 3 commits
```

## Example

**User prompt:** `/audit-fix`

**Output:**
```
## CCA Audit+Fix Complete

| Layer | Status |
|-------|--------|
| 1. Parallel Audit (6 agents) | DONE — 42 raw findings |
| 2. Consolidation | DONE — 18 unique after dedup |
| 3. Fix Plan | DONE — 12 fixes planned (P1: 3, P2: 9, P3: 6 deferred) |
| 4. Implementation | DONE — 12 fixes applied |
| 5. Re-verify | DONE — tests pass, lint clean |
| 6. Architect Gate | APPROVED |
| 7. Commit | abc1234 |
```

## The 6 Auditors

| Auditor | Checks | Does NOT Check |
|---------|--------|----------------|
| Code Quality | Type safety, DRY, complexity, naming | Security, runtime bugs |
| Bug Scanner | Null refs, race conditions, resource leaks | Security, code style |
| Security | OWASP Top 10, injection, auth, secrets | Runtime bugs, quality |
| Performance | Slow queries, hot paths, memory | Security, style |
| Documentation | Missing docs, stale comments | Debug statements |
| Environment | Config consistency, naming | Secrets (owned by Security) |

## Inspired by

Built from production usage on a live trading system. Extracted and generalized as open-source. Full source and additional variants (Codex CLI, OpenRouter Python CLI) at [github.com/GiulioDER/cca-audit](https://github.com/GiulioDER/cca-audit).

## Tips

- Run `/audit-fix` before every PR push for clean, audited code
- Use the two-pass workflow: Round 1 fixes critical issues, Round 2 (`/audit-fix deferred`) handles cosmetic items in a separate commit
- Security is the single authority — it owns all security findings, preventing duplicates with the bug scanner

## Common Use Cases

- **Pre-merge audit**: Run on feature branches before PR to catch issues early
- **Post-refactor verification**: Ensure refactoring didn't introduce bugs across 6 dimensions
- **Security review**: Get OWASP Top 10 coverage with a single command
- **Code quality gate**: Use the architect review verdict (APPROVED/REVISE/BLOCKED) as a merge gate
