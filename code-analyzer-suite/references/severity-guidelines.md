# Severity Rating Guidelines

## Severity Levels

Every issue identified during code analysis must be assigned one of four severity levels. This ensures consistent prioritization across all dimensions and analysts.

### Critical

**Definition**: Issues that pose immediate risk to security, data integrity, or system availability.

**Characteristics**:
- Exploitable vulnerability with no authentication required
- Data loss or corruption in production
- System crash or denial of service
- Security breach exposing sensitive data
- Compliance violation (GDPR, HIPAA, SOC2)

**Action Guidance**: Fix before deployment when the affected path is in scope. Escalate immediately if found in production.

**Examples**:
- SQL injection in authentication endpoint
- Hardcoded production database credentials
- Missing authorization check on admin endpoint
- Race condition causing financial transaction duplication
- Buffer overflow in C/C++ code

### High

**Definition**: Issues that significantly impact functionality, performance, or security under specific conditions.

**Characteristics**:
- Vulnerability requiring authentication or specific conditions
- Major performance degradation under load
- Significant logic flaw affecting core functionality
- Missing critical error handling
- Memory leak in long-running process

**Action Guidance**: Schedule as near-term work. Escalate faster when the affected path is production-facing, security-sensitive, or business-critical.

**Examples**:
- XSS vulnerability in user-generated content display
- N+1 query in frequently accessed endpoint
- Missing rate limiting on API endpoints
- Incorrect business logic in payment processing
- Unhandled promise rejection causing process crash

### Medium

**Definition**: Issues that degrade code quality, maintainability, or introduce moderate risk.

**Characteristics**:
- Code smell or anti-pattern
- Moderate complexity exceeding guidelines
- Incomplete documentation
- Missing test coverage for non-critical paths
- Suboptimal but functional implementation

**Action Guidance**: Plan within the current development cycle when it fits the team's priorities.

**Examples**:
- Function with cyclomatic complexity of 15-20
- Missing input validation on internal API
- Duplicate code blocks (3+ occurrences)
- Missing error handling for edge case
- Inefficient algorithm with limited impact

### Low

**Definition**: Minor issues that have minimal impact on functionality or risk.

**Characteristics**:
- Style inconsistency
- Missing or incomplete comments
- Minor optimization opportunity
- Documentation typo
- Non-critical formatting issue

**Action Guidance**: Address during nearby refactoring or cleanup.

**Examples**:
- Inconsistent naming convention
- Missing type hints in non-public API
- Commented-out code
- Minor whitespace or formatting issue
- Optional documentation improvement

## Severity Assignment Matrix

| Issue Type | Critical | High | Medium | Low |
|-----------|----------|------|--------|-----|
| Security vulnerability | Remote exploitable | Auth required | Defense gap | Hardening |
| Performance | System crash | Significant degradation | Suboptimal | Micro-optimization |
| Code quality | Untested critical path | High complexity | Style issue | Formatting |
| Architecture | Circular dependency | SOLID violation | Pattern inconsistency | Organization |
| Logic | Data corruption | Wrong result | Edge case | Minor behavior |

## Escalation Rules

1. **Clustering increases risk**: Several Medium issues in the same function or module may justify a High severity finding when they share a root cause or amplify each other.
2. **Repeated patterns matter**: A repeated issue pattern across the codebase may deserve higher priority than an isolated instance.
3. **Context matters**: Consider production impact, user-facing vs internal paths, data sensitivity, and blast radius.
4. **Defense in depth matters**: Missing validation at multiple layers can raise the practical severity.

## Severity Distribution Signals

Use issue counts as triage signals, not hard quality targets:

- Any Critical issue deserves immediate attention.
- A cluster of High issues usually indicates a risky release or weak review coverage.
- Many Medium issues in one area may indicate unclear ownership, weak tests, or architectural drift.
- Many Low issues alone rarely justify urgent work unless they obscure important code.
