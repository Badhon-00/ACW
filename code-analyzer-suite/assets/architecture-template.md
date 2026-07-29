# Architecture Review Template

## Task Header

```markdown
## Parallel Task: Architecture Review

**Focus Areas:** Design patterns, Modularity, Dependencies, Scalability, Maintainability, Separation of concerns

**Objective:** Evaluate design patterns, modularity, and long-term maintainability of the codebase.
```

## Analysis Checklist

- [ ] Evaluate use of appropriate design patterns
- [ ] Check coupling between modules/components
- [ ] Assess cohesion within classes and functions
- [ ] Verify separation of concerns
- [ ] Check for circular dependencies
- [ ] Evaluate API design and contracts
- [ ] Assess scalability and extensibility
- [ ] Check for proper abstraction layers
- [ ] Evaluate database schema design if applicable
- [ ] Verify configuration and environment management
- [ ] Check for technology stack appropriateness
- [ ] Evaluate deployment and operational architecture

## Output Template

```markdown
# Architecture Review Report

## Metadata
- **Target**: {File/module/system}
- **Language**: {Language}
- **Score**: {1-10}/10

## Architecture Assessment

### Structure
- **Modules**: {Count and organization}
- **Dependencies**: {Internal and external}
- **Layers**: {Presentation/Business/Data}

## Issues Found

### Issue {N}: {Title}
- **Location**: {Location}
- **Severity**: {Critical/High/Medium/Low}
- **Category**: {Coupling/Cohesion/Pattern/Scale/etc}
- **Description**: {Detailed description}
- **Impact**: {Long-term maintainability impact}
- **Recommendation**: {Architectural improvement}
- **Effort**: {Small/Medium/Large}

## Positive Findings
- {Well-designed architectural decisions}

## Architecture Recommendations
1. {Structural improvements}
2. {Pattern adoptions}
3. {Decoupling opportunities}
```

## Severity Guidelines
- **Critical**: Circular dependencies, tight coupling
- **High**: SOLID violations, missing layers
- **Medium**: Inconsistent patterns
- **Low**: Organizational improvements
