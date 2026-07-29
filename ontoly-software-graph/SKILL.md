---
name: ontoly-software-graph
description: Use when you need to understand a TypeScript repository's architecture, dependencies, request flows, service ownership, configuration usage, or impact radius using Ontoly's deterministic Software Graph before broad source search.
---

# Ontoly Software Graph

Use this skill when a user asks Claude to understand a TypeScript repository's architecture, dependency graph, request flow, service ownership, configuration usage, package topology, impact radius, or security-sensitive code paths.

Ontoly is a deterministic Software Graph compiler. It does not answer questions with AI. It builds graph evidence that Claude can inspect before falling back to source search.

## When to Use This Skill

- Explaining a repository or package architecture.
- Tracing a route, controller, service, module, function, or request lifecycle.
- Finding what depends on a service, repository, module, package, route, or configuration value.
- Reviewing dependency injection, module ownership, configuration usage, or environment variables.
- Planning refactors, migrations, impact analysis, security review, or onboarding.

## What This Skill Does

1. **Graph-first discovery**: Checks for an existing Ontoly graph before searching the repository.
2. **Deterministic evidence**: Uses graph nodes, edges, diagnostics, source spans, graph hash, and confidence signals as primary evidence.
3. **Controlled fallback**: Searches source files only when the graph is missing, stale, low confidence, or insufficient for the user's question.
4. **MCP-aware workflow**: Uses Ontoly MCP when available, and falls back to Ontoly CLI reports when MCP is unavailable.

## How to Use

### Basic Usage

```text
Use Ontoly to explain this repository.
```

### Impact Analysis

```text
Use Ontoly to tell me what breaks if I remove AuthService.
```

### Request Tracing

```text
Use Ontoly to trace POST /login from route to database access.
```

## Workflow

1. Check whether `.ontoly/SoftwareGraph.json` exists.
2. If the graph is missing or stale, ask before installing dependencies or writing generated graph files. Then run:

   ```bash
   pnpm add -D @0xsarwagya/ontoly-cli
   pnpm ontoly build .
   ```

3. Inspect graph quality before answering:

   ```bash
   pnpm ontoly coverage .
   pnpm ontoly stats .
   ```

4. Prefer Ontoly graph queries before repository-wide source search:

   ```bash
   pnpm ontoly architecture --json
   pnpm ontoly report dependencies --format markdown
   pnpm ontoly report routes --format markdown
   pnpm ontoly query impact <node-id>
   pnpm ontoly trace <node-id-or-name>
   ```

5. Start Ontoly MCP when the environment supports MCP-backed tools:

   ```bash
   pnpm ontoly mcp
   ```

6. Use source files only when Ontoly cannot answer the question with enough confidence.

## Evidence Rules

When answering, cite:

- graph hash
- node ids
- relationship types
- source spans when available
- diagnostics or confidence warnings
- fallback reason if source files were inspected

Never claim certainty beyond the graph evidence. If graph coverage is incomplete, say exactly which part is inferred or unresolved.

## Example

**User**: "Which service owns authentication?"

**Output**:

```text
AuthService appears to own authentication.

Evidence:
- node: service:src/auth/auth.service.ts:AuthService
- contained by: module:AuthModule
- callers: AuthController, SessionController
- related routes: POST /login, POST /logout
- configuration reads: JWT_SECRET
- graph hash: <hash>

Confidence: high, because the service is connected to authentication routes, module ownership, and configuration usage in the Software Graph.
```

**Inspired by:** Ontoly's Software Graph and Agent Skills workflows.

## Tips

- Prefer graph evidence over broad grep or repository-wide search.
- Treat missing graph data as a coverage limitation, not proof that a concept does not exist.
- Keep answers actionable: name the owner, trace, dependency, or risk, then show the graph evidence.
- For task-specific workflows, install the official Ontoly skills:

  ```bash
  npx skills add 0xsarwagya/ontoly --list
  npx skills add 0xsarwagya/ontoly --skill architecture-review
  npx skills add 0xsarwagya/ontoly --skill impact-analysis
  npx skills add 0xsarwagya/ontoly --skill request-tracing
  ```

## Common Use Cases

- Repository onboarding.
- Architecture review.
- Dependency analysis.
- Request tracing.
- Configuration audit.
- Security ownership review.
- Refactoring impact analysis.
