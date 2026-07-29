# OpenTelemetry GenAI Semantic Conventions

Canonical attribute reference for the OTel-GenAI spec — the convention Langfuse, SigNoz, Elastic APM, LangSmith, Opik, and Jaeger consume. observent emits these keys when the resolved convention is `otel-genai` or `both` (see `../SKILL.md` Step 3).

**Status:** This spec is in development (experimental) upstream; attribute names may shift. As of 2026-06, the GenAI conventions are being split out of the main `open-telemetry/semantic-conventions` repo into a dedicated `open-telemetry/semantic-conventions-genai` repo (the registry entries are marked *Moved*); the rendered `docs/gen-ai/` paths below still resolve. Re-verify the source URLs, and the floor, before bumping.

---

## Maintainer's sources

Every table below derives from the OTel-GenAI spec, which lives in two places (rendered docs + spec source). Per-section `**Sources:**` bullets call out subsections that point to additional upstream artifacts (events, metrics, provider supplements, sampling, errors).

**Primary spec:**
- Rendered docs (gen-ai) — https://opentelemetry.io/docs/specs/semconv/gen-ai/
- Spec source — https://github.com/open-telemetry/semantic-conventions/tree/main/docs/gen-ai
- Stability/status & roadmap — https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/README.md

**Adjacent specs cited by individual sections:**
- gen-ai events — https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-events.md (§ Events)
- gen-ai metrics — https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-metrics.md (§ Metrics)
- Per-provider supplements (`anthropic.md`, `openai.md`, `azure-ai-inference.md`, `aws-bedrock.md`, `mcp.md`) — https://github.com/open-telemetry/semantic-conventions/tree/main/docs/gen-ai (§ Framework-specific notes)
- OTel sampling — https://opentelemetry.io/docs/concepts/sampling/ (§ Sampling-decision attributes)
- OTel error attributes — https://opentelemetry.io/docs/specs/semconv/general/attributes/#error-attributes (§ Errors)

Last reviewed: 2026-07-03.

---

## Span name conventions

| Span type | Span name format |
|---|---|
| Inference (chat / text completion) | `{gen_ai.operation.name} {gen_ai.request.model}` |
| Embeddings | `{gen_ai.operation.name} {gen_ai.request.model}` |
| Retrievals | `{gen_ai.operation.name} {gen_ai.data_source.id}` |
| Create agent | `create_agent {gen_ai.agent.name}` |
| Invoke agent (local) | `invoke_agent {gen_ai.agent.name}` (span kind `INTERNAL`) |
| Invoke agent (remote) | `invoke_agent {gen_ai.agent.name}` (span kind `CLIENT`) |

Default span kind is `CLIENT`; use `INTERNAL` for same-process operations.

---

## Required attributes (every gen_ai span)

| Attribute | Type | Notes |
|---|---|---|
| `gen_ai.operation.name` | string | One of the well-known values below |
| `gen_ai.provider.name` | string | One of the well-known providers below |

### Well-known `gen_ai.operation.name` values

`chat`, `text_completion`, `embeddings`, `retrieval`, `generate_content`, `execute_tool`, `create_agent`, `invoke_agent`, `invoke_workflow`.

### Well-known `gen_ai.provider.name` values

`openai`, `anthropic`, `aws.bedrock`, `azure.ai.openai`, `azure.ai.inference`, `gcp.gemini`, `gcp.vertex_ai`, `gcp.gen_ai`, `cohere`, `mistral_ai`, `groq`, `deepseek`, `perplexity`, `x_ai`, `ibm.watsonx.ai`.

---

## Conditionally required

| Attribute | Type | When |
|---|---|---|
| `gen_ai.request.model` | string | When available |
| `gen_ai.conversation.id` | string | When a conversation / thread id exists |
| `gen_ai.output.type` | string | When applicable — `text`, `image`, `json`, `speech` |
| `gen_ai.request.choice.count` | int | When the request asked for ≠1 choices |
| `gen_ai.data_source.id` | string | For retrieval spans |
| `error.type` | string | When the operation ends in error (provider error code or canonical exception name) |

---

## Recommended

### Response

