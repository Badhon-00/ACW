# OpenInference Semantic Conventions

Canonical attribute reference for the OpenInference (OI) tracing spec — the convention Arize Phoenix consumes natively. observent emits these keys when the resolved convention is `oi` or `both` (see `../SKILL.md` Step 3).

---

## Maintainer's sources

Every span-kind / attribute table below derives from the OpenInference spec — re-verify against the URLs below when the upstream spec ships changes. Per-section `**Sources:**` bullets call out subsections that pull from adjacent specs (OTel baggage, OTel exceptions).

**Primary spec:**
- Rendered docs — https://arize-ai.github.io/openinference/spec/semantic_conventions.html
- Spec source — https://github.com/Arize-ai/openinference/blob/main/spec/semantic_conventions.md
- Python instrumentors index (one PyPI package per framework) — https://github.com/Arize-ai/openinference/tree/main/python

**Adjacent specs cited by individual sections:**
- OTel baggage API (Cross-cutting) — https://opentelemetry.io/docs/specs/otel/baggage/api/
- OTel exception attributes (Exception handling) — https://opentelemetry.io/docs/specs/semconv/exceptions/

Last reviewed: 2026-07-03.

---

## Span kinds

Set on every span via `openinference.span.kind`.

| Value | Purpose |
|---|---|
| `LLM` | Large Language Model invocations |
| `EMBEDDING` | Embedding service calls |
| `CHAIN` | Workflow / graph nodes; entry points and links between steps |
| `RETRIEVER` | Data retrieval (RAG) |
| `RERANKER` | Document reranking |
| `TOOL` | External tool / function calls |
| `AGENT` | Reasoning blocks combining LLMs and tools |
| `GUARDRAIL` | Jailbreak protection / response filtering |
| `EVALUATOR` | Output evaluation / assessment |
| `PROMPT` | Prompt template rendering |
| `UNKNOWN` | Fallback when the kind can't be determined — don't emit deliberately |

---

## LLM spans

### Core

| Attribute | Type | Notes |
|---|---|---|
| `llm.model_name` | string | Resolved model id (e.g. `gpt-4o`, `claude-sonnet-4-6`) |
| `llm.system` | string | Well-known: `anthropic`, `openai`, `vertexai`, `cohere`, `mistralai`, `xai`, `deepseek`, `amazon`, `meta`, `ai21` |
| `llm.provider` | string | Hosting provider (`openai`, `azure`, `google`, `aws`, …) |
| `llm.invocation_parameters` | JSON string | Excludes input messages |
| `llm.finish_reasons` | string[] | `stop`, `length`, `tool_use`, … |

### Messages (chat API)

Flattened with indexed prefixes — e.g. `llm.input_messages.0.message.role`.

| Attribute | Type | Notes |
|---|---|---|
| `llm.input_messages` | list of objects | Flattened per index |
| `llm.output_messages` | list of objects | Flattened per index |
| `…<i>.message.role` | string | `user`, `system`, `assistant`, `tool`, `function` |
| `…<i>.message.content` | string | Text content |
| `…<i>.message.contents` | list of objects | Multimodal content (use `message_content.*` below) |
| `…<i>.message.tool_calls` | list of objects | Function calls from the LLM |
| `…<i>.message.tool_call_id` | string | References `tool_call.id` |

### Multimodal content

Flattened — e.g. `llm.input_messages.0.message.contents.0.message_content.type`.

| Attribute | Type | Notes |
|---|---|---|
| `message_content.type` | string | `text`, `image`, `audio` |
| `message_content.text` | string | When `type=text` |
| `message_content.image` | object | When `type=image` (use `image.url`) |

### Tool calls (function calling)

| Attribute | Type | Notes |
|---|---|---|
| `tool_call.id` | string | Identifier for concurrent calls |
| `tool_call.function.name` | string | Function name being invoked |
| `tool_call.function.arguments` | JSON string | Function arguments |
| `message.function_call_name` | string | Legacy: function name in tool/function role |
| `message.function_call_arguments_json` | JSON string | Legacy: function arguments |
| `llm.function_call` | JSON string | Object with `function_name` and `args` |

### Available tools (advertised to the model)

| Attribute | Type | Notes |
|---|---|---|
| `llm.tools` | list of objects | Flattened |
| `…<i>.tool.name` | string | Tool identifier |
| `…<i>.tool.description` | string | Purpose |
| `…<i>.tool.json_schema` | JSON string | Input schema |
| `…<i>.tool.parameters` | JSON string | Parameter spec |

### Text completions (legacy API)

