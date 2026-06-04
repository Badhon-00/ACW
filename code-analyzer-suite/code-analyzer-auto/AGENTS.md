# Code Analyzer Auto

## Purpose

An orchestration-first code review skill for runtimes that can dispatch sub-agents or worker threads automatically. It decomposes code review into focused dimensions, shares one orchestration brief across workers, and consolidates findings into one report.

## Activation Triggers

This skill activates when the user:

- Asks for a code review, audit, or analysis using automatic orchestration, sub-agents, worker threads, or multi-agent dispatch
- Wants Security, Performance, Code Quality, Architecture, or Logic analysis to run concurrently
- Requests automatic orchestration, automatic dispatch, multi-agent review, or worker-thread review
- Wants a findings-first consolidated report without manually copying prompts between windows

## Usage

1. Parse the target: snippet, file, module, pull request, or repository area
2. Identify language, framework, runtime, and likely risk areas from local context
3. Select the most relevant dimensions
4. Create one shared orchestration brief
5. Dispatch one worker per selected dimension when the runtime supports it
6. Fall back to copy-paste-ready worker prompts if automatic dispatch is unavailable
7. Consolidate findings into a single report

Ask for clarification only when the target or scope is ambiguous enough to change the worker split.

## Output

- Shared orchestration brief
- Worker specs or fallback prompts
- Consolidated findings-first report
- Open questions, positives, and prioritized follow-up actions

## Reference

See `SKILL.md` for the full orchestration workflow.