| Attribute | Type | Applies to |
|---|---|---|
| `gen_ai.response.id` | string | All operations |
| `gen_ai.response.model` | string | All operations |
| `gen_ai.response.finish_reasons` | string[] | Inference |
| `gen_ai.response.time_to_first_chunk` | double | Streaming requests |

### Token usage

| Attribute | Type | Notes |
|---|---|---|
| `gen_ai.usage.input_tokens` | int | All operations |
| `gen_ai.usage.output_tokens` | int | Inference / generation |
| `gen_ai.usage.cache_creation.input_tokens` | int | When applicable (Anthropic) |
| `gen_ai.usage.cache_read.input_tokens` | int | When applicable (Anthropic) |
| `gen_ai.usage.reasoning.output_tokens` | int | When applicable (reasoning models) |

**Totals are inclusive.** Per the upstream registry, `cache_creation.input_tokens` and `cache_read.input_tokens` are already **counted inside** `gen_ai.usage.input_tokens`, and `reasoning.output_tokens` inside `gen_ai.usage.output_tokens` — they are breakdowns, not addends. Don't re-add them when computing totals or cost.

**Source-API note (OpenAI: Chat Completions vs Responses).** OTel-GenAI's canonical names (`gen_ai.usage.input_tokens` / `output_tokens`) match the OpenAI **Responses API** shape directly. For **Chat Completions**, the instrumentor maps `prompt_tokens → input_tokens` and `completion_tokens → output_tokens` — verify your instrumentor version applies the mapping for both endpoints if your agent mixes APIs. **Streaming gotcha:** Chat Completions streaming omits usage unless the request passes `stream_options={"include_usage": True}` (usage then arrives on the final SSE chunk); Responses API includes usage automatically. Without the opt-in, `gen_ai.usage.*` will be missing. **Reasoning tokens (o-series):** Both APIs map to `gen_ai.usage.reasoning.output_tokens` via the instrumentor — Responses surfaces them under `usage.output_tokens_details.reasoning_tokens`, Chat Completions under `usage.completion_tokens_details.reasoning_tokens`.

**Sources:** OpenAI Chat Completions usage — https://platform.openai.com/docs/api-reference/chat/object#chat/object-usage · OpenAI Responses usage — https://platform.openai.com/docs/api-reference/responses/object · `stream_options` opt-in — https://platform.openai.com/docs/api-reference/chat/create#chat-create-stream_options

### Request parameters

| Attribute | Type | Applies to |
|---|---|---|
| `gen_ai.request.temperature` | double | Inference |
| `gen_ai.request.top_p` | double | Inference |
| `gen_ai.request.top_k` | double | Inference / retrieval |
| `gen_ai.request.max_tokens` | int | Inference |
| `gen_ai.request.frequency_penalty` | double | Inference |
| `gen_ai.request.presence_penalty` | double | Inference |
| `gen_ai.request.stop_sequences` | string[] | Inference |
| `gen_ai.request.seed` | int | When in request |
| `gen_ai.request.stream` | bool | When streaming |

### Embeddings

| Attribute | Type | Notes |
|---|---|---|
| `gen_ai.embeddings.dimension.count` | int | Output vector dimension |
| `gen_ai.request.encoding_formats` | string[] | Encoding formats requested |

### Server

| Attribute | Type | Notes |
|---|---|---|
| `server.address` | string | All operations |
| `server.port` | int | When `server.address` is set |

---

## Opt-in (sensitive content — may contain PII)

These are **not** emitted by default. Enable only when capturing prompt / completion content is acceptable for your privacy posture.

| Attribute | Type | Notes |
|---|---|---|
| `gen_ai.input.messages` | JSON | Chat history (schema: `gen-ai-input-messages.json`) |
| `gen_ai.output.messages` | JSON | Model responses (schema: `gen-ai-output-messages.json`) |
| `gen_ai.system_instructions` | JSON | System prompts (schema: `gen-ai-system-instructions.json`) |
| `gen_ai.tool.definitions` | JSON | Available tool specs (schema: `gen-ai-tool-definitions.json`) |
| `gen_ai.retrieval.documents` | JSON | Retrieved docs with id, score (schema: `gen-ai-retrieval-documents.json`) |
| `gen_ai.retrieval.query.text` | string | Retrieval query text |

