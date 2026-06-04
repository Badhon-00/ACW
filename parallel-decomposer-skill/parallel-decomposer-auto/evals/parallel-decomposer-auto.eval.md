# Parallel Decomposer Auto Evaluation Spec

## Binary Checks

### Structure Validation
- [ ] Skill directory contains `SKILL.md`, `AGENTS.md`, `agents/openai.yaml`, `assets/`, `references/`, and `evals/`
- [ ] `assets/worker-spec-template.md` exists
- [ ] `references/orchestration-patterns.md` exists

### Content Validation
- [ ] `SKILL.md` frontmatter contains `name: parallel-decomposer-auto`
- [ ] `SKILL.md` prefers automatic dispatch and keeps manual copy-paste as fallback
- [ ] `SKILL.md` says to ask clarifying questions only when parallel dispatch would be risky
- [ ] `SKILL.md` tells the agent to use phased sequencing instead of forcing unsafe concurrency
- [ ] `AGENTS.md` mentions shared handoff brief, worker specs, and merge strategy
- [ ] `agents/openai.yaml` matches the skill name and intent

## Golden Cases

### Case 1: Automatic Worker Split
**Input**
```text
Use $parallel-decomposer-auto to split this migration plan into orchestration-ready worker specs.
```

**Expected**
- Produces one shared handoff brief
- Produces multiple worker specs
- Mentions automatic dispatch before any manual fallback
- Includes a merge strategy
- Does not ask the user to manually copy prompts as the primary path

### Case 2: Fallback Prompt Generation
**Input**
```text
Use $parallel-decomposer-auto to decompose this feature launch plan, but assume sub-agents are unavailable.
```

**Expected**
- Preserves the same handoff brief and decomposition
- Emits copy-paste-ready prompts as fallback
- Keeps merge instructions explicit

### Case 3: Dependency-Aware Split
**Input**
```text
Use $parallel-decomposer-auto to split this repository refactor across workers without conflicting edits.
```

**Expected**
- Calls out ownership boundaries
- Avoids creating worker specs that would conflict on the same file set
- Produces dependency notes or a phased plan if independence is not possible

### Case 4: Unsafe Parallelism
**Input**
```text
Use $parallel-decomposer-auto to split this change where every worker would need to edit the same core file.
```

**Expected**
- Explains why fully parallel execution is unsafe
- Produces phased work or narrower ownership boundaries
- Does not force multiple workers onto the same file without conflict controls
