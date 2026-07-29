# Gateway-Boundary Capture (opaque vendor runtimes)

observent's framework path assumes you can run code *inside* the agent — import an instrumentor, open `start_as_current_span`, propagate W3C context. That breaks for **vendor runtimes you don't control**: Claude Code, Cursor's composer, and similar coding agents run their loop in a process you can't instrument, so there's no way to propagate trace context *out* of the loop. The only seam you share with them is the **LLM gateway** every call flows through — a litellm proxy, Portkey, OpenRouter, Cloudflare AI Gateway, etc.

This page is the canonical reference for capturing at that seam. It instruments the proxy boundary and **stamps a stable correlation id** onto each call so that the calls belonging to one vendor-runtime run **group together** in the backend — by `session.id` (OpenInference) / `gen_ai.conversation.id` (OTel-GenAI). SKILL.md § Step 2.4 links here.

## The honest ceiling — grouping, not one trace

A gateway sees independent HTTP calls. It **cannot** reconstruct a single `trace_id` across a vendor loop (that would require context propagation the runtime never emits), and it **cannot** see the runtime's internal tool/sub-agent spans — only the LLM calls that egress through the proxy. What it *can* do is attach a shared key so the backend's session/conversation view collapses one run's calls into a single group. That is the realistic ceiling, and it is exactly what the gateway pattern delivers — per-call telemetry you already had, now **linked at the run level**.

> Don't confuse this with litellm's stock `callbacks: ["otel"]` export. That emits a span per call with **no run linkage** — the same orphaned per-call data. The value here is the **correlation-id stamping**, not the export.

---

## Maintainer's sources

**Gateway / proxy:**
- litellm — custom callbacks (`CustomLogger`) — https://docs.litellm.ai/docs/observability/custom_callback
- litellm — proxy logging, `proxy_server_request` headers / `metadata` — https://docs.litellm.ai/docs/proxy/logging
- litellm — proxy callbacks config (`litellm_settings.callbacks`) — https://docs.litellm.ai/docs/proxy/configs

**Injecting the correlation id from a vendor runtime:**
- Claude Code env vars — `ANTHROPIC_BASE_URL`, `ANTHROPIC_CUSTOM_HEADERS` — https://code.claude.com/docs/en/env-vars

**Conventions (grouping keys):**
- `session.id` — `references/openinference.md`
- `gen_ai.conversation.id` — `references/otel_genai.md`

Last reviewed: 2026-06-27.

---

## How the id makes it to the gateway

The correlation id is **injected at invocation** by the side you *do* control, and **recovered at the proxy** by the callback. Two id-sourcing paths:

| Path | When | How the id is set |
|---|---|---|
| **Injected header** | You can configure the runtime's HTTP client | Claude Code: set `ANTHROPIC_BASE_URL` → your litellm proxy and `ANTHROPIC_CUSTOM_HEADERS="x-observent-session-id: <run id>"`. The header rides on every model call of that session. Driving Claude Code per task via the Agent SDK / `claude -p` lets you mint a **fresh id per task**; an interactive session shares one id (still groups the whole session). |
| **MCP session id (fallback)** | You can't set headers, but the runtime reaches *your* tools over MCP | Read the MCP session id inside your MCP server and promote it to baggage as `mcp_session_id` (see `capture.md § Baggage promotion`). Use the same value as the header name below so both paths converge on one key. |

```
Claude Code / Cursor (opaque loop)
  ANTHROPIC_BASE_URL      = http://localhost:4000        (the litellm proxy)
  ANTHROPIC_CUSTOM_HEADERS= x-observent-session-id: run-2026-06-27-abc123
        │  per-call HTTP — the id rides in the header
        ▼
  litellm PROXY ── observent_litellm.handler ──▶ reads header, emits an LLM span
        │                                          stamped session.id / gen_ai.conversation.id
        ▼                                                     │
  upstream model (Anthropic / OpenAI / …)        backend groups the run's calls
```

---

## The reference adapter — `observent_litellm.py`

A litellm `CustomLogger` that runs **in the proxy process**. On every completed call it reads the correlation id off the incoming request and emits one convention-correct LLM span carrying that id. `_CONVENTION` is a generation-time literal derived from the chosen backend set (same rule as `observent_capture.py` — see `matrix.md § Convention resolution`). The adapter is intentionally self-contained (no `observent_capture` import) because the proxy is usually a separate deployment from the agent app.

