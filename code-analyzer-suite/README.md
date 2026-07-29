# Code Analyzer Suite

A parallel multi-dimensional code analysis skill suite that decomposes code review tasks into 5 specialized analysis dimensions, each executable independently in separate agent windows.

## Features

- **5 Analysis Dimensions**: Security, Performance, Code Quality, Architecture, Logic Verification
- **Parallel Execution**: Each dimension runs in independent agent windows simultaneously
- **Structured Output**: Consistent severity ratings (Critical/High/Medium/Low) across all dimensions
- **Language Support**: Python, JavaScript/TypeScript, Java, Go, Rust, SQL, and more
- **Consolidated Reports**: Automatic merging of dimension results into unified reports
- **Flexible Input**: Accepts code snippets, file paths, or entire codebase references

## Related Skill

For general-purpose task decomposition (non-code parallel planning), use [parallel-decomposer-skill](https://github.com/Alex-eng-ux/parallel-decomposer-skill) instead. This skill focuses on code-specific multi-dimensional analysis.

## Installation

### Quick Install

```bash
./install.sh
```

### Manual Install by Platform

**Claude Code:**

```bash
cp -R code-analyzer-suite ~/.claude/skills/code-analyzer-suite
```

**GitHub Copilot (project-level):**

```bash
cp -R code-analyzer-suite .github/skills/code-analyzer-suite
```

**Cursor (project-level):**

```bash
cp -R code-analyzer-suite .cursor/skills/code-analyzer-suite
```

**Windsurf:**

```bash
cp -R code-analyzer-suite ~/.codeium/windsurf/skills/code-analyzer-suite
```

**Universal (all platforms):**

```bash
cp -R code-analyzer-suite ~/.agents/skills/code-analyzer-suite
```

## Usage

Once installed, invoke with:

```
/code-analyzer Review this Python API for security and performance issues
/code-analyzer Analyze the authentication module for vulnerabilities and logic errors
/code-analyzer Check this React component for performance, accessibility, and best practices
/code-analyzer Audit the entire codebase for security risks
/code-analyzer Review src/auth/login.ts for all dimensions
```

## Analysis Dimensions

| Dimension | Focus | Keywords |
|-----------|-------|----------|
| **Security** | Vulnerabilities, injection, auth, data exposure | security, vulnerability, auth, injection, XSS |
| **Performance** | Bottlenecks, memory leaks, N+1 queries | performance, bottleneck, slow, memory, optimize |
| **Code Quality** | Style, complexity, documentation, tests | quality, style, complexity, documentation, test |
| **Architecture** | Design patterns, coupling, scalability | architecture, design pattern, coupling, scalable |
| **Logic Verification** | Correctness, edge cases, error handling | logic, correctness, edge case, error handling |

## Severity Ratings

| Level | Action Required | Timeline |
|-------|----------------|----------|
| **Critical** | Immediate fix before deployment | Now |
| **High** | Fix within 24-48 hours | 1-2 days |
| **Medium** | Fix within current sprint | 1-2 weeks |
| **Low** | Fix when convenient | Backlog |

## Skill Structure

```
code-analyzer-suite/
├── SKILL.md                    # Core skill definition and workflow (for agents)
├── AGENTS.md                   # Cross-platform agent instructions
├── README.md                   # This file
├── install.sh                  # Cross-platform installer
├── scripts/
│   ├── generate_tasks.py       # Task generator
│   ├── consolidate_report.py   # Report merger
│   ├── run_pipeline.py         # Pipeline orchestrator
│   ├── check_pipeline.py       # Validation
│   └── run_evals.py            # Evaluation runner
├── references/
│   ├── analysis-dimensions.md  # Dimension details
│   ├── severity-guidelines.md  # Severity standards
│   ├── output-templates.md     # Output formats
│   └── parallel-execution.md   # Execution guide
├── assets/
│   ├── security-template.md    # Security analysis template
│   ├── performance-template.md # Performance template
│   ├── quality-template.md     # Quality template
│   ├── architecture-template.md# Architecture template
│   ├── logic-template.md       # Logic template
│   └── consolidated-template.md# Report template
└── evals/
    └── code-analyzer.eval.md   # Evaluation spec
```

## Requirements

- Python 3.8+
- No external dependencies (stdlib only)

## License

MIT
