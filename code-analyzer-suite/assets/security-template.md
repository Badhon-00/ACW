# Security Analysis Template

## Task Header

```markdown
## Parallel Task: Security Analysis

**Focus Areas:** Authentication, Authorization, Input validation, Data exposure, Injection risks, Cryptographic practices

**Objective:** Identify all security vulnerabilities, defensive coding gaps, and potential attack vectors in the provided code.
```

## Analysis Checklist

- [ ] Check for SQL injection vulnerabilities (string concatenation, f-strings in queries)
- [ ] Verify input validation and sanitization on all external inputs
- [ ] Check authentication and authorization mechanisms
- [ ] Look for hardcoded secrets, API keys, or passwords
- [ ] Verify secure data handling (encryption, hashing)
- [ ] Check for XSS, CSRF, and other web vulnerabilities
- [ ] Verify proper error handling that doesn't leak sensitive info
- [ ] Check file upload/download security
- [ ] Verify session management and token handling
- [ ] Check for insecure dependencies or deprecated functions
- [ ] Verify CORS configuration
- [ ] Check for path traversal vulnerabilities
- [ ] Verify rate limiting and brute force protection

## Output Template

```markdown
# Security Analysis Report

## Metadata
- **Target**: {File/module}
- **Language**: {Language}
- **Score**: {1-10}/10

## Issues Found

### Issue {N}: {Title}
- **Location**: {Location}
- **Severity**: {Critical/High/Medium/Low}
- **Category**: {Injection/XSS/Auth/Crypto/etc}
- **CVE/CWE**: {Reference if applicable}
- **Description**: {Detailed description}
- **Impact**: {What an attacker could do}
- **Proof of Concept**: {Example exploit if applicable}
- **Recommendation**: {Specific fix}
- **Effort**: {Small/Medium/Large}

## Positive Findings
- {Security controls that are properly implemented}

## Security Hardening Recommendations
1. {Additional defense-in-depth measures}
```

## Severity Guidelines
- **Critical**: Remote exploitable without authentication
- **High**: Requires auth or specific conditions
- **Medium**: Defense-in-depth gap
- **Low**: Hardening opportunity
