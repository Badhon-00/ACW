---
name: parallel-decomposer-auto
description: Convert a complex request into orchestration-ready subtask specs for automatic sub-agent execution or worker-thread dispatch, with a shared handoff brief, dependency notes, ownership boundaries, and a merge plan. Use when the user asks for automatic orchestration, sub-agents, concurrent workers, multi-agent dispatch, or an auto-first decomposition workflow. For ordinary manual task-card decomposition, use parallel-decomposer-skill instead. If automatic execution is unavailable, fall back to copy-paste-ready worker prompts.
---

# Parallel Decomposer Auto

Use this skill when the environment can orchestrate multiple workers automatically. Produce worker specs for sub-agents or worker threads as the primary path. Use manual copy-paste prompts only as a fallback when the runtime cannot dispatch workers.

## Workflow

1. Infer the goal and clarify only when needed.
   - Identify the final deliverable, relevant files or data, constraints, and known non-goals from the request and local context.
   - Make reasonable assumptions when the decomposition remains safe.
   - Ask a short clarifying question only when missing scope, write ownership, or sequencing constraints would make parallel dispatch risky.

2. Choose the split strategy.
   - Split by aspect, component, audience, method, or phase depending on the task.
   - Avoid splits that create heavy coordination or file ownership conflicts.
   - If work is not safely parallel, create a phased plan with sequential gates instead of forcing concurrency.

3. Create a shared handoff brief.
   - Include the original goal, shared context, relevant files, constraints, non-goals, and expected final deliverable.
   - Pass this brief to every worker as shared context.

4. Generate orchestration-ready worker specs.
   - Define one worker spec per independent subtask.
   - Assign ownership boundaries when multiple workers touch the same project area.
   - Include a merge strategy and dependency notes.
   - Include the expected dispatch mode: automatic sub-agent, worker thread, or manual fallback.

5. Dispatch or fall back.
   - If sub-agent execution is available, dispatch worker specs automatically.
   - If unavailable, emit copy-paste-ready worker prompts without changing the decomposition.
   - Do not present manual copy-paste as the main workflow when automatic dispatch is available.

6. Merge results.
   - Deduplicate overlaps.
   - Resolve contradictions explicitly.
   - Preserve important uncertainty and blockers.

## Output Shape

```markdown
## Handoff Brief
Original goal: {goal}
Shared context: {facts every worker needs}
Relevant files or data: {paths, links, artifacts}
Constraints and non-goals: {limits}
Final deliverable: {merged result shape}

## Worker Specs
### Worker 1: {Title}
- Goal: {worker objective}
- Inputs: {files, data, handoff brief}
- Dispatch mode: {automatic sub-agent | worker thread | manual fallback}
- Focus: {what this worker should handle}
- Avoid: {what to leave alone}
- Output: {required result shape}

## Merge Strategy
- Merge order: {recommended order}
- Deduplicate: {likely overlap}
- Resolve: {expected conflicts}
- Finalize: {how to produce the final deliverable}
```

## Bundled Resources

- Read `references/orchestration-patterns.md` when choosing between automatic dispatch and manual fallback.
- Use `assets/worker-spec-template.md` when reusable worker specs would help.
