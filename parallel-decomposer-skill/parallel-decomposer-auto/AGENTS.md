# Parallel Decomposer Auto

## Purpose

An orchestration-first task decomposition skill for runtimes that can dispatch sub-agents or worker threads automatically. It turns one complex request into a shared handoff brief, orchestration-ready worker specs, and a merge strategy.

## Activation Triggers

This skill activates when the user:

- Wants a complex request split across multiple workers automatically
- Mentions automatic orchestration, sub-agents, worker threads, or concurrent task execution
- Wants a shared handoff brief and structured worker specs instead of ad hoc prompts
- Needs a manual fallback only if automatic worker execution is unavailable

## Usage

1. Infer the final deliverable, constraints, relevant files, and non-goals from context
2. Choose a split strategy that minimizes dependency and ownership conflicts
3. Create one shared handoff brief
4. Generate one worker spec per independent subtask
5. Dispatch worker specs automatically when the runtime supports it
6. Fall back to copy-paste-ready prompts when automatic dispatch is unavailable
7. Merge results using the provided merge strategy

Ask for clarification only when missing scope, write ownership, or sequencing constraints would make automatic dispatch risky.

## Output

- Shared handoff brief
- Orchestration-ready worker specs
- Merge strategy with dependency and conflict notes
- Manual fallback prompts when needed

## Reference

See `SKILL.md` for the full decomposition workflow.
