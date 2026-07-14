---
name: software-graph-analysis
description: Use Ontoly to build or query a deterministic Software Graph before searching files. Use when the user asks to explain a repository, trace routes or request flows, find dependencies, inspect services/controllers/modules, audit configuration or environment variables, analyze impact, or use Ontoly MCP.
license: MIT
---

# Software Graph Analysis

This skill helps Claude use Ontoly as the source of truth for repository understanding.

Ontoly builds a deterministic Software Graph from a codebase. Claude should use that graph to answer architecture, dependency, request tracing, configuration, and impact questions before falling back to broad source search.

## When to Use

Use this skill when the user asks:

- "Explain this repository."
- "Trace this route."
- "Which service owns authentication?"
- "What depends on this package, module, class, or function?"
- "What breaks if I remove this service?"
- "Where is this environment variable used?"
- "Show routes, controllers, services, modules, or packages."
- "Use Ontoly MCP."

Do not use this skill for generic architecture theory without repository evidence, or for changing Ontoly compiler behavior.

## Workflow

1. Check whether Ontoly output already exists, such as `.ontoly/`, `SoftwareGraph.json`, diagnostics, statistics, graph hash, or MCP configuration.
2. If no usable graph exists, run:

   ```bash
   ontoly build .
   ```

3. Check graph trust, diagnostics, coverage, framework detection, graph hash, and build timestamp.
4. Prefer Ontoly MCP or CLI graph queries before repository-wide source search.
5. Answer with evidence from the graph:
   - node IDs
   - node kinds
   - relationship names
   - source locations
   - diagnostics
   - confidence
6. Inspect source files only when the graph is missing, stale, ambiguous, or insufficient.
7. Clearly label any fallback source inspection as non-graph evidence.

## Capability Map

| User intent | Ontoly capability or query |
| --- | --- |
| Repository overview | ArchitectureSummary |
| Route/request trace | TraceExecution |
| Dependency tree | FindDependencies |
| Impact analysis | ImpactAnalysis |
| Configuration usage | FindConfigurationUsage |
| Authentication flow | FindAuthenticationFlow |
| Authorization checks | FindAuthorization |
| Framework coverage | FrameworkReport |
| Dead code review | FindDeadCode |

If a named capability is unavailable, use the closest deterministic graph query and state the fallback.

## Output Requirements

For every substantive answer:

- Cite the graph artifact or MCP response used.
- Include relevant node IDs and relationship names when available.
- Include source locations when available.
- Mention diagnostics that reduce confidence.
- Separate measured graph facts from inferred observations.

Do not invent graph facts. If Ontoly cannot answer, say what is missing and what fallback evidence was inspected.

## Troubleshooting

If `ontoly build .` fails, report the exact command, exit code, and diagnostic summary.

If MCP is unavailable, query persisted graph JSON or Ontoly CLI output and state that MCP was unavailable.

If multiple graph nodes match, show candidates with IDs, kinds, and locations instead of silently choosing one.