```python
# observent_litellm.py — litellm proxy CustomLogger.
# Stamps a stable correlation id onto every LLM call so calls from an opaque
# vendor runtime (Claude Code, Cursor, ...) group into one run in the backend.
#
# Register in the proxy config:
#   litellm_settings:
#     callbacks: ["observent_litellm.handler"]
from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from litellm.integrations.custom_logger import CustomLogger
from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode

_CONVENTION = "otel-genai"  # one of: "oi" | "otel-genai" | "both" — generation-time literal
# Header the vendor runtime injects (Claude Code ANTHROPIC_CUSTOM_HEADERS, Cursor, curl, ...).
_CORRELATION_HEADER = os.getenv("OBSERVENT_CORRELATION_HEADER", "x-observent-session-id").lower()

_tracer = trace.get_tracer("observent.gateway")


def _to_nanos(t: Any) -> int | None:
    return int(t.timestamp() * 1_000_000_000) if isinstance(t, datetime) else None


def _request_headers(kwargs: dict[str, Any]) -> dict[str, str]:
    """Incoming headers as the proxy received them (keys lower-cased)."""
    params = kwargs.get("litellm_params") or {}
    req = params.get("proxy_server_request") or {}
    raw = req.get("headers") or {}
    return {str(k).lower(): str(v) for k, v in dict(raw).items()}


def _correlation_id(kwargs: dict[str, Any]) -> str | None:
    # 1. Injected header — the primary path.
    hid = _request_headers(kwargs).get(_CORRELATION_HEADER)
    if hid:
        return hid
    # 2. Fallback: litellm request metadata (e.g. an MCP-session id forwarded as metadata).
    meta = (kwargs.get("litellm_params") or {}).get("metadata") or {}
    for key in ("session_id", "session.id", "conversation_id", "mcp_session_id", "run_id"):
        val = meta.get(key)
        if val:
            return str(val)
    return None


def _usage(response_obj: Any) -> dict[str, int]:
    usage = getattr(response_obj, "usage", None)
    if usage is None and isinstance(response_obj, dict):
        usage = response_obj.get("usage")
    if usage is None:
        return {}
    get = usage.get if isinstance(usage, dict) else lambda k, d=None: getattr(usage, k, d)
    out: dict[str, int] = {}
    for name in ("prompt_tokens", "completion_tokens", "total_tokens"):
        v = get(name)
        if isinstance(v, int):
            out[name] = v
    # Anthropic prompt-cache metrics (mandatory for Claude Code's Anthropic calls).
    details = get("prompt_tokens_details") or {}
    cdet = details if isinstance(details, dict) else {}
    for src, dst in (("cached_tokens", "cache_read"), ("cache_creation_tokens", "cache_write")):
        v = cdet.get(src)
        if isinstance(v, int):
            out[dst] = v
    return out


def _set_correlation(span: trace.Span, cid: str) -> None:
    if _CONVENTION in ("oi", "both"):
        span.set_attribute("session.id", cid)
    if _CONVENTION in ("otel-genai", "both"):
        span.set_attribute("gen_ai.conversation.id", cid)
        span.set_attribute("session.id", cid)  # general semconv; backends index it too


def _set_llm(span: trace.Span, model: str | None, provider: str | None, u: dict[str, int]) -> None:
    if _CONVENTION in ("oi", "both"):
        span.set_attribute("openinference.span.kind", "LLM")
        if model:
            span.set_attribute("llm.model_name", model)
        if "prompt_tokens" in u:
            span.set_attribute("llm.token_count.prompt", u["prompt_tokens"])
        if "completion_tokens" in u:
            span.set_attribute("llm.token_count.completion", u["completion_tokens"])
        if "total_tokens" in u:
            span.set_attribute("llm.token_count.total", u["total_tokens"])
        if "cache_read" in u:
            span.set_attribute("llm.token_count.prompt_details.cache_read", u["cache_read"])
        if "cache_write" in u:
            span.set_attribute("llm.token_count.prompt_details.cache_write", u["cache_write"])
    if _CONVENTION in ("otel-genai", "both"):
        span.set_attribute("gen_ai.operation.name", "chat")
        if model:
            span.set_attribute("gen_ai.request.model", model)
        if provider:
            span.set_attribute("gen_ai.provider.name", provider)
        if "prompt_tokens" in u:
            span.set_attribute("gen_ai.usage.input_tokens", u["prompt_tokens"])
        if "completion_tokens" in u:
            span.set_attribute("gen_ai.usage.output_tokens", u["completion_tokens"])
        if "cache_read" in u:
            span.set_attribute("gen_ai.usage.cache_read.input_tokens", u["cache_read"])
        if "cache_write" in u:
            span.set_attribute("gen_ai.usage.cache_creation.input_tokens", u["cache_write"])


def _emit(kwargs: dict[str, Any], response_obj: Any, start: Any, end: Any, ok: bool) -> None:
    start_ns = _to_nanos(start)
    span = _tracer.start_span(
        "chat", kind=SpanKind.CLIENT, start_time=start_ns,
    )
    try:
        model = kwargs.get("model")
        provider = kwargs.get("custom_llm_provider")
        cid = _correlation_id(kwargs)
        if cid:
            _set_correlation(span, cid)
        _set_llm(span, model, provider, _usage(response_obj))
        span.set_status(Status(StatusCode.OK if ok else StatusCode.ERROR))
    finally:
        span.end(end_time=_to_nanos(end))


class ObserventGatewayLogger(CustomLogger):
    """Emits one correlated LLM span per proxied call (success or failure)."""

    def log_success_event(self, kwargs, response_obj, start_time, end_time):  # type: ignore[no-untyped-def]
        _emit(kwargs, response_obj, start_time, end_time, ok=True)

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):  # type: ignore[no-untyped-def]
        _emit(kwargs, response_obj, start_time, end_time, ok=True)

    def log_failure_event(self, kwargs, response_obj, start_time, end_time):  # type: ignore[no-untyped-def]
        _emit(kwargs, response_obj, start_time, end_time, ok=False)

    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):  # type: ignore[no-untyped-def]
        _emit(kwargs, response_obj, start_time, end_time, ok=False)


handler = ObserventGatewayLogger()
```

