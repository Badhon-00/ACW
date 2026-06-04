# Parallel Decomposer Auto

An orchestration-first task decomposition skill that converts complex requests into orchestration-ready worker specs for automatic sub-agent or worker-thread dispatch.

## When to Use

Use when your runtime supports sub-agents or concurrent worker threads and you want:

- Complex tasks automatically decomposed into parallel worker specs
- A shared handoff brief across all workers
- Dependency-aware splitting with ownership boundaries
- Manual fallback only when sub-agents are unavailable

For manual task-card decomposition or copy-paste workflows, use [parallel-decomposer-skill](https://github.com/Alex-eng-ux/parallel-decomposer-skill) instead.

## Quick Install

This skill is inside the `parallel-decomposer-auto/` subdirectory of the `parallel-decomposer-skill` repo.

### Claude Code

```bash
git clone https://github.com/Alex-eng-ux/parallel-decomposer-skill.git ~/.claude/skills/parallel-decomposer-skill
```

### Universal

```bash
git clone https://github.com/Alex-eng-ux/parallel-decomposer-skill.git ~/.agents/skills/parallel-decomposer-skill
```

### Cursor (project-level)

```bash
git clone https://github.com/Alex-eng-ux/parallel-decomposer-skill.git .cursor/skills/parallel-decomposer-skill
```

Invoke with:

```
/parallel-decomposer-auto Split this migration plan into orchestration-ready worker specs
```

## Structure

```
parallel-decomposer-auto/
├── SKILL.md                           # Decomposition workflow
├── AGENTS.md                          # Agent activation instructions
├── README.md                          # This file
├── agents/openai.yaml
├── assets/
│   └── worker-spec-template.md
├── references/
│   └── orchestration-patterns.md
└── evals/
    └── parallel-decomposer-auto.eval.md
```
