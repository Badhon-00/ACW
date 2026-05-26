---
name: llm-observer
description: >
  Complete audit, optimization, and documentation workflow for any LLM observability platform (Helicone, LangSmith, Langfuse, Braintrust, W&B Weave, Phoenix/Arize, and others). Use this skill whenever you need to: review logs or traces of model calls, analyze request costs or latency, audit agent or chatbot behavior, improve or version prompts with real data, document LLM audit findings, generate optimized prompts for Claude Code, set up a monitoring platform for the first time, or replicate a review methodology across multiple services or SaaS tools. Also activate when the user mentions words like observability, traces, sessions, LLM dashboard, prompt hub, cost tracking, model latency, Helicone, LangSmith, Langfuse, Braintrust, or any AI monitoring platform. Do not wait for the user to name a specific platform — if the context involves auditing or improving LLM usage, this skill is the right one.
---

# LLM Observer — Audit, Optimization, and Documentation

This skill guides a complete, repeatable workflow for any LLM observability platform. Designed to work with Helicone, LangSmith, Langfuse, Braintrust, W&B Weave, Phoenix/Arize, or any similar service.

## Before You Start: Identify the Context

Ask the user (if not already stated):

1. **Which platform are they using?** (or want to set up)
2. **What is the starting point?** — Do they already have accumulated logs? Are they configuring from scratch?
3. **What is the main objective?** — Reduce costs, improve quality, debug errors, document findings, generate Claude Code prompts

With that information, jump to the appropriate module.

---

## Module 1 — Initial Setup

> Use this module when the user needs to connect their application or Claude Code to an observability platform.

Consult `references/platforms.md` for exact steps for each platform. The general pattern is always the same:

1. Create an account and obtain the platform's API key
2. Choose the integration method:
   - **Proxy/Gateway**: redirect the base URL of LLM calls through the platform (zero changes to application logic)
   - **SDK wrapper**: wrap the LLM client with the platform's SDK (more control, more metadata)
   - **MCP server**: for Claude Code specifically, use the platform's MCP server if available
3. Verify that the first requests appear in the dashboard
4. Configure tags/properties to classify requests by project, user, environment

**Success criterion**: the dashboard shows at least one request with visible metrics (latency, tokens, cost).

---

## Module 2 — Log and Trace Review

> Use this module when there are accumulated logs to review.

### 2.1 Quick Dashboard Overview

Ask the user to share (or describe) what they see in their dashboard:
- Request volume by period
- Most used models
- Accumulated cost
- Average and p95 latency
- Error rate

Look for anomalies: unusual cost spikes, very high latencies, frequent errors in the same prompt.

### 2.2 Session and Trace Analysis

For agentic flows (like Claude Code), review **sessions**: groupings of requests that form a complete workflow.

Key questions when reviewing a session:
- How many model calls were made to complete the task?
- Are there redundant or repeated calls with the same prompt?
- Which tool calls consumed the most tokens?
- Were there unexpected retries or loops?
- Is the context (system prompt) repeated in full on each call, or is it cached?

### 2.3 Identifying Problematic Requests

Filter and note requests that meet any of these criteria:
- Cost above the user's threshold
- Latency > 10 seconds
- Error response (4xx, 5xx, or empty responses)
- Output much shorter than what was requested
- Same prompt repeated many times without variation (caching candidate)

Document each finding with: request ID, summarized prompt, identified problem, estimated impact.

---

## Module 3 — Metrics Analysis

> Use this module to convert raw data into actionable insights.

Consult `references/prompt-optimization.md` for the complete framework.

### The 4 Key Dimensions

**Cost**: How much does each complete task cost? Which prompts are most expensive? Is there an opportunity to use a smaller model for simple tasks?

**Latency**: Which parts of the flow are slowest? Does high latency come from the model or network/proxy? Does the end user perceive it?

**Quality**: Do responses meet the objective? Manually review a sample of outputs: hallucinations, incorrect formatting, ignored instructions.

