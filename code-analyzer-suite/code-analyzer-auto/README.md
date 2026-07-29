# Code Analyzer Auto

An orchestration-first code review skill that automatically dispatches multi-dimensional code analysis to sub-agents or worker threads and consolidates findings into one report.

## When to Use

Use when your runtime supports sub-agents or concurrent worker threads and you want:

- Automatic parallel code review across Security, Performance, Code Quality, Architecture, and Logic dimensions
- A shared orchestration brief passed to all workers
- Findings automatically consolidated into one report

For single-agent code reviews or manual prompt workflows, use [code-analyzer-suite](https://github.com/Alex-eng-ux/code-analyzer-suite) instead.

## Quick Install

This skill is inside the `code-analyzer-auto/` subdirectory of the `code-analyzer-suite` repo.

### Claude Code

```bash
git clone https://github.com/Alex-eng-ux/code-analyzer-suite.git ~/.claude/skills/code-analyzer-suite
```

### Universal

```bash
git clone https://github.com/Alex-eng-ux/code-analyzer-suite.git ~/.agents/skills/code-analyzer-suite
```

### Cursor (project-level)

```bash
git clone https://github.com/Alex-eng-ux/code-analyzer-suite.git .cursor/skills/code-analyzer-suite
```

Invoke with:

```
/code-analyzer-auto Review this pull request for security and performance issues
```

## Structure

```
code-analyzer-auto/
├── SKILL.md                           # Orchestration workflow
├── AGENTS.md                          # Agent activation instructions
├── README.md                          # This file
├── agents/openai.yaml
├── assets/
│   └── orchestration-brief-template.md
├── references/
│   └── orchestration-guide.md
└── evals/
    └── code-analyzer-auto.eval.md
```