---

## Agent spans

`gen_ai.operation.name` ∈ `{create_agent, invoke_agent, invoke_workflow}` plus:

| Attribute | Type | Requirement | Notes |
|---|---|---|---|
| `gen_ai.agent.id` | string | Conditionally required | Unique agent identifier |
| `gen_ai.agent.name` | string | Conditionally required | Human-readable name |
| `gen_ai.agent.version` | string | Conditionally required | Agent version |
| `gen_ai.agent.description` | string | Conditionally required | Free-form description |

Agents reuse the request / usage / response attributes above when invoking a model.

---

## Tool execution (`execute_tool` spans)

`gen_ai.operation.name = "execute_tool"`, span kind `INTERNAL`, span name `execute_tool {gen_ai.tool.name}`.

| Attribute | Type | Requirement | Notes |
|---|---|---|---|
| `gen_ai.tool.name` | string | Required | Tool the model invoked (e.g. `get_weather`) |
| `gen_ai.tool.call.id` | string | Recommended (if available) | Correlates to the `tool_call` part in `gen_ai.output.messages` |
| `gen_ai.tool.description` | string | Recommended (if available) | Free-form tool description |
| `gen_ai.tool.type` | string | Recommended (if available) | e.g. `function`, `extension`, `datastore` |
| `gen_ai.tool.call.arguments` | any / JSON | Opt-in (sensitive) | Parameters passed to the call — may contain PII; JSON-stringify if structured form unsupported |
| `gen_ai.tool.call.result` | any / JSON | Opt-in (sensitive) | Value the tool returned — may contain PII |

The advertised tool list (`gen_ai.tool.definitions`) is set on the **inference** span, not here — see § Opt-in.

---

## Sampling-decision attributes

These attributes should be populated **at span start** so head-based samplers can use them. Don't compute them lazily.

`gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`, `server.address`, `server.port`.

---

## Events

The spec defines structured input / output events as an alternative to opt-in content attributes. See upstream `gen-ai-events.md`. observent currently uses the attribute form; revisit if backends start preferring events.

**Sources:** https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-events.md

---

## Metrics

The spec defines:

- `gen_ai.client.token.usage` — histogram, per-token usage by operation.
- `gen_ai.client.operation.duration` — histogram, end-to-end operation latency.
- `gen_ai.server.request.duration` — histogram (server-side equivalent).
- `gen_ai.server.time_per_output_token` — histogram for streaming.

See upstream `gen-ai-metrics.md`. Backends ingest these alongside spans.

**Sources:** https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-metrics.md

---

## Framework-specific notes

The upstream spec includes per-provider supplements. Summary:

- **`anthropic.md`** — `gen_ai.usage.cache_creation.input_tokens`, `gen_ai.usage.cache_read.input_tokens` are the canonical Anthropic prompt-cache metrics. `gen_ai.provider.name = "anthropic"`.
- **`openai.md`** — covers Chat Completions and Responses API. `gen_ai.provider.name = "openai"` (or `"azure.ai.openai"` for Azure-hosted).
- **`azure-ai-inference.md`** — `gen_ai.provider.name = "azure.ai.inference"`.
- **`aws-bedrock.md`** — `gen_ai.provider.name = "aws.bedrock"`. Includes guidance on Converse API.
- **`mcp.md`** — Model Context Protocol semantics for tool / resource interactions.

**Sources:** per-provider supplements live alongside the main spec at https://github.com/open-telemetry/semantic-conventions/tree/main/docs/gen-ai — re-check each `.md` for added providers or renamed attributes when bumping the verified date above.

---

## Errors

When a span ends in error, set:

| Attribute | Type | Notes |
|---|---|---|
| `error.type` | string | Provider error code (`rate_limit_exceeded`, `invalid_request_error`, …) or canonical exception name |

Pair with the standard OTel `record_exception()` API.

**Sources:** OTel general error attributes — https://opentelemetry.io/docs/specs/semconv/general/attributes/#error-attributes · OTel exception semconv — https://opentelemetry.io/docs/specs/semconv/exceptions/
