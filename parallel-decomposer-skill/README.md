# parallel-decomposer-skill

A cross-platform agent skill for decomposing complex tasks into parallel subtasks optimized for multi-agent execution.

## What It Does

This skill helps you break down complex work into 3-7 independent subtasks that can run simultaneously across multiple agent windows. It handles:

- **Task Analysis** — Understanding your complex task's domain, objectives, and constraints
- **Smart Decomposition** — Breaking work into independent parallel pieces
- **Dependency Detection** — Ensuring subtasks don't depend on each other
- **Context Preservation** — Including all necessary background in each subtask card
- **Result Integration** — Providing templates to merge parallel outputs into unified results

## Related Skill

For code-specific parallel analysis (Security, Performance, Code Quality, Architecture, Logic Verification), use [code-analyzer-suite](https://github.com/Alex-eng-ux/code-analyzer-suite) instead. This skill focuses on general-purpose task decomposition.

## Installation

### Quick Install (Auto-detect)

```bash
./install.sh
```

### Install to Specific Platform

```bash
./install.sh --platform claude
./install.sh --platform cursor
./install.sh --platform windsurf
```

### Install to All Detected Platforms

```bash
./install.sh --all
```

### Manual Install

Copy this directory to your tool's native skills path:

| Platform | Path |
|----------|------|
| Claude Code | `~/.claude/skills/parallel-decomposer-skill` |
| GitHub Copilot | `~/.copilot/skills/parallel-decomposer-skill` |
| VS Code Copilot | `.github/skills/parallel-decomposer-skill` |
| Cursor | `.cursor/skills/parallel-decomposer-skill` |
| Windsurf | `.windsurf/rules/parallel-decomposer-skill` or `~/.codeium/windsurf/skills/parallel-decomposer-skill` |
| Cline | `~/.cline/skills/parallel-decomposer-skill` |
| Trae | `.trae/rules/parallel-decomposer-skill` |
| Gemini CLI | `~/.gemini/skills/parallel-decomposer-skill` |
| Goose | `~/.config/goose/skills/parallel-decomposer-skill` |
| OpenCode | `~/.config/opencode/skills/parallel-decomposer-skill` |
| Roo Code | `~/.roo/skills/parallel-decomposer-skill` |
| Universal | `~/.agents/skills/parallel-decomposer-skill` |

## Usage

Once installed, invoke with:

```
/parallel-decomposer Analyze this codebase for security vulnerabilities, performance issues, and code quality
```

### Example Invocations

```
/parallel-decomposer Write a comprehensive report about AI trends covering technical, business, and ethical aspects
/parallel-decomposer Review this pull request for logic errors, style issues, and documentation completeness
/parallel-decomposer Research the competitive landscape: product features, pricing, market share, and customer reviews
/parallel-decomposer Build a marketing campaign: content strategy, social media, email sequences, and landing pages
```

### Natural Activation

You can also activate without the slash prefix:

```
Break this into parallel tasks
Decompose this for multiple agents
Split this work so we can parallelize it
I need to run these in separate agent windows
Divide and conquer this project
```

## How It Works

1. **You provide** a complex task
2. **Skill analyzes** and decomposes into independent subtasks
3. **Skill outputs** structured subtask cards with full context
4. **You copy** each card to separate agent windows
5. **You paste** results back
6. **Skill provides** integration template to merge results

## Skill Structure

```
parallel-decomposer-skill/
├── SKILL.md              # Core workflow definition (for agents)
├── AGENTS.md             # Cross-platform agent instructions
├── README.md             # This file
├── install.sh            # Cross-platform installer
├── scripts/
│   ├── check_pipeline.py # Validate skill structure
│   ├── validate.py       # Spec validation (frontmatter, naming)
│   └── security_scan.py  # Security scan for secrets
├── references/
│   ├── decomposition-patterns.md  # Domain-specific strategies
│   ├── integration-guide.md       # Result merging techniques
│   └── dependency-checker.md      # Dependency detection guide
├── assets/
│   ├── handoff-brief-template.md  # Shared context template for workers
│   └── subtask-card-template.md   # Reusable subtask card format
└── evals/
    └── parallel-decomposer.eval.md # Evaluation spec
```

## Validation

Run the built-in validation:

```bash
python3 scripts/validate.py .
python3 scripts/security_scan.py .
python3 scripts/check_pipeline.py .
```

## License

MIT
