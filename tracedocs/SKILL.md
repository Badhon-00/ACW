---
name: tracedocs
description: Turn any codebase into evidence-grounded Markdown study docs plus a machine-readable index.json, where every claim cites its source and deployment steps are never invented.
---

# tracedocs

tracedocs turns any codebase into a durable, evidence-grounded documentation
package — operation, deployment, learning, architecture, API/data,
troubleshooting, and maintenance manuals — plus a machine-readable `index.json`
for AI agents. Every operational or deployment claim cites the source file it
came from and carries a confidence label (`Verified` / `Inferred` / `Unknown` /
`Needs confirmation`), and the skill refuses to invent steps it cannot source.

Full skill, references, templates, and a validated sample output:
https://github.com/wxggzz/tracedocs (MIT).

## When to Use This Skill

- Onboarding to, or documenting, an unfamiliar codebase
- Producing durable in-repo docs for operation, deployment, and maintenance
- Preparing an AI-agent-ready knowledge handoff (with `index.json`)
- Turning a repo into a study guide whose claims are traceable to source

## What This Skill Does

1. **Analyze**: reads the stack, scripts, entry points, environment-variable names, deployment signals, and tests.
2. **Evidence map**: records a source map, assumptions, and a generation log with confidence labels.
3. **Write**: produces the Markdown manuals and an `index.json` manifest — never inventing deployment steps.
4. **Quality check**: verifies paths exist, commands are sourced, no secret values leak, and gaps are documented.

## How to Use

### Basic Usage

```
Use tracedocs to generate evidence-grounded study docs for this repository. Write the output to study-docs/.
```

### Advanced Usage

```
Use tracedocs to document https://github.com/owner/repo. Emphasize deployment and operations, and produce index.json for agent handoff.
```

## Example

**User**: "Document ./my-app with tracedocs"

**Output**:
```
study-docs/
  00-project-overview.md ... 10-maintenance-and-contribution.md
  index.json            # machine-readable manifest
  _evidence/            # source-map, assumptions, generation-log
```

Each operational claim cites its source and confidence; anything unverifiable
(for example, "no deployment configuration found") is stated, not guessed.

## Tips

- Treat anything not labelled `Verified` as a prompt to check the source.
- Commit `study-docs/` so docs diff in PRs and stay current.
- Feed `index.json` to other agents for a structured project handoff.

## Common Use Cases

- New-hire / contributor onboarding
- Operations and deployment runbooks grounded in the actual repo
- AI-agent handoff with a machine-readable manifest
