# Code Quality Analysis Template

## Task Header

```markdown
## Parallel Task: Code Quality Analysis

**Focus Areas:** Style consistency, Readability, Complexity metrics, Documentation, Test coverage, Maintainability

**Objective:** Evaluate code maintainability, readability, and adherence to best practices.
```

## Analysis Checklist

- [ ] Check naming conventions and consistency
- [ ] Evaluate code readability and clarity
- [ ] Measure cyclomatic and cognitive complexity
- [ ] Verify function and class documentation
- [ ] Check for proper type hints or annotations
- [ ] Evaluate test coverage and test quality
- [ ] Check for code duplication (DRY principle)
- [ ] Verify error handling completeness
- [ ] Check for magic numbers and string literals
- [ ] Evaluate code organization and modularity
- [ ] Check import organization and unused imports
- [ ] Verify consistent error handling patterns
- [ ] Check for dead code and commented-out code

## Output Template

```markdown
# Code Quality Analysis Report

## Metadata
- **Target**: {File/module}
- **Language**: {Language}
- **Score**: {1-10}/10

## Metrics
- **Cyclomatic Complexity**: {Max/Average}
- **Cognitive Complexity**: {Max/Average}
- **Function Length**: {Max/Average lines}
- **Test Coverage**: {Percentage}

## Issues Found

### Issue {N}: {Title}
- **Location**: {Location}
- **Severity**: {Critical/High/Medium/Low}
- **Category**: {Complexity/Style/Docs/Tests/etc}
- **Description**: {Detailed description}
- **Impact**: {Maintainability impact}
- **Recommendation**: {Specific improvement}
- **Effort**: {Small/Medium/Large}

## Positive Findings
- {Well-implemented patterns}

## Quality Improvement Plan
1. {Immediate fixes}
2. {Refactoring opportunities}
3. {Documentation additions}
```

## Severity Guidelines
- **Critical**: Untested critical paths
- **High**: High complexity, major duplication
- **Medium**: Missing docs, style issues
- **Low**: Formatting, minor improvements
