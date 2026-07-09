# AI-Boundary Input/Output Capture

observent's prime directive is **never miss any input or output that crosses the AI-system boundary** — the prompt, the request state, the run config, and the result — regardless of *how* the agent was triggered (HTTP request, CLI invocation, queue/worker job, cron, notebook). This capture is **transport-agnostic**: it attaches to the agent run itself, not to any web framework.

The mechanism is a single generated module, `observent_capture.py`, plus a thin optional HTTP adapter. The same engine powers every entry point, so adding observability to a FastAPI route, a Celery task, and a `python main.py` script all produce the same `input.*` / `output.*` / status attributes on the run's root span.

This page is the canonical reference for that engine. SKILL.md § Step 2.3 links here.

---

## Maintainer's sources

**Specs:**
- OTel trace API — current span & status — https://opentelemetry.io/docs/languages/python/instrumentation/#set-span-status
- OTel `record_exception()` / exception semconv — https://opentelemetry.io/docs/specs/semconv/exceptions/
- OTel baggage API — https://opentelemetry.io/docs/specs/otel/baggage/api/
- W3C Baggage — https://www.w3.org/TR/baggage/

**Instrumentors & processors:**
- `opentelemetry-processor-baggage` (`BaggageSpanProcessor`) — https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/processor/opentelemetry-processor-baggage
- `opentelemetry-instrumentation-asgi` (`exclude_spans` knob, header capture) — https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/asgi/asgi.html

**OTel SDK knobs cited under § Truncation:**
- `OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT` / `OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT` — https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/

Last reviewed: 2026-06-20.

---

## Core principle — enrich in place, never duplicate the root span

observent does **not** open its own root span for the agent run. The framework instrumentor (LangChain / CrewAI / LlamaIndex / …) — or the transport instrumentor (e.g. `opentelemetry-instrumentation-fastapi`) — has already opened a root span by the time the agent is invoked. observent **enriches that existing span**:

```python
span = trace.get_current_span()
if span.is_recording():
    # Normal path: stamp input/output/status (+ agent identity) onto the span
    # that's already current.
    enrich_current_span(inputs)
else:
    # Fallback ONLY when nothing is recording (e.g. a bare CLI before any
    # instrumentor opened a span). Prime directive = never miss input, so open a
    # minimal root rather than silently drop it. Named f"{_SERVICE_NAME}.run".
    with tracer.start_as_current_span(f"{_SERVICE_NAME}.run") as span:
        ...
```

This is why there is **no second root span** behind HTTP or inside a framework run — the attributes land on the existing root. The fallback span appears only in the rare "nothing open" case, and is documented so it is never a surprise. Both branches go through the public `open_or_enrich_span(...)` (see § Public entry point), which also stamps the mandatory agent-identity attributes and names the fallback span for readability.

### Attribute namespacing

Because the attributes ride a span observent did not name, every captured key is namespaced so it can never collide with the host span's own attributes:

| Namespace | Sourced from | Convention mapping |
|---|---|---|
| `input.value` / `input.<path>` | The run's input (prompt, state dict, request body) | OI native key is `input.value`; flattened leaves use `input.<path>` |
| `output.value` / `output.<path>` | The run's result | OI native key is `output.value`; flattened leaves use `output.<path>` |
| `input.mime_type` / `output.mime_type` | Derived from the payload's Python type | `application/json` when the payload is a dict/list (JSON-serialized), `text/plain` otherwise |
| `gen_ai.prompt` / `gen_ai.completion` | Same data, OTel-GenAI convention | Emitted when `_CONVENTION` ∈ {`otel-genai`, `both`} |

**Serialization, not `str()`.** A dict/list payload is rendered via `json.dumps(..., default=str)` for `.value`, not Python's `str()` — `str({'query': 'x'})` produces Python repr syntax (single-quoted keys), which is not valid JSON despite `input.mime_type = application/json`. A payload that is already a string (e.g. an agent's final text output) passes through unchanged — it looks "plainer" than a dict-shaped input by nature of being a string, not because of a bug; its `mime_type` is `text/plain`.