| Attribute | Type | Notes |
|---|---|---|
| `llm.prompts` | list of objects | `…<i>.prompt.text` |
| `llm.choices` | list of objects | `…<i>.completion.text` |

### Token counts

| Attribute | Type | Notes |
|---|---|---|
| `llm.token_count.prompt` | int | Input tokens |
| `llm.token_count.completion` | int | Output tokens |
| `llm.token_count.total` | int | Sum |
| `llm.token_count.prompt_details.cache_read` | int | Anthropic cache hit |
| `llm.token_count.prompt_details.cache_write` | int | Anthropic cache write |
| `llm.token_count.prompt_details.audio` | int | Audio input tokens |
| `llm.token_count.completion_details.reasoning` | int | Reasoning tokens |
| `llm.token_count.completion_details.audio` | int | Audio output tokens |

**Source-API note (OpenAI: Chat Completions vs Responses).** The two OpenAI text endpoints return usage under different field names — Chat Completions: `usage.{prompt_tokens, completion_tokens, total_tokens}`; Responses API: `usage.{input_tokens, output_tokens, total_tokens}`. `openinference-instrumentation-openai` normalizes both into the OI keys above (`llm.token_count.prompt` / `.completion` / `.total`), but only when its version supports the Responses API — check the instrumentor changelog if you mix both APIs in a single agent. **Streaming gotcha:** Chat Completions streaming omits usage unless the request passes `stream_options={"include_usage": True}`; Responses API includes usage in the final event automatically. Without the opt-in, `llm.token_count.*` will be missing on the span. **Reasoning tokens (o-series):** Responses API exposes them under `usage.output_tokens_details.reasoning_tokens`; Chat Completions under `usage.completion_tokens_details.reasoning_tokens`. Both map to `llm.token_count.completion_details.reasoning`.

**Sources:** OpenAI Chat Completions usage — https://platform.openai.com/docs/api-reference/chat/object#chat/object-usage · OpenAI Responses usage — https://platform.openai.com/docs/api-reference/responses/object · `stream_options` opt-in — https://platform.openai.com/docs/api-reference/chat/create#chat-create-stream_options

### Cost (USD)

| Attribute | Type | Notes |
|---|---|---|
| `llm.cost.prompt` | float | Input cost |
| `llm.cost.completion` | float | Output cost |
| `llm.cost.total` | float | Combined |
| `llm.cost.prompt_details.{input,cache_write,cache_read,cache_input,audio}` | float | Detail breakdown (`cache_input` = cost of the tokens written to cache on this call; `cache_read` = cost of cache hits) |
| `llm.cost.completion_details.{output,reasoning,audio}` | float | Detail breakdown |

### Prompt templates

| Attribute | Type | Notes |
|---|---|---|
| `llm.prompt_template.template` | string | Template with `{variable}` syntax |
| `llm.prompt_template.variables` | JSON string | Key-value substitutions |
| `llm.prompt_template.version` | string | Template version |
| `prompt.vendor` | string | `langchain`, `langsmith`, `portkey`, `arize-phoenix` |
| `prompt.id` | string | Vendor-specific id |
| `prompt.url` | string | Vendor-specific URL |

---

## TOOL spans

| Attribute | Type | Notes |
|---|---|---|
| `tool.name` | string | Tool identifier |
| `tool.description` | string | Documentation |
| `tool.json_schema` | JSON string | Input spec |
| `tool.parameters` | JSON string | Parameter spec |
| `tool.id` | string | Tool call result identifier |

Pair with generic `input.value` / `output.value` for actual call args and return value.

---

## AGENT spans

`openinference.span.kind = "AGENT"` plus:

| Attribute | Type | Notes |
|---|---|---|
| `agent.name` | string | Required — used for UI grouping |
| `agent.role` | string | |
| `agent.framework` | string | `langgraph` / `crewai` / `microsoft-agent-framework` / `anthropic-agents` / `openai-agents` / `smolagents` / `llama-index` / `custom` |
| `input.value` | string | Triggering task or message |
| `output.value` | string | Final agent output |

---

## CHAIN spans (workflow / graph nodes)

`openinference.span.kind = "CHAIN"` plus generic `input.value`, `output.value`.

---

## EMBEDDING spans

`openinference.span.kind = "EMBEDDING"` plus:

| Attribute | Type | Notes |
|---|---|---|
| `embedding.model_name` | string | e.g. `text-embedding-3-small` |
| `embedding.text` | string | Input text |
| `embedding.vector` | float[] | Output vector |
| `embedding.embeddings` | list of objects | `…<i>.embedding.{text,vector}` for batched calls |
| `embedding.invocation_parameters` | JSON string | Excludes input |