**Efficiency**: How many tokens go to the system prompt vs. actual content? Is there irrelevant context always being sent? Is prompt caching being used?

### Module Output

Generate a prioritized findings table:

| Priority | Problem | Estimated Impact | Recommended Action |
|----------|---------|-----------------|-------------------|
| High | ... | ... | ... |
| Medium | ... | ... | ... |
| Low | ... | ... | ... |

---

## Module 4 — Prompt Optimization

> Use this module to improve prompts identified as problematic.

Core principle: **optimize with real data, not intuition**.

Consult `references/prompt-optimization.md` for the detailed framework.

### Iterative Process

1. Select the prompt to improve (from the previous analysis)
2. Document the current state: exact prompt, current metrics
3. Formulate a hypothesis: why does it fail or underperform?
4. Propose a variant: change **one variable at a time**
5. Compare using the platform: same inputs, measure the difference
6. Only adopt the change if the data justifies it

### Most Common Optimization Types

**To reduce cost:**
- Shorten the system prompt by removing redundant instructions
- Move static instructions to the beginning to leverage Anthropic prompt caching
- Use smaller models for simple classifications or extractions

**To reduce latency:**
- Activate prompt caching on the largest, most static context block
- Split long tasks into short parallel subtasks
- Check if sequential tool calls could run in parallel

**To improve quality:**
- Add concrete few-shot examples of expected output
- Specify the output format with an explicit schema or template
- Separate role, task, and constraint instructions into sections using XML tags
- Eliminate ambiguities: phrases like "if necessary" generate inconsistencies

---

## Module 5 — Findings Documentation

> Generate a structured report at the end of each audit.

Standard template:

```markdown
# LLM Audit — [Project / Service Name]
Date: [date]
Platform: [name]
Analysis period: [from] → [to]

## Executive Summary
[2-3 lines: what was found, most important finding, what to do first]

## Period Metrics
- Total requests: X
- Total cost: $X
- Average latency: Xms
- Error rate: X%
- Models used: [list]

## Key Findings
[Findings table from Module 3]

## Applied Optimizations
[For each optimization: prompt before / after, metrics before / after]

## Generated Prompts for Claude Code
[See Module 6]

## Next Steps
[Prioritized list of pending actions]
```

---

## Module 6 — Claude Code Prompt Generation

> Convert findings into prompts ready to use in Claude Code.

### Optimized System Prompt

Write a system prompt that incorporates:
- The agent's main role and objective
- Constraints and output formats identified as necessary
- The most effective instructions discovered in the audit
- Sections delimited with XML tags: `<role>`, `<task>`, `<format>`, `<constraints>`

### CLAUDE.md Instructions

To improve Claude Code specifically, generate the block to add to `CLAUDE.md`:
- Default agent behaviors
- Most efficient tool usage patterns according to logs
- Model routing rules (e.g., "use haiku for classifications, sonnet for generation")

### Reusable Task Prompts

For the most frequent tasks identified in logs, generate templates with:
- Variables marked with `[VARIABLE]`
- Format instructions included
- Few-shot examples if quality requires them

---

## Module 7 — Replication Across Services

> Apply the same methodology to other platforms or SaaS tools.

1. Consult `references/platforms.md` to see if the new platform already has a guide
2. If not documented, follow the Module 1 pattern adapting field names
3. Modules 2-6 apply equally on any platform
4. Document discovered differences to enrich `references/platforms.md`

Domains where this workflow can be applied:
- **LLM Observability**: Helicone, LangSmith, Langfuse, Braintrust, W&B Weave, Phoenix/Arize, PromptLayer
- **API Monitoring**: Datadog, New Relic, Grafana (with LLM exporters)
- **Eval and Testing**: Promptfoo, DeepEval, Ragas
- **Prompt Management**: PromptHub, Vellum, Humanloop

**Inspired by:** Real workflow developed while auditing Helicone.ai logs and optimizing Claude Code prompts for production agents.