**No bare `namespace` key for a scalar payload.** `_write` only runs the `_flatten` per-leaf loop when the payload is a dict/list. A scalar payload (a plain-string output) is *not* flattened — only `namespace.value` is set. Flattening it anyway would fall through to `_flatten`'s generic branch and yield a bare `namespace` key (no dot) holding the same content `namespace.value` already carries: a silent duplicate of a potentially large string, and a key shape that breaks the `namespace.value` / `namespace.<path>` contract this table promises.

The flattening rules (dot-notation, lists-of-primitives kept native, lists-of-objects indexed, `None` dropped) are identical to the HTTP adapter below — they share `_flatten`.

---

## Span status (set at the AI boundary)

The engine sets span status on the run's root span itself, so status no longer depends on whether a transport instrumentor happens to be present:

- **Success** → `span.set_status(Status(StatusCode.OK))`.
- **Exception** → `span.record_exception(exc)`, `span.set_status(Status(StatusCode.ERROR, str(exc)))`, and `error.type` = the exception's qualified name, then re-raise. This pairs the OTel `record_exception()` API (see `otel_genai.md § Errors`) with an explicit ERROR status — the exception event *and* the status both land on the span.

---

## Redaction & baggage promotion

Both are **generation-time literals** in the generated file (no env-var override — same rule as `_CONVENTION`). The redaction list (auth credentials, session/CSRF, PII) and the baggage whitelist are unchanged from observent's prior design; sensitive values become `***REDACTED***` (key preserved so the attribute shape is stable), and a configurable whitelist of leaf keys is promoted into OTel baggage so a `BaggageSpanProcessor` stamps them onto every child span (LLM / tool / agent). See § Baggage promotion below.

---

## Canonical engine

Generated as `observent_capture.py` in the user's project root. **Zero web-framework imports** — depends only on `opentelemetry-api`.