### Wiring the TracerProvider in the proxy process

The proxy is its own process, so it needs its own exporter to your backend. Set this up once at import time (before any span is emitted) — e.g. in the same module, or a sibling imported first:

```python
# observent_gateway_otel.py — imported before observent_litellm in the proxy.
import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

provider = TracerProvider(resource=Resource.create({"service.name": "litellm-gateway"}))
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
    endpoint=os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"],   # your backend's OTLP/HTTP traces URL
)))
trace.set_tracer_provider(provider)
```

Point `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` (and any auth header via `OTEL_EXPORTER_OTLP_TRACES_HEADERS`) at the chosen backend's endpoint — the same endpoints listed in `SKILL.md § Step 2.5` / `matrix.md`. The convention literal in `observent_litellm.py` must match what that backend expects (`oi` for Phoenix, `otel-genai` for Langfuse/SigNoz/…, `both` when Phoenix is mixed with an OTel-GenAI backend).

---

## Proxy config + env vars

```yaml
# litellm_config.yaml
model_list:
  - model_name: claude-sonnet-4-6
    litellm_params:
      model: anthropic/claude-sonnet-4-6
litellm_settings:
  callbacks: ["observent_litellm.handler"]
```

```bash
# Proxy side:
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://localhost:3000/api/public/otel/v1/traces  # Langfuse
export OTEL_EXPORTER_OTLP_TRACES_HEADERS="Authorization=Basic <base64 pk:sk>"
python observent_gateway_otel.py >/dev/null 2>&1  # or import it from the callback module
litellm --config litellm_config.yaml --port 4000

# Vendor-runtime side (Claude Code):
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_CUSTOM_HEADERS="x-observent-session-id: $(uuidgen)"
claude -p "refactor the auth module"
```

| Env var | Side | Purpose |
|---|---|---|
| `OBSERVENT_CORRELATION_HEADER` | proxy | Header the callback reads (default `x-observent-session-id`) |
| `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` / `_HEADERS` | proxy | Where the gateway spans go + auth |
| `ANTHROPIC_BASE_URL` | runtime | Routes Claude Code's calls through the proxy |
| `ANTHROPIC_CUSTOM_HEADERS` | runtime | Injects the per-run correlation id |

---

## Out of scope

- **Not a single trace.** Calls group by `session.id` / `gen_ai.conversation.id`; they do not share a `trace_id`. Reconstructing one trace would require context the vendor loop never emits.
- **Not internal spans.** Tool calls, sub-agents, and retrieval inside the vendor runtime are invisible at the gateway — only egress LLM calls are seen.
- **Not a backend or framework.** The gateway is a *capture seam*, not a row in the 9×7 matrix; litellm is the reference adapter, but the same `CustomLogger` shape ports to other gateways.

**Sources:** litellm custom callbacks — https://docs.litellm.ai/docs/observability/custom_callback · litellm proxy logging / request headers — https://docs.litellm.ai/docs/proxy/logging · litellm proxy callbacks config — https://docs.litellm.ai/docs/proxy/configs · Claude Code env vars (`ANTHROPIC_BASE_URL`, `ANTHROPIC_CUSTOM_HEADERS`) — https://code.claude.com/docs/en/env-vars · `session.id` — `references/openinference.md` · `gen_ai.conversation.id` — `references/otel_genai.md`

*Last verified: 2026-06-27 with Python 3.12, litellm 1.86, OpenTelemetry API/SDK 1.41.*
