---
name: context-receipts
description: Verify what context an agent loaded, deferred, summarized, or suppressed without exposing raw content.
---

# Context Receipts

Use this skill when evaluating context-heavy agent workflows: Claude Code skills, MCP Tool Search, lazy-loaded tools, RAG notes, long-running subagents, or handoffs between coding agents.

The goal is to produce a small, privacy-safe receipt that proves **what crossed the context boundary** without logging raw prompts, schemas, retrieved documents, arguments, results, or private files.

## When to Use This Skill

- A workflow claims to save tokens through Tool Search, lazy MCP loading, or progressive disclosure.
- A skill or prompt pack should load only routing instructions at startup, then fetch details on demand.
- A subagent returns a summary and you need to confirm raw child output did not leak into parent context.
- A role-specific subagent should receive only its allowed MCP servers, not the full union of deployment, analytics, browser, email, and repo tools.
- A memory/RAG/code-graph system retrieves notes and you need evidence of scope, source, and suppression.

## What This Skill Does

1. **Names the boundary**: tool index, skill activation, retrieved context, compaction, subagent handoff, or summary.
2. **Records minimal evidence**: counts, hashes, IDs, token buckets, timestamps, and reasons.
3. **Flags privacy posture**: explicitly states which raw content was not logged.
4. **Reports audit gaps**: calls out when the workflow cannot prove a claim.

## How to Use

Ask the agent to generate a context receipt after the operation:

```
Use context-receipts to verify this Tool Search workflow. Show only counts, hashes, source IDs, token buckets, and privacy flags. Do not include raw tool schemas, prompts, args, retrieved text, or tool results.
```

## Receipt Shape

```yaml
receipt_type: tool-search
operation_id: <stable id or timestamp>
boundary:
  before: startup
  after: tool_call
loaded:
  catalog_count: 42
  hydrated_tool_count: 1
  hydrated_tool_hashes: [sha256:...]
deferred:
  suppressed_tool_count: 41
  suppressed_reason: not relevant to task
privacy:
  raw_schema_logged: false
  raw_args_logged: false
  raw_result_logged: false
audit_gap: null
```

## 60-Second Checks

### Tool Search / Lazy MCP

- Did startup load only catalog metadata, not full schemas?
- Which search query or routing reason selected the tool?
- Which tool definition was hydrated, and why?
- How many tools stayed suppressed?
- Were raw schemas, args, and results excluded from the receipt?

### Skill / Prompt Context

- Which skill names/descriptions were visible at startup?
- Which full skill body was loaded?
- Which auxiliary files or references were read?
- Which references stayed unloaded?

### Per-Agent MCP Injection

- Which subagent role/session was booted?
- Which MCP servers were available to that role?
- Which servers were explicitly excluded before boot?
- Did the subagent load full schemas, or only a compact index?
- How many tool definitions stayed deferred/suppressed?
- What startup token bucket remained after applying the policy?

### Subagent Boundary

- What was delegated to the child agent?
- What came back to the parent: summary, IDs, counts, or raw transcript?
- How large was the returned context bucket?
- Was raw child/tool output excluded from parent context?

## Example

**User**: "Check whether our browser automation skill is actually progressive-disclosure safe."

**Output**:

```yaml
receipt_type: skill-context
skill: browser-automation
startup_visible: [name, description]
loaded_files:
  - path_hash: sha256:7d3...
    role: primary_instructions
    token_bucket: 1k-2k
suppressed_files:
  count: 3
  reason: not needed for this task
privacy:
  raw_file_content_logged: false
  raw_user_prompt_logged: false
audit_gap: no runtime hook confirms whether downstream tool output re-entered parent context
```

## Per-Agent MCP Injection Example

```yaml
receipt_type: per-agent-mcp-injection
subagent_role: testing
policy_source: role_config
available:
  server_count: 2
  server_set_hash: sha256:...
excluded:
  server_count: 5
  server_set_hash: sha256:...
boot:
  loaded_tool_definition_count: 0
  deferred_tool_definition_count: 48
  startup_token_bucket: 50k-75k
privacy:
  raw_server_names_logged: false
  raw_tool_schema_logged: false
audit_gap: proves injection boundary, not whether selected tools are optimal
```

## Tips

- Prefer hashes and stable IDs over excerpts.
- Use token buckets (`0-1k`, `1k-2k`, `2k-5k`) instead of exact sensitive sizes when needed.
- Treat `audit_gap` as useful signal, not failure.
- Do not claim a context-saving workflow worked unless the receipt proves what stayed deferred or suppressed.

## Common Use Cases

- Verifying MCP Tool Search or deferred tool loading.
- Auditing Claude Code / OpenCode skills that load references on demand.
- Checking RAG or memory retrieval scope without leaking retrieved notes.
- Proving per-agent MCP injection excluded irrelevant servers before subagent boot.
- Confirming subagent summaries do not silently copy raw transcripts into parent context.

**Inspired by:** Pluribus context receipts for privacy-safe context-boundary auditing.
