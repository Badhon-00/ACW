# Code Analyzer Suite — Agent Instructions

## Purpose

The Code Analyzer Suite is a parallel multi-dimensional code analysis system that decomposes code review tasks into 5 specialized analysis dimensions, each executable in independent agent windows.

## Activation Triggers

This skill activates when the user:
- Types `/code-analyzer` followed by a code review request
- Mentions analyzing code for security, performance, quality, architecture, or logic
- Asks to review, audit, or inspect code, files, or modules
- Requests vulnerability assessment or bottleneck identification
- Asks for code quality checks or architecture review

## Usage Instructions

1. Parse the user's code input (snippet, file path, or module reference)
2. Identify the programming language
3. Determine which of the 5 dimensions are relevant based on user request
4. Generate parallel analysis tasks — one per dimension
5. Each task must include: code context, analysis checklist, and structured output template
6. Provide a consolidated report template for combining results

## Analysis Dimensions

1. **Security Analysis** — vulnerabilities, injection risks, auth issues, data exposure
2. **Performance Analysis** — bottlenecks, memory leaks, inefficient algorithms, N+1 queries
3. **Code Quality** — style consistency, complexity, documentation, test coverage
4. **Architecture Review** — design patterns, coupling, cohesion, scalability
5. **Logic Verification** — business logic correctness, edge cases, error handling

## Severity Ratings

All findings must use: Critical, High, Medium, Low

## Output Format

Each dimension produces structured output with:
- Issues found (location, severity, description, recommendation)
- Positive findings
- Optional dimension score (1-10)

The consolidated report combines all dimensions with executive summary, cross-dimensional findings, and prioritized action items.

## Reference

For full skill details, see [SKILL.md](SKILL.md).
