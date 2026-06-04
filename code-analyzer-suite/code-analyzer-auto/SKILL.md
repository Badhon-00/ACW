---
name: code-analyzer-auto
description: Automatically orchestrate multi-dimensional code review across sub-agents or worker threads, then consolidate findings into one report. Use when the user asks for automatic orchestration, sub-agents, concurrent workers, multi-agent review, worker-thread review, or auto-dispatched code analysis across security, performance, code quality, architecture, and logic dimensions. For ordinary single-agent or manual prompt code review, use code-analyzer-suite instead. If automatic worker execution is unavailable, fall back to producing copy-paste-ready worker prompts.
---

# Code Analyzer Auto

Use this skill when the environment can dispatch work to sub-agents or worker threads. Treat automatic orchestration as the primary path. Emit manual worker prompts only as a fallback when automatic orchestration is unavailable.

## Workflow

1. Identify the review target.
   - Determine whether the target is a snippet, file, module, pull request, or repository area.
   - Inspect local files and surrounding context before selecting dimensions.
   - Determine language, framework, and likely risk areas from the codebase.
   - Ask a clarifying question only when the review target or write/read scope is ambiguous enough to change the worker split.

2. Select dimensions.
   - Start with the dimensions the user explicitly asked for.
   - For broad requests, choose the 2-3 highest-value dimensions first.
   - Use all five dimensions only when the target is large, high-risk, or the user asked for a comprehensive audit.
   - Avoid dispatching redundant workers when a narrower review would produce a clearer result.

3. Produce a shared orchestration brief.
   - Include the target, scope, relevant files, language/framework, shared constraints, severity rules, and final report shape.
   - Keep this brief short enough to pass to each sub-agent as shared context.

4. Dispatch work.
   - If sub-agent execution is available, dispatch one worker per selected dimension.
   - Give each worker the shared orchestration brief and a narrow dimension-specific assignment.
   - If sub-agent execution is unavailable, emit copy-paste-ready worker prompts for manual fallback.
   - Do not present manual copy-paste as the main workflow when automatic dispatch is available.

5. Consolidate findings.
   - Deduplicate overlapping issues.
   - Merge repeated root causes into a single action item when appropriate.
   - Keep the highest justified severity.
   - Separate confirmed issues from open questions.

## Dimensions

| Dimension | Focus |
| --- | --- |
| Security | Auth, authorization, input validation, secrets, injection, data exposure |
| Performance | Bottlenecks, query patterns, async behavior, resource use, rendering cost |
| Code Quality | Readability, cohesion, duplication, tests, documentation, local conventions |
| Architecture | Boundaries, dependencies, layering, modularity, scalability |
| Logic Verification | Correctness, edge cases, state transitions, error paths, business rules |

## Output Shape

When automatic orchestration is available:

```markdown
## Orchestration Brief
Target: {files/modules}
Scope: {included and excluded areas}
Shared context: {framework, language, constraints, known risks}
Selected dimensions: {dimensions}
Worker rule: Read this brief before starting your assigned review.

## Worker Specs
### {Dimension}
- Goal: {what this worker should inspect}
- Focus: {key checks}
- Ignore: {out of scope}
- Output: {finding format}

## Consolidated Report
{merged findings, open questions, positives, and prioritized actions}
```

When automatic orchestration is unavailable, emit the same structure plus manual worker prompts.

## Bundled Resources

- Read `references/orchestration-guide.md` when deciding between automatic dispatch and manual fallback.
- Read `assets/orchestration-brief-template.md` when a reusable shared brief would help.
- Reuse the parent skill's references only when more detailed dimension guidance is needed.
