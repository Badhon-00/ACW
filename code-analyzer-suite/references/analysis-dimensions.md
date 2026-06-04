# Analysis Dimensions Reference

## Overview

The Code Analyzer Suite decomposes code analysis into five specialized dimensions. Each dimension focuses on a specific aspect of code quality and can be executed independently in parallel.

## Dimension 1: Security Analysis

### Purpose
Identify vulnerabilities, security risks, and defensive coding gaps that could lead to exploitation.

### Focus Areas
- **Authentication**: Verify identity mechanisms (login, session, tokens)
- **Authorization**: Check permission enforcement (RBAC, ACLs)
- **Input Validation**: Validate all external inputs (user data, files, APIs)
- **Data Exposure**: Prevent leaks of sensitive data (PII, credentials)
- **Injection Risks**: SQL, NoSQL, Command, LDAP, XPath injection
- **Cryptographic Practices**: Proper use of encryption, hashing, randomness

### Language-Specific Security Checks

#### Python
- SQL injection via f-strings or `.format()` in queries
- Unsafe `eval()`, `exec()`, `pickle.loads()`
- Missing input validation with Flask/FastAPI/Django
- Hardcoded secrets in settings files
- Insecure deserialization

#### JavaScript/TypeScript
- XSS via `innerHTML`, `document.write()`
- Prototype pollution
- Insecure `eval()` usage
- Missing CSRF tokens
- npm package vulnerabilities

#### Java
- SQL injection in JDBC/JPA queries
- Insecure deserialization
- Missing Spring Security configuration
- Log injection
- XXE (XML External Entity) attacks

#### Go
- SQL injection via string concatenation
- Race conditions in concurrent code
- Insecure random number generation
- Missing context timeout handling
- Unsafe pointer usage

#### Rust
- Unsafe block usage
- `unwrap()` and `expect()` panic paths
- Insecure randomness
- Missing bounds checks
- Unsafe FFI boundaries

### Severity Guidelines for Security
- **Critical**: Exploitable vulnerability with no authentication required
- **High**: Vulnerability requiring authentication or specific conditions
- **Medium**: Defense-in-depth gap, missing security headers
- **Low**: Documentation of security assumptions, minor hardening

## Dimension 2: Performance Analysis

### Purpose
Identify bottlenecks, resource inefficiencies, and scalability limitations.

### Focus Areas
- **Algorithm Complexity**: Time and space complexity analysis
- **Memory Usage**: Leaks, excessive allocation, cache inefficiency
- **Database Queries**: N+1 problems, missing indexes, slow queries
- **Caching Strategies**: Cache hit rates, invalidation, stampede
- **Async Patterns**: Blocking operations, promise handling, concurrency
- **Resource Management**: File handles, connections, thread pools

### Common Performance Anti-Patterns
1. **N+1 Queries**: Loading related data in loops
2. **Memory Leaks**: Uncleaned event listeners, closures, caches
3. **Blocking Async**: Synchronous I/O in async contexts
4. **Inefficient Algorithms**: O(n^2) where O(n log n) suffices
5. **Resource Exhaustion**: Unbounded goroutines, thread creation

### Severity Guidelines for Performance
- **Critical**: System crash, unbounded resource growth, deadlock
- **High**: Significant latency impact, memory leaks in production
- **Medium**: Suboptimal queries, missing caching opportunities
- **Low**: Micro-optimizations, premature optimization concerns

## Dimension 3: Code Quality

### Purpose
Evaluate maintainability, readability, and adherence to best practices.

### Focus Areas
- **Style Consistency**: Naming, formatting, conventions
- **Readability**: Clarity of intent, cognitive load
- **Complexity Metrics**: Cyclomatic complexity, cognitive complexity
- **Documentation**: Docstrings, comments, README completeness
- **Test Coverage**: Unit tests, integration tests, edge cases
- **Maintainability**: DRY principle, single responsibility

### Quality Signals
Treat these as review signals, not automatic findings. Report an issue only when the code is hard to understand, hard to test, error-prone, or inconsistent with local conventions.

- **Cyclomatic Complexity**: High branching may hide untested paths or unclear responsibility.
- **Cognitive Complexity**: Deep conditionals, negation, and mixed abstraction levels increase review risk.
- **Function Length**: Long functions deserve attention when they combine multiple responsibilities.
- **Parameter Count**: Large parameter lists may indicate unclear boundaries or missing value objects.
- **Nesting Depth**: Deep nesting can obscure error paths and early exits.

### Severity Guidelines for Quality
- **Critical**: Untested critical paths, missing error handling
- **High**: High complexity, significant duplication
- **Medium**: Missing documentation, style inconsistencies
- **Low**: Minor formatting, optional type hints

## Dimension 4: Architecture Review

### Purpose
Evaluate design patterns, modularity, and long-term maintainability.

### Focus Areas
- **Design Patterns**: Appropriate pattern usage, anti-patterns
- **Coupling**: Inter-module dependencies, import cycles
- **Cohesion**: Single responsibility per module/class
- **Scalability**: Horizontal scaling, statelessness
- **Maintainability**: Ease of modification, testability
- **Separation of Concerns**: Layer boundaries, MVC/MVVM

### Architecture Principles
1. **SOLID**: Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion
2. **DRY**: Don't repeat yourself
3. **Simplicity**: Prefer the simplest design that satisfies current requirements.
4. **Avoid premature generality**: Do not introduce abstractions for hypothetical future needs.
5. **Law of Demeter**: Principle of least knowledge

### Severity Guidelines for Architecture
- **Critical**: Circular dependencies, tight coupling across layers
- **High**: Missing abstraction layers, violation of SOLID principles
- **Medium**: Inconsistent pattern usage, unclear module boundaries
- **Low**: Minor organizational improvements

## Dimension 5: Logic Verification

### Purpose
Verify business logic correctness, edge case handling, and error paths.

### Focus Areas
- **Business Logic**: Correctness of domain rules
- **Boundary Conditions**: Edge cases, off-by-one errors
- **Error Handling**: Exception paths, fallback behavior
- **State Management**: Consistency, transitions, race conditions
- **Data Flow**: Input validation, transformation, output
- **Concurrency**: Thread safety, atomicity, ordering

### Common Logic Errors
1. **Off-by-One**: Array bounds, loop conditions
2. **Null/Undefined**: Missing null checks
3. **Integer Overflow**: Arithmetic edge cases
4. **Race Conditions**: Unsynchronized state access
5. **Missing Defaults**: Incomplete switch/case handling

### Severity Guidelines for Logic
- **Critical**: Data corruption, security bypass, financial impact
- **High**: Incorrect business results, broken core functionality
- **Medium**: Edge case failures, incomplete validation
- **Low**: Minor behavioral inconsistencies

## Cross-Dimensional Relationships

Some issues span multiple dimensions:
- **Missing input validation**: Security + Logic
- **SQL injection**: Security + Performance (if using parameterized queries)
- **High complexity**: Quality + Architecture + Logic
- **Race conditions**: Logic + Performance + Security

When an issue spans dimensions, report it in the most relevant dimension and reference it in the consolidated report's cross-dimensional findings section.
