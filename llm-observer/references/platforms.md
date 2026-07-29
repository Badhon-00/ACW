# Platform Configuration Guide

Quick reference for connecting applications and Claude Code to the main LLM observability platforms.

---

## Helicone

**Site**: helicone.ai | **Type**: proxy + SDK | **Model**: freemium / enterprise

### Method 1 — Proxy (recommended for Claude Code)

```bash
# 1. Export the API key
export HELICONE_API_KEY="sk-helicone-xxxxxxx"

# 2. In Claude Code (~/.claude/settings.json or CLAUDE.md), add:
# ANTHROPIC_BASE_URL=https://anthropic.helicone.ai
# Header: Helicone-Auth: Bearer $HELICONE_API_KEY
```

### Method 2 — MCP server

```json
// ~/.claude/settings.json
{
  "mcpServers": {
    "helicone": {
      "command": "npx",
      "args": ["@helicone/mcp@latest"],
      "env": {
        "HELICONE_API_KEY": "sk-helicone-xxxxxxx"
      }
    }
  }
}
```

### Method 3 — Python/Node SDK

```python
from anthropic import Anthropic
client = Anthropic(
    base_url="https://anthropic.helicone.ai",
    default_headers={"Helicone-Auth": f"Bearer {HELICONE_API_KEY}"}
)
```

### Key Features
- Sessions and Traces for agentic flows
- Prompt Hub with versioning
- Auto-Improve for automatic prompt suggestions
- Anthropic Prompt Caching support (cached token monitoring)
- Enterprise audit logs (SOC 2 / GDPR)

---

## LangSmith (LangChain)

**Site**: smith.langchain.com | **Type**: SDK | **Model**: freemium

### Basic Configuration

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY="ls__xxxxxxx"
export LANGCHAIN_PROJECT="my-project"
```

```python
# With direct Anthropic (without LangChain):
from langsmith.wrappers import wrap_anthropic
from anthropic import Anthropic

client = wrap_anthropic(Anthropic())
```

### Key Features
- Detailed traces with LangGraph and LangChain
- Playground for comparing prompts
- Integrated datasets and evaluations
- Human feedback UI
- Production alerts and monitoring

---

## Langfuse

**Site**: langfuse.com | **Type**: SDK + proxy | **Model**: open source / cloud

### Basic Configuration

```bash
export LANGFUSE_SECRET_KEY="sk-lf-xxxxxxx"
export LANGFUSE_PUBLIC_KEY="pk-lf-xxxxxxx"
export LANGFUSE_HOST="https://cloud.langfuse.com"  # or your self-hosted instance
```

```python
from langfuse.anthropic import anthropic

# Client is automatically instrumented
client = anthropic.Anthropic()
```

### Key Features
- Self-hosted available (full data privacy)
- Prompt management with variables and versioning
- Manual or automated scores and evaluations
- Native integration with LangChain, LlamaIndex, Haystack
- Offline eval datasets

---

## Braintrust

**Site**: braintrust.dev | **Type**: SDK | **Model**: freemium

### Basic Configuration

```python
import braintrust
from anthropic import Anthropic

client = braintrust.wrap_anthropic(Anthropic())
```

```bash
export BRAINTRUST_API_KEY="xxxxxxx"
```

### Key Features
- Focus on evaluations and benchmarking
- CI/CD integration for automated evals
- A/B prompt comparisons with scoring
- Playground with experiment history
- Native support for LLM-as-judge evals

---

## Weights & Biases — Weave

**Site**: wandb.ai/weave | **Type**: SDK | **Model**: freemium

### Basic Configuration

```python
import weave
from anthropic import Anthropic

weave.init("my-project")

@weave.op()
def call_claude(prompt: str):
    client = Anthropic()
    return client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
```

### Key Features
- Nested traces for complex flows
- Integration with W&B Runs and ML experiments
- Evaluations with reusable datasets
- Ideal if you already use W&B for model training

---

## Phoenix / Arize

**Site**: phoenix.arize.com | **Type**: SDK + self-hosted UI | **Model**: open source

### Basic Configuration

```bash
pip install arize-phoenix opentelemetry-sdk opentelemetry-exporter-otlp
```

```python
import phoenix as px
from openinference.instrumentation.anthropic import AnthropicInstrumentor

px.launch_app()  # Launches local UI at localhost:6006
AnthropicInstrumentor().instrument()

from anthropic import Anthropic
client = Anthropic()  # Now automatically instrumented
```

### Key Features
- Local UI without an account (ideal for private development)
- Based on OpenTelemetry (open standard)
- Embeddings and RAG analysis
- Hallucination and toxicity detection
- Exportable to Arize cloud for production

---

## PromptLayer

**Site**: promptlayer.com | **Type**: proxy + SDK | **Model**: freemium

### Basic Configuration

```python
import promptlayer
promptlayer.api_key = "pl_xxxxxxx"

anthropic = promptlayer.anthropic.Anthropic()
# Identical usage to the standard client
```

### Key Features
- Visual history of all prompts
- Tags and search by prompt content
- A/B prompt testing
- Templates with versioning
- Team collaboration on prompts

---

## Quick Comparison

| Platform | Self-hosted | Best for | Claude Code Integration |
|----------|-------------|----------|------------------------|
| Helicone | ✅ | Simple proxy + agents | ✅ MCP + proxy |
| LangSmith | ❌ | LangChain ecosystem | SDK wrapper |
| Langfuse | ✅ | Privacy + open source | SDK wrapper |
| Braintrust | ❌ | Evals and benchmarking | SDK wrapper |
| W&B Weave | ❌ | Existing ML teams | SDK @weave.op |
| Phoenix | ✅ | Local development | OTel auto-instrument |
| PromptLayer | ❌ | Simple prompt management | SDK wrapper |