```python
# observent_capture.py
"""Transport-agnostic capture of the input/output that crosses the AI-system
boundary, plus run status, as attributes on the agent run's existing root span.

Works identically whether the agent is triggered by HTTP, a CLI, a queue worker,
or a script: enrich_current_span() stamps onto whatever span is current, and
capture_run() wraps any callable. No web framework required.

Generated by observent. Edit _REDACT_KEYS / _PROMOTE_TO_BAGGAGE / _CONVENTION to
customize; no env-var override is read at runtime by design.
"""
from __future__ import annotations

import functools
import json
from contextlib import nullcontext
from typing import Any, Awaitable, Callable, Iterator, TypeVar

from opentelemetry import baggage, context, trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.util.types import AttributeValue

_CONVENTION = "oi"  # one of: "oi" | "otel-genai" | "both" — generation-time literal

# Multi-agent identity, all generation-time literals (no runtime env override, same
# rule as _CONVENTION). These name the fallback root span and stamp the "mandatory"
# agent-identity attributes (matrix.md § Mandatory Span Attributes) so a trace list
# is legible without opening resource attributes. The skill fills them from
# spec.choice at generation time; callers can still override per-call via
# open_or_enrich_span(name=..., agent_name=..., agent_role=..., agent_framework=...).
_SERVICE_NAME = "agent"  # names the fallback root span: f"{_SERVICE_NAME}.run"
_AGENT_NAME = "agent"    # agent.name / gen_ai.agent.name on the run's root span
_AGENT_ROLE = ""         # agent.role (OI); "" = omit
_FRAMEWORK = ""          # agent.framework (OI), e.g. "crewai" | "langgraph"; "" = omit (overridable per-call via agent_framework=)

_REDACT_KEYS: frozenset[str] = frozenset({
    "api_key", "apikey", "api-key",
    "authorization", "bearer",
    "token", "access_token", "refresh_token", "id_token",
    "secret", "client_secret",
    "password", "passwd", "pwd",
    "x-api-key", "x_api_key",
    "openai_api_key", "anthropic_api_key", "azure_openai_key",
    "aws_access_key", "aws_access_key_id",
    "aws_secret", "aws_secret_access_key",
    "cookie", "set-cookie",
    "session", "session_id", "sessionid",
    "csrf", "csrf_token", "x-csrf-token", "xsrf-token",
    "email", "e_mail", "email_address",
    "phone", "phone_number", "mobile",
    "ssn", "social_security_number",
    "credit_card", "card_number", "cvv", "cvc",
    "dob", "date_of_birth", "birth_date",
})
_REDACTED = "***REDACTED***"

# Leaf names promoted from the flattened input into OTel baggage, so a
# BaggageSpanProcessor can stamp them onto every child span.
_PROMOTE_TO_BAGGAGE: frozenset[str] = frozenset({
    "tenant_id",
    "user_id",
    "session_id",
    "request_id",
    "conversation_id",
    "run_id",
    "mcp_session_id",
})

# OTel attribute values must be one of these primitives, or a list of them.
_PRIMITIVES = (str, bool, int, float)

_tracer = trace.get_tracer("observent.capture")

F = TypeVar("F", bound=Callable[..., Any])
AF = TypeVar("AF", bound=Callable[..., Awaitable[Any]])


def _is_sensitive(key: str) -> bool:
    k = key.lower()
    return any(needle in k for needle in _REDACT_KEYS)


def _coerce(value: Any) -> AttributeValue:
    if isinstance(value, _PRIMITIVES):
        return value
    if isinstance(value, (list, tuple)) and all(isinstance(v, _PRIMITIVES) for v in value):
        return list(value)
    return str(value)


def _flatten(prefix: str, value: Any) -> Iterator[tuple[str, AttributeValue]]:
    """Yield (attribute_key, attribute_value) pairs from an arbitrary payload.

    - Dicts recurse with `{prefix}.{key}`. A sensitive key short-circuits to ***REDACTED***.
    - Lists of primitives are kept as a single OTel list attribute.
    - Lists of objects flatten with an integer index segment.
    - None is dropped (OTel disallows None attribute values).
    """
    if value is None:
        return
    if isinstance(value, dict):
        for k, v in value.items():
            child_key = f"{prefix}.{k}" if prefix else str(k)
            if _is_sensitive(str(k)):
                yield child_key, _REDACTED
            else:
                yield from _flatten(child_key, v)
        return
    if isinstance(value, (list, tuple)):
        if all(isinstance(v, _PRIMITIVES) or v is None for v in value):
            cleaned = [v for v in value if v is not None]
            if cleaned:
                yield prefix, _coerce(cleaned)
            return
        for i, v in enumerate(value):
            yield from _flatten(f"{prefix}.{i}", v)
        return
    yield prefix, _coerce(value)


def _promote_baggage(attr_key: str, value: AttributeValue, ctx: context.Context) -> context.Context:
    if value == _REDACTED:
        return ctx
    leaf = attr_key.rsplit(".", 1)[-1]
    if leaf not in _PROMOTE_TO_BAGGAGE:
        return ctx
    return baggage.set_baggage(leaf, str(value), context=ctx)


def _serialize(payload: Any) -> tuple[str, str]:
    """Render `payload` as a single string for `.value` / `gen_ai.*`, alongside its
    mime type. A dict/list becomes valid JSON (`json.dumps`, not Python's `str()`,
    which would emit repr-style single-quoted syntax); a payload that is already a
    string passes through untouched; anything else falls back to `str()`."""
    if isinstance(payload, str):
        return payload, "text/plain"
    if isinstance(payload, (dict, list, tuple)):
        try:
            return json.dumps(payload, default=str, ensure_ascii=False), "application/json"
        except TypeError:
            return str(payload), "text/plain"
    return str(payload), "text/plain"


def _write(span: trace.Span, namespace: str, payload: Any) -> None:
    """Flatten `payload` under `namespace` and set each leaf as a span attribute.

    Also sets the OI-native `input.value` / `output.value` (+ `.mime_type`) and,
    when the convention calls for it, the OTel-GenAI `gen_ai.*` mirror.
    """
    if not span.is_recording():
        return
    ctx = context.get_current()
    # Only recurse into dict/list payloads for per-leaf attributes (input.query,
    # output.reply, ...). A scalar payload (e.g. a plain-string agent output) has
    # no leaves to flatten — falling through to _flatten's fallback branch would
    # yield a *bare* `namespace` key holding the same content the `.value` mirror
    # below already carries, duplicating a potentially large string on the span.
    if isinstance(payload, (dict, list, tuple)):
        for key, val in _flatten(namespace, payload):
            span.set_attribute(key, val)
            ctx = _promote_baggage(key, val, ctx)
        if ctx is not context.get_current():
            context.attach(ctx)  # promote into the active context for child spans

    # Convention-native single-value mirrors (so each backend's UI lights up).
    flat_str, mime_type = _serialize(payload)
    if _CONVENTION in ("oi", "both"):
        span.set_attribute(f"{namespace}.value", flat_str)
        span.set_attribute(f"{namespace}.mime_type", mime_type)
    if _CONVENTION in ("otel-genai", "both"):
        gen_ai_key = "gen_ai.prompt" if namespace == "input" else "gen_ai.completion"
        span.set_attribute(gen_ai_key, flat_str)


def enrich_current_span(inputs: Any) -> trace.Span:
    """Stamp `input.*` attributes (with redaction + baggage promotion) onto the
    span that is currently recording. Returns that span. Safe to call when no
    span is recording (it becomes a no-op and returns the non-recording span)."""
    span = trace.get_current_span()
    _write(span, "input", inputs)
    return span


def capture_output(result: Any, span: trace.Span | None = None) -> Any:
    """Stamp `output.*` attributes onto `span` (or the current span). Returns the
    result unchanged so it can wrap a return value inline."""
    _write(span or trace.get_current_span(), "output", result)
    return result


def set_ok(span: trace.Span | None = None) -> None:
    span = span or trace.get_current_span()
    if span.is_recording():
        span.set_status(Status(StatusCode.OK))


def set_error(exc: BaseException, span: trace.Span | None = None) -> None:
    span = span or trace.get_current_span()
    if span.is_recording():
        span.record_exception(exc)
        span.set_attribute("error.type", type(exc).__qualname__)
        span.set_status(Status(StatusCode.ERROR, str(exc)))


def _set_agent_identity(
    span: trace.Span,
    agent_name: str | None = None,
    agent_role: str | None = None,
    agent_framework: str | None = None,
) -> None:
    """Stamp the mandatory multi-agent identity attributes onto `span`, per the
    resolved convention. Params override the generation-time literals (including
    agent_framework, which overrides _FRAMEWORK — the way a single shared
    observent_capture.py can serve multiple frameworks in a multi-service repo).
    Applied to the run's root span (both the enriched framework span and the
    fallback), so every trace shows *which* agent produced it without opening
    resource attrs."""
    if not span.is_recording():
        return
    name = agent_name or _AGENT_NAME
    role = agent_role or _AGENT_ROLE
    framework = agent_framework or _FRAMEWORK
    if _CONVENTION in ("oi", "both"):
        span.set_attribute("openinference.span.kind", "AGENT")
        if name:
            span.set_attribute("agent.name", name)
        if role:
            span.set_attribute("agent.role", role)
        if framework:
            span.set_attribute("agent.framework", framework)
    if _CONVENTION in ("otel-genai", "both"):
        span.set_attribute("gen_ai.operation.name", "invoke_agent")
        if name:
            span.set_attribute("gen_ai.agent.name", name)


def open_or_enrich_span(
    inputs: Any,
    *,
    name: str | None = None,
    agent_name: str | None = None,
    agent_role: str | None = None,
    agent_framework: str | None = None,
):
    """Public context-manager entry point (also used by capture_run / _async).

    If a span is already recording (framework instrumentor / server span), enrich
    it in place and yield it — **no** new span. Otherwise open a fallback root span
    so input is never missed, named `name` (default `f"{_SERVICE_NAME}.run"`). Either
    way it stamps `input.*` and the multi-agent identity attributes, so the root
    span carries both the run's input and *which* agent produced it. Callers that
    wrap a shared AI boundary (e.g. a base executor) can use this directly instead
    of the decorators; pair it with `capture_output(...)` so the root also carries
    `output.*` (see § Root span always carries input and output)."""
    current = trace.get_current_span()
    if current.is_recording():
        enrich_current_span(inputs)
        # Enrich path: the current span belongs to the framework/transport
        # instrumentor, not observent. Only stamp identity when the caller passes
        # it *explicitly* — never auto-apply the generic literal defaults, which
        # would relabel a foreign span (e.g. an HTTP server span) or clobber
        # better identity the instrumentor already set (e.g. Google ADK's
        # gen_ai.agent.name). The fallback span below (which observent owns) always
        # gets identity.
        if agent_name or agent_role or agent_framework:
            _set_agent_identity(current, agent_name, agent_role, agent_framework)
        return nullcontext(current)
    # set_error() already records the exception and sets ERROR status, so disable
    # the context manager's own exception handling to avoid a duplicate event.
    span_name = name or f"{_SERVICE_NAME}.run"
    cm = _tracer.start_as_current_span(
        span_name, record_exception=False, set_status_on_exception=False
    )
    span = cm.__enter__()
    enrich_current_span(inputs)
    _set_agent_identity(span, agent_name, agent_role, agent_framework)
    return _Closing(cm, span)


class _Closing:
    """Adapts start_as_current_span's CM so capture_run can treat both paths alike."""
    def __init__(self, cm: Any, span: trace.Span) -> None:
        self._cm, self.span = cm, span

    def __enter__(self) -> trace.Span:
        return self.span

    def __exit__(self, *exc: Any) -> Any:
        return self._cm.__exit__(*exc)


def capture_run(fn: F) -> F:
    """Decorator: capture the wrapped callable's first argument as `input.*`, its
    return value as `output.*`, and set OK/ERROR status — on the existing root
    span when one is recording, else on a fallback `agent.run` span.

    Works for sync callables. Use `capture_run_async` for coroutines.
    """
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        inputs = args[0] if args else kwargs
        holder = open_or_enrich_span(inputs)
        with holder as span:
            try:
                result = fn(*args, **kwargs)
            except BaseException as exc:
                set_error(exc, span)
                raise
            capture_output(result, span)
            set_ok(span)
            return result
    return wrapper  # type: ignore[return-value]


def capture_run_async(fn: AF) -> AF:
    """Async counterpart of capture_run for coroutine entry points."""
    @functools.wraps(fn)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        inputs = args[0] if args else kwargs
        holder = open_or_enrich_span(inputs)
        with holder as span:
            try:
                result = await fn(*args, **kwargs)
            except BaseException as exc:
                set_error(exc, span)
                raise
            capture_output(result, span)
            set_ok(span)
            return result
    return wrapper  # type: ignore[return-value]
```

