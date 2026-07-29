# Subtask Card Template

Use this template when a user wants formal cards for parallel workers.

```markdown
## Handoff Brief

Original goal: {Goal all workers are helping complete}
Shared context: {Facts, constraints, decisions, and vocabulary every worker needs}
Relevant files or data: {Paths, links, datasets, or artifacts}
Non-goals: {What workers should not spend time on}
Final deliverable: {What the merged result should become}

Worker rule: Read this handoff brief before starting your assigned subtask.

---

## Subtask {N}: {Title}

Complexity: {Low/Medium/High}
Estimated time: {X minutes/hours}
Worker type: {Generalist/Specialist/Expert}

### Context
Read the Handoff Brief first. {Minimum task-specific background for this isolated agent. Include only context that differs from the shared brief.}

### Prompt
{Specific, copy-paste-ready instruction. Remind the worker to consult the Handoff Brief, then state what to analyze or create, what to focus on, what to ignore, and any checklist the worker must follow.}

### Output Format
{Exact structure the worker should return. Include headings, tables, bullets, severity levels, or examples if needed.}

### Success Criteria
- {Specific deliverable}
- {Quality threshold}
- {Completeness check}
```

## Integration Template

```markdown
# Integration Prompt

I have {N} parallel subtask results below. Combine them into one coherent {output_type}.

Please:
1. Read all results.
2. Remove duplicate findings.
3. Resolve contradictions with brief reasoning.
4. Preserve important dissent or uncertainty.
5. Organize the final output in this order: {desired_order}.
6. Produce the final unified deliverable.

Subtask results:
{paste all subtask outputs here}
```
