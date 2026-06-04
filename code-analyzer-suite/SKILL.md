---
name: code-analyzer-suite
description: Analyze code through focused review dimensions such as security, performance, code quality, architecture, and logic verification. Use when the user asks to review, audit, inspect, analyze, or assess code snippets, files, modules, pull requests, or whole repositories for vulnerabilities, bottlenecks, correctness bugs, maintainability risks, architecture issues, tests, or best practices. Use as a specialized code-review decomposition skill; for non-code parallel planning use parallel-decomposer-skill instead.
---

# Code Analyzer Suite

Use this skill to produce focused, evidence-based code analysis. It can either run as a single review or generate parallel worker prompts for separate analysis dimensions.

## Workflow

1. Identify the analysis target.
   - Determine whether the target is an inline snippet, file, directory, module, pull request, or whole repository.
   - Inspect local files when paths are available.
   - Determine language, framework, runtime, and test surface from the codebase rather than guessing.

2. Select only useful dimensions.
   - Use explicit user requests first.
   - For broad requests like "review this" or "analyze this code", start with the 2-3 highest-value dimensions based on risk.
   - Use all five dimensions only when the user asks for "all dimensions", "full audit", "comprehensive review", or the target is large enough to justify parallel review.

3. Analyze with evidence.
   - Prefer concrete file and line references.
   - Separate confirmed findings from hypotheses.
   - Do not report generic advice as an issue unless it is tied to observed code.
   - Include positive findings briefly when they help calibrate the report.

4. Generate parallel tasks when useful.
   - Create one task per selected dimension.
   - Produce a short handoff brief for fresh agent threads before listing dimension tasks.
   - Make each task self-contained enough for a fresh agent, but keep context compact.
   - Tell each task to read the handoff brief first, then focus only on its assigned dimension.
   - Assign ownership when two dimensions touch the same concern, such as auth logic spanning security and correctness.
   - Provide a consolidation template after the task blocks.

5. Consolidate results.
   - Deduplicate overlapping findings.
   - Keep the highest justified severity.
   - Merge related fixes into one action item when the same root cause appears in multiple dimensions.
   - Rank by user impact, exploitability, likelihood, and fix urgency.

## Dimensions

| Dimension | Use When | Focus |
| --- | --- | --- |
| Security | security, vulnerability, auth, injection, secrets, XSS, CSRF, crypto | Authentication, authorization, input validation, data exposure, dependency risk |
| Performance | performance, bottleneck, slow, memory, N+1, caching | Complexity, memory use, database queries, async behavior, rendering cost |
| Code Quality | quality, maintainability, style, complexity, tests, docs | Readability, cohesion, duplication, testability, documentation, local conventions |
| Architecture | architecture, design, coupling, boundaries, scalability | Module boundaries, dependencies, layering, API shape, long-term maintainability |
| Logic Verification | bug, correctness, edge case, error handling, state | Business rules, boundary cases, null handling, failure paths, state transitions |

## Severity

Use this scale for every issue:

| Severity | Meaning |
| --- | --- |
| Critical | Exploitable vulnerability, data loss, system crash, or severe correctness failure likely in production |
| High | Significant security, correctness, performance, or maintainability risk that should be fixed soon |
| Medium | Real issue with moderate impact or localized risk |
| Low | Minor cleanup, hardening, or clarity improvement |

## Output Shape

For direct analysis, lead with findings:

```markdown
## Findings

1. [Severity] {Title} - {file:line}
   {Why this is a problem, what can happen, and the concrete fix.}

## Open Questions
{Only include if uncertainty affects the recommendation.}

## Notes
{Brief positives, scope limits, or test gaps.}
```

For parallel analysis, use:

```markdown
## Handoff Brief
Target: {files/modules}
Shared context: {language, framework, relevant architecture, constraints}
Scope: {what is included and excluded}
Worker rule: Read this brief before starting your dimension review.

## Parallel Task 1: {Dimension}
Target: {files/modules}
Context: Read the Handoff Brief first. {minimum dimension-specific facts}
Prompt: {copy-paste-ready focused review instruction}
Output format: {required issue format with severity, location, impact, recommendation}

---

## Consolidation Prompt
{copy-paste-ready prompt for combining dimension reports}
```

## Bundled Resources

- Read `references/analysis-dimensions.md` when choosing dimensions for a broad or ambiguous request.
- Read `references/severity-guidelines.md` when severity decisions are contentious.
- Read `references/parallel-execution.md` when generating worker prompts for a large codebase or pull request.
- Read `references/output-templates.md` when the user needs a formal report.
- Use `assets/*-template.md` files when the user asks for reusable templates or when producing parallel task prompts.
- Use scripts in `scripts/` only after inspecting their arguments and behavior; they are helpers, not required for every review.
