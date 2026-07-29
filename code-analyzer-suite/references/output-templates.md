# Output Templates Reference

## Issue Entry Format

Every issue found during analysis must follow this format:

```markdown
### Issue {N}: {Title}

- **Location**: {File path, line numbers, or function name}
- **Severity**: {Critical | High | Medium | Low}
- **Category**: {Specific sub-category}
- **Description**: {Detailed explanation of the issue}
- **Impact**: {What could go wrong if not fixed}
- **Recommendation**: {Specific, actionable fix}
- **Effort**: {Small | Medium | Large}
- **Example Fix**:
  ```{language}
  // Before (problematic)
  {code showing the issue}

  // After (fixed)
  {code showing the fix}
  ```
```

## Dimension Report Template

```markdown
# {Dimension Name} Analysis Report

## Metadata
- **Target**: {File/module/codebase}
- **Language**: {Programming language}
- **Analyst**: {Agent/Dimension}
- **Timestamp**: {Analysis time}
- **Dimension Score**: {1-10}/10

## Summary
{Brief overview of findings}

## Issues Found

### Issue 1: {Title}
- **Location**: {Location}
- **Severity**: {Severity}
- **Description**: {Description}
- **Recommendation**: {Recommendation}

[Additional issues...]

## Positive Findings
- {What's done well}
- {Good patterns observed}

## Recommendations
1. {Prioritized recommendation}
2. {Next recommendation}

## Appendix
- **Checklist Results**: {Which checklist items passed/failed}
- **References**: {Relevant documentation links}
```

## Consolidated Report Template

```markdown
# Consolidated Code Analysis Report

## Executive Summary
- **Overall Risk Level**: {Critical | High | Medium | Low}
- **Dimensions Analyzed**: {List of dimensions}
- **Total Issues Found**: {N}
- **Critical Issues**: {N}
- **High Issues**: {N}
- **Medium Issues**: {N}
- **Low Issues**: {N}
- **Overall Health Score**: {1-10}/10

## Risk Assessment Matrix

| Dimension | Issues | Critical | High | Medium | Low | Score |
|-----------|--------|----------|------|--------|-----|-------|
| Security | {N} | {N} | {N} | {N} | {N} | {S}/10 |
| Performance | {N} | {N} | {N} | {N} | {N} | {S}/10 |
| Code Quality | {N} | {N} | {N} | {N} | {N} | {S}/10 |
| Architecture | {N} | {N} | {N} | {N} | {N} | {S}/10 |
| Logic | {N} | {N} | {N} | {N} | {N} | {S}/10 |

## Cross-Dimensional Findings
{Issues that affect multiple dimensions}

## Prioritized Action Items

### Immediate (Critical/High)
1. [{Severity}] [{Dimension}] {Issue title}
   - {Recommendation}

### Short-term (Medium)
1. [{Severity}] [{Dimension}] {Issue title}
   - {Recommendation}

### Long-term (Low)
1. [{Severity}] [{Dimension}] {Issue title}
   - {Recommendation}

## Dimension Summaries

### Security
{Summary}

### Performance
{Summary}

### Code Quality
{Summary}

### Architecture
{Summary}

### Logic Verification
{Summary}

## Recommendations by Priority

### Must Do (This Sprint)
- {List}

### Should Do (Next Sprint)
- {List}

### Could Do (Backlog)
- {List}
```

## JSON Output Format

For programmatic consumption, dimensions can output JSON:

```json
{
  "dimension": "security",
  "target": "src/auth/login.ts",
  "language": "TypeScript",
  "score": 6,
  "issues": [
    {
      "id": "SEC-001",
      "title": "SQL Injection Vulnerability",
      "location": "src/auth/login.ts:42",
      "severity": "Critical",
      "category": "Injection",
      "description": "User input is directly concatenated into SQL query",
      "impact": "Attackers can extract all database data",
      "recommendation": "Use parameterized queries",
      "effort": "Small"
    }
  ],
  "positive_findings": [
    "Passwords are properly hashed with bcrypt",
    "Rate limiting is implemented"
  ],
  "summary": "2 critical issues require immediate attention"
}
```

## Severity Text Format

Use plain text severity labels in reports:

- **Critical**
- **High**
- **Medium**
- **Low**