---

## Public entry point, span naming & agent identity

`open_or_enrich_span(inputs, *, name=None, agent_name=None, agent_role=None, agent_framework=None)` is the **public** context-manager entry point — the same one `capture_run` / `capture_run_async` use internally. Use it directly when you want to wrap a **single shared AI boundary** (e.g. a base executor's `execute()`), rather than decorating each entry point:

```python
from observent_capture import open_or_enrich_span, capture_output

with open_or_enrich_span(inputs, name=f"{service_name}: {summary}", agent_name="text2sql", agent_role="sql-writer") as span:
    result = run_the_agent(inputs)
    capture_output(result, span)
```

**Span naming (readability).** The fallback root span is named `f"{_SERVICE_NAME}.run"` (a generation-time literal, default `"agent"` → `agent.run`). Set `_SERVICE_NAME` per service so a trace list reads `text2sql.run` / `deepresearch.run` instead of a wall of identical `agent.run`. A caller may pass `name=` for a richer label (e.g. `f"{service_name}: {input_summary[:40]}"`). **Never** put a redacted field's raw value in a span *name* — names aren't redacted; only attributes are. This only controls observent's own root span; a framework's internal span names (CrewAI's `Crew_<uuid>.kickoff`, `Task Execution`, …) are upstream and not renameable — see `matrix.md § CrewAI`.

**Agent identity (mandatory attributes).** `_set_agent_identity` stamps the identity attributes `matrix.md § Mandatory Span Attributes` requires on an agent/chain root — `openinference.span.kind="AGENT"`, `agent.name`, `agent.role`, `agent.framework` (OI) and/or `gen_ai.operation.name="invoke_agent"`, `gen_ai.agent.name` (OTel-GenAI), keyed by `_CONVENTION`. **Scope matters:** identity is stamped **always on the fallback span** (which observent owns), but on the **enrich path only when `agent_name`/`agent_role`/`agent_framework` is passed explicitly** — the engine never auto-applies the generic literal defaults to a span it didn't create, since that would relabel a foreign span (an HTTP server span) or clobber better identity an instrumentor already set (e.g. Google ADK's `gen_ai.agent.name`). Defaults come from the `_AGENT_NAME` / `_AGENT_ROLE` / `_FRAMEWORK` generation-time literals (used for the fallback span); per-call `agent_name=` / `agent_role=` / `agent_framework=` override them and are the way to add identity to an existing framework root. `agent_framework=` is what lets a **single shared `observent_capture.py`** serve multiple frameworks in a multi-service monorepo — each service passes its own framework per-call instead of relying on one global `_FRAMEWORK` literal (see `spec_schema.md § Multi-service specs`). This is what lets a trace list identify *which* agent produced a span without opening the `service.name` resource attribute.

### Root span always carries input and output

The run's root span must carry **both** `input.*` and `output.*` (never input-only). `capture_run` / `capture_run_async` guarantee this — they call `enrich_current_span` (input) on entry and `capture_output` on success. When you use `open_or_enrich_span` directly, always pair it with `capture_output(result, span)` inside the block so the root isn't left output-less on the happy path.

## Per-framework wrap points

`capture_run` / `capture_run_async` (or a bare `open_or_enrich_span(...)` + `capture_output(...)` pair) goes at the **agent invocation**, so it enriches the framework's own root span:

| Framework | Where to wrap |
|---|---|
| **LangGraph** | the function that calls `graph.invoke(state)` / `graph.ainvoke(state)` / iterates `graph.stream(state)` |
| **CrewAI** | the function that calls `crew.kickoff(inputs=...)` |
| **LlamaIndex** | the function that calls `query_engine.query(...)` / `chat_engine.chat(...)` |
| **smolagents** | the function that calls `agent.run(task)` |
| **Anthropic / OpenAI Agents SDK** | the request handler / `Runner.run(...)` call site |
| **Microsoft Agent Framework** | the function that invokes the workflow/agent |
| **Custom** | wherever the manual root span is opened — call `enrich_current_span` right after |

Because capture enriches the *current* span, the framework's instrumentor must run first (it opens the root). If the agent is invoked with **no** instrumentor active (bare script), the fallback `agent.run` span guarantees input is still captured.

---

## Baggage promotion (cross-span correlation)

Span attributes live on one span; child spans (LLM / tool / agent steps) do **not** inherit them. To filter child spans by a request field (`tenant_id`, `user_id`, …), the engine promotes a configurable whitelist of leaf keys from the input into **OTel baggage**, and a `BaggageSpanProcessor` stamps them onto every span as it starts.

```python
from opentelemetry.processor.baggage import BaggageSpanProcessor, ALLOW_ALL_BAGGAGE_KEYS

provider.add_span_processor(BaggageSpanProcessor(ALLOW_ALL_BAGGAGE_KEYS))
```

Install: `pip install opentelemetry-processor-baggage`. Place it on the same `TracerProvider` that carries the OTLP exporters; Elastic APM picks up the same spans via its OTel bridge. Matching is exact, case-sensitive on the leaf segment; redacted values are never promoted. Keep the whitelist small for per-span cardinality / ingest cost — full-payload duplication onto every child span is intentionally avoided (N spans × full payload, brittle under sampling).

The whitelist also carries the **correlation keys** used to group runs that originate in an opaque vendor runtime (`conversation_id`, `run_id`, `mcp_session_id` alongside `session_id`). When your tools serve a vendor runtime (Claude Code, Cursor) over MCP, read the MCP session id in the server handler and put it in the input (or set it directly via `baggage.set_baggage("mcp_session_id", ...)`); the processor then stamps it onto every child span so the run's calls group by one key. This is the in-process counterpart to the proxy-side capture in `references/gateway.md` — same key, different seam.

---

## Optional HTTP body adapter

`capture_run` already captures the agent's logical input/output for **any** transport. The HTTP adapter is needed **only when you additionally want the raw HTTP request/response bodies and headers** (e.g. a header or envelope field the agent never receives as an argument). Generate it **only if** `spec.choice.http_body_capture: true`.

It is a thin Starlette/ASGI middleware that **enriches the existing server span** with `http.request.*` / `http.response.*` attributes via the same `_flatten` engine. Key differences from the engine:

- **No new span** — it writes onto the server span the FastAPI instrumentor already opened.
- **No response re-buffering** — it reads the request body (re-injecting it so the route still sees it) and, for the response, captures headers/status without collapsing a `StreamingResponse`. Streaming endpoints keep streaming.
- Transport spans (`http receive` / `http send`) from the ASGI instrumentor are governed by `spec.choice.http_transport_spans` (see § HTTP transport spans below) — by default observent doesn't emit them at all. **Suppressing them is framework-specific** (gap: the advice used to assume FastAPI): `FastAPIInstrumentor.instrument_app()` accepts `exclude_spans=["receive", "send"]`, but `StarletteInstrumentor.instrument_app()` has **no** such parameter (its signature only exposes the request/response hooks + provider args). For Starlette — and for de-noising **any** streaming ASGI app — add the underlying ASGI middleware directly, which *does* support it:
  ```python
  from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
  app.add_middleware(OpenTelemetryMiddleware, exclude_spans=["receive", "send"])
  ```
  This matters in practice: a plain `StarletteInstrumentor.instrument_app(app)` emits a `http send` span **per SSE chunk** (12+ transport spans for one streamed JSON-RPC response), on top of the one real server span.

```python
# observent_http.py
"""Optional: enrich the existing HTTP server span with raw request/response
headers + bodies. Use ONLY when the agent's logical input (captured by
observent_capture.capture_run) is not enough and you need the wire payload.

Adds NO span and does NOT buffer streaming responses.
"""
from __future__ import annotations

import json
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

from observent_capture import _coerce, _flatten, _is_sensitive, _REDACTED


class ObserventHTTPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any) -> Response:
        from opentelemetry import trace

        span = trace.get_current_span()  # the FastAPI server span — enrich it
        if span.is_recording():
            for k, v in request.headers.items():
                key = f"http.request.headers.{k.lower().replace('-', '_')}"
                span.set_attribute(key, _REDACTED if _is_sensitive(k) else v)
            for k, v in _flatten("http.request.query", dict(request.query_params)):
                span.set_attribute(k, v)

        body = await request.body()  # cached on request; route still reads it
        if span.is_recording() and body:
            try:
                parsed = json.loads(body.decode("utf-8", errors="replace"))
                if isinstance(parsed, (dict, list)):
                    for k, v in _flatten("http.request.body", parsed):
                        span.set_attribute(k, v)
                else:
                    span.set_attribute("http.request.body", _coerce(parsed))
            except (UnicodeDecodeError, json.JSONDecodeError):
                span.set_attribute("http.request.body", body.decode("utf-8", errors="replace"))

        response = await call_next(request)

        # Streaming responses are passed through untouched — never collapse them.
        if span.is_recording() and not isinstance(response, StreamingResponse):
            span.set_attribute("http.response.status_code", response.status_code)
        return response
```

Registration — instrument **before** adding the middleware so the server span exists first:

```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from observent_http import ObserventHTTPMiddleware

FastAPIInstrumentor.instrument_app(app)   # opens the server span (+ keeps transport spans)
app.add_middleware(ObserventHTTPMiddleware)
```

---

## HTTP transport spans

For a web-served agent, the ASGI/framework instrumentor bundles four things onto every request: (1) **incoming `traceparent` extraction** — critical for cross-service/cross-agent trace linkage; (2) a **server root span**; (3) **`http receive`/`http send` transport child spans** — per-SSE-chunk noise for streaming apps; (4) HTTP method/route/status attributes. For a multi-agent app the *meaningful* spans already come from the framework instrumentor (CrewAI/LangGraph/ADK) and this capture engine's root — so only (1) is essential.

`spec.choice.http_transport_spans` picks how much to emit:

| Mode | What's generated | When |
|---|---|---|
| `full` | Framework/ASGI instrumentor open, transport spans kept. | Legacy / user opts in. |
| `root-only` | Framework instrumentor's server span kept; `exclude_spans=["receive","send"]` suppresses transport children (retains HTTP method/route/status — feeds APM dashboards). | **Default when an APM backend** (SigNoz / Elastic APM / Jaeger) is in the set — their transaction/service-map/RED-metric views are built on the HTTP server span. |
| `none` | **No** framework instrumentor at all. A context-only middleware extracts `traceparent` (no span); the capture fallback root becomes the single clean span. | **Default when the backend set is LLM-native-only** ({phoenix, langfuse, opik, langsmith}), which ignore HTTP server spans. |

**`none` — context-only middleware (no span on success, one span on early error).** Drop the ASGI/framework instrumentor entirely and add this. It preserves cross-service linkage (so child-agent spans still nest under the caller's trace) with zero spans on the happy path, but opens a single `http.error` span if the request fails *before* the agent boundary opened its own root (validation / auth / malformed body — otherwise invisible under `none`):

```python
from opentelemetry import context as otel_context
from opentelemetry.propagate import extract
from opentelemetry.trace import Status, StatusCode
from observent_capture import _tracer  # reuse the engine's tracer

class TraceContextMiddleware:
    """Extract W3C trace context (traceparent/tracestate) from the incoming
    request so this service's spans join the caller's trace — WITHOUT opening a
    server span. Opens a lone `http.error` span only if the app raises before the
    agent boundary's own root span exists."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        carrier = {k.decode("latin-1"): v.decode("latin-1") for k, v in scope.get("headers", [])}
        token = otel_context.attach(extract(carrier))
        try:
            await self.app(scope, receive, send)          # success: no span opened
        except Exception as exc:
            with _tracer.start_as_current_span("http.error") as span:
                span.record_exception(exc)
                span.set_attribute("error.type", type(exc).__qualname__)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise
        finally:
            otel_context.detach(token)
```

Register it *instead of* any `*Instrumentor` (uniformly, for FastAPI / Starlette / Flask-ASGI / …):

```python
app.add_middleware(TraceContextMiddleware)   # no FastAPIInstrumentor / StarletteInstrumentor
```

> **Linkage guardrail.** Never emit `none` *without* this middleware — dropping the instrumentor and adding nothing silently breaks distributed tracing (each service starts a disconnected trace). `none` == "no server span, but still extract context."

The outbound counterpart (propagate `traceparent` on outgoing calls without a per-request httpx span) lives in `matrix.md § Context Propagation § Cross-service / cross-agent network calls` (inject-only transport).

## Truncation and attribute limits

**No engine-level truncation** — full input/output is flattened into per-key attributes. Two OTel SDK caps still apply:

- **`OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT`** (default `128`) — caps attributes per span; a payload with > 128 leaf fields has its tail dropped. Raise it (e.g. `1024`) for large payloads.
- **`OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT`** — caps each value's length (unset/unlimited by default).

---

## Convention compatibility

`input.*` / `output.*` are the OI-native single-value keys (paired with `input.mime_type` / `output.mime_type`); `gen_ai.prompt` / `gen_ai.completion` mirror the same `_serialize()`d string for OTel-GenAI backends (that convention has no mime-type companion attribute, so none is set). The flattened per-leaf attributes (`input.user_id`, `http.request.body.*`) are plain OTel attributes that work for all five backends without convention switching. `_CONVENTION` (generation-time literal, derived from the backend set — see `matrix.md § Convention resolution`) decides which single-value mirror(s) are emitted.

---

*Last verified: 2026-07-03 with Python 3.12, OpenTelemetry API/SDK 1.41, Starlette 0.40.*
