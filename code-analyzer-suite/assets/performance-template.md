# Performance Analysis Template

## Task Header

```markdown
## Parallel Task: Performance Analysis

**Focus Areas:** Algorithm complexity, Memory usage, Database queries, Caching strategies, Async patterns, Resource management

**Objective:** Identify performance bottlenecks, resource inefficiencies, and scalability limitations.
```

## Analysis Checklist

- [ ] Analyze time and space complexity of algorithms
- [ ] Check for N+1 query problems
- [ ] Identify memory leaks or excessive allocation
- [ ] Verify caching implementation and cache invalidation
- [ ] Check for blocking operations in async contexts
- [ ] Analyze database query efficiency and missing indexes
- [ ] Check for unnecessary computations or redundant calls
- [ ] Verify proper resource cleanup (files, connections, locks)
- [ ] Identify potential deadlock or race conditions
- [ ] Check for inefficient data structures or patterns
- [ ] Verify connection pooling configuration
- [ ] Check for memory fragmentation
- [ ] Analyze garbage collection pressure

## Output Template

```markdown
# Performance Analysis Report

## Metadata
- **Target**: {File/module}
- **Language**: {Language}
- **Score**: {1-10}/10

## Issues Found

### Issue {N}: {Title}
- **Location**: {Location}
- **Severity**: {Critical/High/Medium/Low}
- **Category**: {Algorithm/Memory/Query/Concurrency/etc}
- **Description**: {Detailed description}
- **Impact**: {Performance impact under load}
- **Benchmark**: {Measured or estimated impact}
- **Recommendation**: {Specific optimization}
- **Effort**: {Small/Medium/Large}
- **Expected Improvement**: {Percentage or time savings}

## Positive Findings
- {Efficient patterns observed}

## Optimization Roadmap
1. {Quick wins}
2. {Medium-term improvements}
3. {Long-term architectural changes}
```

## Severity Guidelines
- **Critical**: System crash, unbounded growth, deadlock
- **High**: Significant degradation under load
- **Medium**: Suboptimal but functional
- **Low**: Micro-optimization
