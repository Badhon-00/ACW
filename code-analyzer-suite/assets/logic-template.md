# Logic Verification Template

## Task Header

```markdown
## Parallel Task: Logic Verification

**Focus Areas:** Business logic correctness, Boundary conditions, Error handling, State management, Data flow

**Objective:** Verify business logic correctness, edge case handling, and error paths.
```

## Analysis Checklist

- [ ] Verify business logic correctness
- [ ] Check boundary conditions and edge cases
- [ ] Validate input ranges and constraints
- [ ] Verify error handling paths
- [ ] Check state management consistency
- [ ] Validate transaction boundaries
- [ ] Check for race conditions in state changes
- [ ] Verify null/undefined/empty handling
- [ ] Check for off-by-one errors
- [ ] Validate conditional logic completeness
- [ ] Check for integer overflow/underflow
- [ ] Verify floating-point precision issues
- [ ] Check for timezone and locale handling

## Output Template

```markdown
# Logic Verification Report

## Metadata
- **Target**: {File/module}
- **Language**: {Language}
- **Score**: {1-10}/10

## Logic Analysis

### Business Rules Verified
- {List of rules checked}

## Issues Found

### Issue {N}: {Title}
- **Location**: {Location}
- **Severity**: {Critical/High/Medium/Low}
- **Category**: {Boundary/Error/State/Race/etc}
- **Description**: {Detailed description}
- **Impact**: {Functional impact}
- **Test Case**: {Failing scenario}
- **Recommendation**: {Fix approach}
- **Effort**: {Small/Medium/Large}

## Positive Findings
- {Robust handling observed}

## Testing Recommendations
1. {Additional test cases needed}
2. {Edge cases to cover}
3. {Property-based testing opportunities}
```

## Severity Guidelines
- **Critical**: Data corruption, financial impact
- **High**: Wrong business results
- **Medium**: Edge case failures
- **Low**: Minor behavioral issues