Embedding spans do **not** use `llm.system` or `llm.provider`.

---

## RETRIEVER spans (RAG)

`openinference.span.kind = "RETRIEVER"` plus:

| Attribute | Type | Notes |
|---|---|---|
| `retrieval.documents` | list of objects | Flattened per document |
| `…<i>.document.id` | string / int | Unique identifier |
| `…<i>.document.content` | string | Retrieved text |
| `…<i>.document.score` | float | Relevance |
| `…<i>.document.metadata` | JSON string | Associated metadata |
| `input.value` | string | Query text |

---

## RERANKER spans

| Attribute | Type | Notes |
|---|---|---|
| `reranker.model_name` | string | e.g. `cross-encoder/ms-marco-MiniLM-L-12-v2` |
| `reranker.query` | string | Query text |
| `reranker.input_documents` | list of objects | Pre-rank |
| `reranker.output_documents` | list of objects | Post-rank |
| `reranker.top_k` | int | Number of top results returned |

---

## Generic input / output

Set on most span kinds for at-a-glance inspection in the UI.

| Attribute | Type | Notes |
|---|---|---|
| `input.value` | string | Operation input |
| `input.mime_type` | string | e.g. `application/json` |
| `output.value` | string | Operation output |
| `output.mime_type` | string | e.g. `application/json` |

---

## Audio

| Attribute | Type | Notes |
|---|---|---|
| `audio.url` | string | Cloud storage URL |
| `audio.mime_type` | string | `audio/mpeg`, `audio/wav`, … |
| `audio.transcript` | string | Transcribed text |

---

## Image

| Attribute | Type | Notes |
|---|---|---|
| `image.url` | string | URL or base64-encoded data |

---

## Agent / execution graph

| Attribute | Type | Notes |
|---|---|---|
| `agent.name` | string | |
| `graph.node.id` | string | Execution graph node identifier |
| `graph.node.name` | string | Human-readable node name |
| `graph.node.parent_id` | string | Parent node; empty = root |

---

## Resource attributes (project routing)

Set on the OTel `Resource` (not per-span). Phoenix reads these to route traces into projects when raw OTLP is used instead of `phoenix.otel.register()`.

**Sources:** Phoenix "Setup Tracing" / projects — https://docs.arize.com/phoenix/tracing/how-to-tracing/setup-tracing/setup-tracing-python

| Attribute | Type | Notes |
|---|---|---|
| `openinference.project.name` | string | Phoenix project the trace lands in. `register(project_name=...)` sets this for you; a manual `TracerProvider` (e.g. the multi-backend fan-out) must add it to `Resource.create({...})` itself, or traces land in the `default` project. Env-driven via `PHOENIX_PROJECT_NAME`. |

---

## Cross-cutting (Baggage)

Set once at the entry point with OTel baggage; promoted to span attributes via `BaggageSpanProcessor`.

**Sources:** OTel baggage API spec — https://opentelemetry.io/docs/specs/otel/baggage/api/ · `BaggageSpanProcessor` (PyPI `opentelemetry-processor-baggage`) — https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/processor/opentelemetry-processor-baggage

| Attribute | Type | Notes |
|---|---|---|
| `session.id` | string | Groups traces per conversation / session |
| `user.id` | string | |
| `tenant.id` | string | |
| `app.version` | string | |
| `metadata` | JSON string | Span-level metadata |
| `tag.tags` | string[] | Categorical tags |

---

## Exception handling

**Sources:** OTel exception semantic conventions — https://opentelemetry.io/docs/specs/semconv/exceptions/ (the OpenInference spec inherits these unchanged).

| Attribute | Type | Notes |
|---|---|---|
| `exception.type` | string | Exception class name |
| `exception.message` | string | Detailed error message |
| `exception.stacktrace` | string | Stack trace |
| `exception.escaped` | bool | Scope escape indicator |

---

## Flattening rules

OI uses **indexed-attribute prefixes** for arrays of objects:

```
<prefix>.<index>.<suffix>
```

Examples:
- `llm.input_messages.0.message.role`
- `llm.output_messages.1.message.content`
- `llm.tools.0.tool.json_schema`
- `llm.output_messages.0.message.tool_calls.0.tool_call.id`

Allowed leaf types: `bool`, `str`, `bytes`, `int`, `float`, or `List` variants thereof. Anything richer (objects, mixed lists) must be JSON-stringified before being set.
