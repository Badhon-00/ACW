# Data-Driven Prompt Optimization Framework

This document contains the detailed framework for analyzing and improving prompts using real data from observability logs.

---

## Core Principles

**1. One change at a time.** If you change the model, the prompt, and the system simultaneously, you won't know what improved. Isolate variables.

**2. Define "better" before you start.** Better = cheaper? Faster? More correct output? Choose a primary metric and measure it.

**3. Use production as the source of truth.** Prompts that seem perfect in the playground fail in production with real inputs. Always validate with real log data.

**4. Size matters.** A 5% improvement on a prompt that runs 10,000 times a day is a huge gain. Prioritize by volume × impact.

---

## Diagnostic Framework

### Step 1: Classify the Problem

Before optimizing, identify which category the problem falls into:

| Category | Log Symptoms | Common Root Cause |
|----------|-------------|------------------|
| **High cost** | Very high tokens/request | Bloated system prompt, unnecessary context, oversized model |
| **High latency** | Time-to-first-token > 3s or total > 10s | Very long prompt, large model, no streaming, no caching |
| **Low quality** | Incorrect outputs, broken format, ignored instructions | Ambiguous prompt, no examples, contradictory instructions |
| **Frequent errors** | Elevated 4xx/5xx rate | Unvalidated inputs, exceeded token limits, rate limiting |
| **Inconsistency** | Same query → very different outputs | High temperature, vague instructions, no output schema |

### Step 2: Measure the Baseline

For each problematic prompt, record before touching anything:

```
Prompt ID / name: ___
Current version: ___
Average tokens (input): ___
Average tokens (output): ___
Average cost per request: $___
Average latency: ___ms
p95 latency: ___ms
Estimated success rate: ___%
Manually reviewed output sample: N=___
```

### Step 3: Analyze the Current Prompt

Read the full prompt and ask yourself:

**Structure:**
- Does it have a role section separate from the task?
- Are instructions in logical order (context → task → format → constraints)?
- Are there contradictory instructions?

**Information Density:**
- Is there filler text that doesn't change behavior? (e.g., "Please, in great detail...")
- Are there duplicated instructions?
- Is the context sent always necessary, or only sometimes?

**Output Specificity:**
- Is the exact output format specified?
- Are there examples of expected output?
- What happens if the model doesn't have enough information? Is it instructed to handle that?

---

## Optimization Techniques by Category

### To Reduce Cost (Input Tokens)

**Technique 1 — System Prompt Compression**

Before:
```
You are a very helpful and friendly assistant that helps users with their questions.
You should always be polite, respectful, and considerate. When you don't know something,
say so honestly. Please always respond in English and with great detail.
```

After:
```
Respond in English. If you don't know something, say so directly.
```

Rule: if removing a phrase doesn't change observable behavior in the logs, remove it.

**Technique 2 — Prompt Caching (Anthropic specific)**

Anthropic's prompt caching caches the prompt prefix if:
- It has more than 1024 tokens (Sonnet/Opus) or 2048 tokens (Haiku)
- The prefix is identical between requests

To take advantage of it, structure the prompt like this:
```xml
<system>
[ALL static context here — documents, fixed instructions, examples]
<!-- This block gets cached after the first request -->
</system>

[The dynamic part (user query) goes AFTER the static block]
```

Potential savings: 90% of input cost on the cached block, with reduced latency.

**Technique 3 — Model Routing**

Not all requests need the most powerful model. Define rules:

| Task Type | Recommended Model | Criteria |
|-----------|------------------|----------|
| Simple classification (category, sentiment) | claude-haiku-4-5 | <5 classes, short input |
| Structured data extraction | claude-haiku-4-5 / claude-sonnet-4-6 | Depends on complexity |
| Short text generation | claude-sonnet-4-6 | Responses <500 words |
| Complex reasoning, code | claude-sonnet-4-6 / claude-opus-4-6 | Multi-step tasks |
| Long analysis, research | claude-opus-4-6 | When quality > cost |

---

### To Reduce Latency

**Technique 1 — Enable Streaming**

If the user sees the response in real time, streaming reduces perceived latency even if total time is the same.

**Technique 2 — Parallelize Tool Calls**

In agentic flows, identify tool calls that don't depend on each other and run them in parallel. Claude supports multiple tool calls in the same turn.

Before (sequential): search file → read file → generate response = 3 calls in series
After (parallel): [search file + read file] in parallel → generate response = 2 calls

**Technique 3 — Reduce Sent Context**

If the conversation history grows indefinitely, cost and latency increase with each turn. Strategies:
- Summarize history after N turns
- Keep only the last K turns in context
- Use RAG instead of sending full documents

---

### To Improve Quality

**Technique 1 — Few-Shot Examples**

The difference between a prompt with and without examples is enormous. For structured outputs:

```
Classify the sentiment of the text. Respond only with: positive, negative, or neutral.

Examples:
Input: "The service was excellent, highly recommended"
Output: positive

Input: "They took 3 weeks to respond to my ticket"
Output: negative

Input: "I received the product on the indicated date"
Output: neutral

Now classify:
Input: [TEXT]
Output:
```

**Technique 2 — Explicit Output Schema**

Instead of describing the format in words, show it:

```
ALWAYS respond in this exact JSON format:
{
  "summary": "string of maximum 2 sentences",
  "key_points": ["string", "string", "string"],
  "recommended_action": "string or null"
}
```

**Technique 3 — Chain of Thought for Reasoning**

For tasks requiring complex logic, ask the model to think out loud before responding:

```
Analyze the problem step by step before giving your final answer.
Use <thinking> for your reasoning and <answer> for your final response.
```

**Technique 4 — Separation of Concerns**

If the prompt does too much at once, split it into specialized calls:
- Call 1: extract information from input
- Call 2: reason about extracted information
- Call 3: format the final output

Each call does one thing and does it well.

---

## Experiment Template

Use this template to document each optimization:

```markdown
## Experiment: [descriptive name]
Date: ___
Platform: ___

### Hypothesis
[What problem it solves and why you think it will work]

### Change Applied
**Before:**
[previous prompt or fragment]

**After:**
[new prompt or fragment]

### Results
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Cost/request | $X | $X | -X% |
| Avg latency | Xms | Xms | -X% |
| p95 latency | Xms | Xms | -X% |
| Success rate | X% | X% | +X% |

### Sample of Compared Outputs
N= ___ requests manually evaluated

### Decision
[ ] Adopt  [ ] Discard  [ ] Continue iterating
Reason: ___
```

---

## Early Warning Signals (for continuous monitoring)

Configure alerts in your platform when:

- Cost/hour exceeds 150% of the 7-day average
- p95 latency > 15 seconds for more than 5 minutes
- Error rate > 5% in any 10-minute window
- A single request exceeds $0.50 (adjust for your scale)
- A new model appears in production that wasn't authorized

---

## Production-Ready Prompt Checklist

Before deploying a modified prompt to production:

- [ ] Tested with at least 20 real inputs from the log (not invented)
- [ ] Works with edge case inputs: empty, very long, in another language, with special characters
- [ ] Estimated cost and latency are acceptable at production volume
- [ ] Output format is parseable by the code that consumes it
- [ ] A fallback is defined if the model returns unexpected output
- [ ] New version is saved in the platform's Prompt Hub with a version number
- [ ] Team has been notified of the change
