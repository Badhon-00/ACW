# observent Examples

Runnable end-to-end examples covering 9 frameworks × 7 backends, with backends rotated across frameworks plus one extra example per non-Phoenix backend (Elastic APM, LangSmith, Opik, Jaeger). Plus a multi-backend fan-out, a verification checklist, and troubleshooting.

> **Convention notes.** Phoenix-targeted examples (1, 5, 8, 11) emit OpenInference keys — Phoenix's UI is OI-native. Langfuse / SigNoz / Elastic APM / LangSmith / Opik / Jaeger examples (2, 3, 4, 6, 7, 9, 10, 12, 13) inherit OI keys from the relevant `openinference-instrumentation-*` package and exporters carry them on the OTLP wire; the backends ingest the spans, but for richer convention-aware UI on those backends you can supplement with OTel-GenAI keys (`gen_ai.*` — see `otel_genai.md`) or use the Custom path (the helper bakes in the convention literal at generation time — see Example 8). The Multi-Backend Fan-Out example at the bottom emits both conventions because the resolved set requires it.

---

## Maintainer's sources

Each example carries a per-example `**Sources:**` bullet pointing to the framework + backend docs the snippet was verified against. Bump the `*Last verified: …*` footer when you re-run an example end-to-end.

**Specs & SDK (apply to every example):**
- W3C Trace Context Level 1 — https://www.w3.org/TR/trace-context/
- W3C Baggage — https://www.w3.org/TR/baggage/
- OTel Python SDK — https://opentelemetry.io/docs/languages/python/
- OTLP/HTTP exporter — https://github.com/open-telemetry/opentelemetry-python/tree/main/exporter/opentelemetry-exporter-otlp-proto-http

**Cross-service HTTP propagation (W3C `traceparent` + `tracestate` + `baggage` injection on outbound requests):**
- `opentelemetry-instrumentation-httpx` — https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-httpx (OpenAI/Anthropic SDKs use `httpx`)
- `opentelemetry-instrumentation-requests` — https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-requests

Enable one or both alongside the framework instrumentor when your app fans out to sibling services — the SDK's default composite propagator (`TraceContextTextMapPropagator` + `W3CBaggagePropagator`) handles the wire format; the HTTP instrumentor handles the actual header injection. The examples below add `HTTPXClientInstrumentor().instrument()` where the LLM client is `httpx`-based (OpenAI, Anthropic, LangChain integrations) so the trace tree stays continuous across downstream services.

Last reviewed: 2026-05-17.

---

## 1. LangGraph + Arize Phoenix (local, zero account)

```python
# main.py
import os
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

# --- Observability: Phoenix local ---
tracer_provider = register(
    project_name=os.getenv("PHOENIX_PROJECT_NAME", "langgraph-demo"),
    endpoint=os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces"),
)
LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
HTTPXClientInstrumentor().instrument(tracer_provider=tracer_provider)  # W3C traceparent on outbound HTTP

# --- Agent ---
llm = ChatAnthropic(model="claude-sonnet-4-6")

def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"It's 72°F and sunny in {city}."

agent = create_react_agent(llm, tools=[get_weather])

if __name__ == "__main__":
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "What's the weather in Tokyo?"}]},
        config={"configurable": {"session_id": "demo-session-001"}},
    )
    print(result["messages"][-1].content)
    # Open http://localhost:6006 to see the trace
```

```bash
# 1. Start Phoenix UI in another terminal:
python -m phoenix.server.main serve   # or `pip install arize-phoenix && phoenix serve`

# 2. Install dependencies:
pip install 'arize-phoenix>=5.0' 'openinference-instrumentation-langchain>=0.1' \
            'opentelemetry-instrumentation-httpx>=0.48' \
            'langgraph>=0.2' 'langchain-anthropic>=0.2'

# 3. Set ANTHROPIC_API_KEY and run:
export ANTHROPIC_API_KEY=sk-ant-...
python main.py
```

**Sources:** Phoenix `register()` / OTLP — https://docs.arize.com/phoenix/tracing/how-to-tracing/setup-tracing/setup-tracing-python · LangGraph — https://langchain-ai.github.io/langgraph/ · `openinference-instrumentation-langchain` — https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-langchain · `opentelemetry-instrumentation-httpx` — https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-httpx

*Last verified: 2026-05-08 with Python 3.12.*

---

## 2. CrewAI + Langfuse (callback, cost tracking)

```python
# crew_main.py
import os
from langfuse.langchain import CallbackHandler
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# --- Observability: Langfuse via LangChain callback ---
langfuse_handler = CallbackHandler()  # reads LANGFUSE_PUBLIC_KEY/SECRET_KEY/HOST from env

llm = ChatOpenAI(model="gpt-4o", callbacks=[langfuse_handler])

researcher = Agent(
    role="Senior Research Analyst",
    goal="Find accurate, source-backed information",
    backstory="You are a meticulous researcher.",
    llm=llm, verbose=True,
)
writer = Agent(
    role="Technical Writer",
    goal="Turn research into clear summaries",
    backstory="You write for a developer audience.",
    llm=llm, verbose=True,
)

research = Task(
    description="Research the latest developments in {topic}",
    expected_output="A structured summary with sources",
    agent=researcher,
)
write = Task(
    description="Write a 3-paragraph summary based on the research",
    expected_output="A polished 3-paragraph summary",
    agent=writer,
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research, write],
    process=Process.sequential,
    verbose=True,
)

if __name__ == "__main__":
    result = crew.kickoff(inputs={"topic": "multi-agent observability"})
    print(result)
    # langfuse_handler flushes automatically; or:
    from langfuse import get_client
    get_client().flush()
```

```bash
pip install 'crewai>=0.80' 'langfuse>=3.0' 'langchain-openai>=0.2'
export LANGFUSE_PUBLIC_KEY=pk-lf-... LANGFUSE_SECRET_KEY=sk-lf-...
export LANGFUSE_HOST=https://cloud.langfuse.com  # or http://localhost:3000 for self-host
export OPENAI_API_KEY=sk-...
python crew_main.py
# Visit https://cloud.langfuse.com to see Crew → Agent → Task → LLM hierarchy
```

**Sources:** Langfuse LangChain integration — https://langfuse.com/docs/integrations/langchain/tracing · Langfuse `CallbackHandler` — https://python.reference.langfuse.com/langfuse/langchain · CrewAI — https://docs.crewai.com/ · Langfuse OpenAI/CrewAI cost tracking — https://langfuse.com/docs/model-usage-and-cost

*Last verified: 2026-05-08 with Python 3.12.*

---

## 3. Microsoft Agent Framework + SigNoz (OTLP, session_id propagation)

```python
# maf_signoz.py
import asyncio
import os
from opentelemetry import baggage, context, trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from openinference.instrumentation.openai import OpenAIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient

# --- Observability: SigNoz via OTLP ---
# Register the global TracerProvider BEFORE constructing any Agent — MAF's
# native OTel emission attaches to whatever provider is set globally.
headers = {}
if key := os.getenv("SIGNOZ_INGESTION_KEY"):
    headers["signoz-access-token"] = key

provider = TracerProvider(
    resource=Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", "maf-demo")}),
)
provider.add_span_processor(
    BatchSpanProcessor(
        OTLPSpanExporter(
            endpoint=os.getenv("SIGNOZ_ENDPOINT", "http://localhost:4318/v1/traces"),
            headers=headers,
        )
    )
)
trace.set_tracer_provider(provider)
OpenAIInstrumentor().instrument(tracer_provider=provider)
HTTPXClientInstrumentor().instrument(tracer_provider=provider)  # W3C traceparent on outbound HTTP

# --- Agents ---
async def main(session_id: str):
    # Set session.id baggage so it propagates across all child spans
    ctx = baggage.set_baggage("session.id", session_id)
    ctx = baggage.set_baggage("user.id", "user-42", context=ctx)
    token = context.attach(ctx)
    try:
        client = OpenAIChatClient(model_id="gpt-4o")
        assistant = Agent(
            client=client,
            name="assistant",
            instructions="You are a concise expert.",
        )
        critic = Agent(
            client=client,
            name="critic",
            instructions="Critique the assistant's answer in 1 sentence.",
        )
        # Simple two-step workflow: assistant answers, critic reviews.
        answer = await assistant.run("Explain how LLM caching works.")
        review = await critic.run(f"Assistant answered:\n{answer}")
        print(review)
    finally:
        context.detach(token)
        provider.shutdown()

if __name__ == "__main__":
    asyncio.run(main(session_id="demo-session-002"))
```

```bash
# Start SigNoz self-host first (Foundry CLI — SigNoz deprecated its docker-compose manifests):
curl -fsSL https://signoz.io/foundry.sh | bash      # installs foundryctl (checksum-verified)
foundryctl forge -f casting.yaml                     # generates pours/deployment/compose.yaml
docker compose -f pours/deployment/compose.yaml up -d --wait
# see references/self_host.md § SigNoz for casting.yaml + the OTLP-readiness caveat

pip install 'agent-framework>=1.4' \
            'opentelemetry-sdk>=1.25' 'opentelemetry-exporter-otlp-proto-http>=1.25' \
            'opentelemetry-instrumentation-httpx>=0.48' \
            'openinference-instrumentation-openai>=0.1'
export OPENAI_API_KEY=sk-... SIGNOZ_ENDPOINT=http://localhost:4318/v1/traces
python maf_signoz.py
# UI: http://localhost:8080
```

**Sources:** Microsoft Agent Framework — https://github.com/microsoft/agent-framework · MAF observability — https://learn.microsoft.com/en-us/agent-framework/python/observability · SigNoz OTLP ingestion — https://signoz.io/docs/instrumentation/opentelemetry-python/ · `openinference-instrumentation-openai` — https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-openai

*Last verified: 2026-05-17 with Python 3.12.*

---

## 4. Anthropic Agents SDK + Langfuse (decorator, token usage)

```python
# anthropic_langfuse.py
import os
import anthropic
from langfuse import observe, get_client

langfuse = get_client()
client = anthropic.Anthropic()

TOOLS = [{
    "name": "get_weather",
    "description": "Returns current weather for a city",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    },
}]

def get_weather(city: str) -> str:
    return f"72°F sunny in {city}"

@observe(name="tool-call")
def execute_tool(name: str, args: dict) -> str:
    if name == "get_weather":
        return get_weather(args["city"])
    return "unknown tool"

@observe(name="agent-run", as_type="generation")
def run_agent(prompt: str, session_id: str = "default") -> str:
    langfuse.update_current_trace(
        session_id=session_id,
        user_id="user-42",
        tags=["weather", "anthropic-agents-sdk"],
    )
    messages = [{"role": "user", "content": prompt}]

    while True:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )
        # Surface usage so Langfuse computes cost:
        langfuse.update_current_observation(
            model="claude-sonnet-4-6",
            usage_details={
                "input": resp.usage.input_tokens,
                "output": resp.usage.output_tokens,
                "cache_read_input_tokens": getattr(resp.usage, "cache_read_input_tokens", 0),
                "cache_creation_input_tokens": getattr(resp.usage, "cache_creation_input_tokens", 0),
            },
        )

        if resp.stop_reason == "end_turn":
            return "".join(b.text for b in resp.content if b.type == "text")

        if resp.stop_reason == "tool_use":
            tool_use = next(b for b in resp.content if b.type == "tool_use")
            tool_result = execute_tool(tool_use.name, tool_use.input)
            messages.append({"role": "assistant", "content": resp.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": tool_result,
                }],
            })

if __name__ == "__main__":
    print(run_agent("What's the weather in Tokyo?", session_id="demo-003"))
    langfuse.flush()
```

```bash
pip install 'anthropic>=0.40' 'langfuse>=3.0'
export ANTHROPIC_API_KEY=sk-ant-...
export LANGFUSE_PUBLIC_KEY=pk-lf-... LANGFUSE_SECRET_KEY=sk-lf-...
python anthropic_langfuse.py
```

**Sources:** Langfuse `@observe` decorator — https://langfuse.com/docs/sdk/python/decorators · Langfuse `update_current_observation` (usage / cost) — https://langfuse.com/docs/model-usage-and-cost · Anthropic Messages API — https://docs.anthropic.com/en/api/messages · Anthropic prompt caching usage fields — https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching · Note: Langfuse `@observe` uses its own OTel-bridged tracer; cross-service HTTP propagation is automatic when the SDK is initialized — no separate `HTTPXClientInstrumentor` needed for this path.

*Last verified: 2026-05-08 with Python 3.12.*

---

## 5. OpenAI Agents SDK + Arize Phoenix (native trace processor)

This example uses the **OpenAI Agents SDK's native tracing** wired to Phoenix — it captures handoffs, guardrails, and agent runs as first-class spans. Do **not** use `openinference-instrumentation-openai` here; that only captures raw OpenAI HTTP calls and loses agent structure.

```python
# openai_agents_phoenix.py
import os
from phoenix.otel import register
from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from agents import Agent, Runner, function_tool

# --- Observability: Phoenix native trace processor for Agents SDK ---
tracer_provider = register(
    project_name=os.getenv("PHOENIX_PROJECT_NAME", "openai-agents-demo"),
    endpoint=os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces"),
)
OpenAIAgentsInstrumentor().instrument(tracer_provider=tracer_provider)
HTTPXClientInstrumentor().instrument(tracer_provider=tracer_provider)  # W3C traceparent on outbound HTTP

# --- Agents with handoff ---
@function_tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"72°F sunny in {city}"

weather_agent = Agent(
    name="WeatherAgent",
    instructions="You answer weather questions concisely.",
    tools=[get_weather],
)
triage = Agent(
    name="Triage",
    instructions="Hand off weather questions to WeatherAgent.",
    handoffs=[weather_agent],
)

if __name__ == "__main__":
    result = Runner.run_sync(triage, "What's the weather in Tokyo?")
    print(result.final_output)
    # Open http://localhost:6006 — you should see:
    #   Runner.run -> Triage -> Handoff -> WeatherAgent -> tool: get_weather -> LLM
```

```bash
phoenix serve &  # background Phoenix UI on :6006
pip install 'arize-phoenix>=5.0' 'openinference-instrumentation-openai-agents>=0.1' \
            'opentelemetry-instrumentation-httpx>=0.48' \
            'openai-agents>=0.0.4'
export OPENAI_API_KEY=sk-...
python openai_agents_phoenix.py
```

**Sources:** OpenAI Agents SDK tracing — https://openai.github.io/openai-agents-python/tracing/ · OpenAI Agents SDK `set_trace_processors` — https://openai.github.io/openai-agents-python/ref/tracing/ · `openinference-instrumentation-openai-agents` — https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-openai-agents · Phoenix `register()` — https://docs.arize.com/phoenix/tracing/how-to-tracing/setup-tracing/setup-tracing-python

*Last verified: 2026-05-08 with Python 3.12.*

---

## 6. smolagents + Langfuse (OpenInference instrumentor)

```python
# smolagents_langfuse.py
import base64
import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from smolagents import CodeAgent, DuckDuckGoSearchTool, LiteLLMModel

# --- Observability: Langfuse via OTLP ---
host = os.environ["LANGFUSE_HOST"].rstrip("/")
auth = base64.b64encode(
    f"{os.environ['LANGFUSE_PUBLIC_KEY']}:{os.environ['LANGFUSE_SECRET_KEY']}".encode()
).decode()

provider = TracerProvider(resource=Resource.create({"service.name": "smolagents-demo"}))
provider.add_span_processor(
    BatchSpanProcessor(
        OTLPSpanExporter(
            endpoint=f"{host}/api/public/otel/v1/traces",
            headers={"Authorization": f"Basic {auth}"},
        )
    )
)
trace.set_tracer_provider(provider)
SmolagentsInstrumentor().instrument(tracer_provider=provider)
HTTPXClientInstrumentor().instrument(tracer_provider=provider)  # W3C traceparent on outbound HTTP

# --- Agent ---
model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-6")
agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=model)

if __name__ == "__main__":
    answer = agent.run("Who won the latest Formula 1 Grand Prix?")
    print(answer)
    provider.shutdown()
```

```bash
pip install 'smolagents>=1.0' 'openinference-instrumentation-smolagents>=0.1' \
            'opentelemetry-sdk>=1.25' 'opentelemetry-exporter-otlp-proto-http>=1.25' \
            'opentelemetry-instrumentation-httpx>=0.48'
export ANTHROPIC_API_KEY=sk-ant-...
export LANGFUSE_PUBLIC_KEY=pk-lf-... LANGFUSE_SECRET_KEY=sk-lf-... LANGFUSE_HOST=https://cloud.langfuse.com
python smolagents_langfuse.py
```

**Sources:** smolagents — https://huggingface.co/docs/smolagents · `openinference-instrumentation-smolagents` — https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-smolagents · Langfuse OTLP endpoint (`/api/public/otel/v1/traces`) — https://langfuse.com/docs/opentelemetry/get-started

*Last verified: 2026-05-08 with Python 3.12.*

---

## 7. LlamaIndex + SigNoz (RetrieverQueryEngine with retrieval spans)

```python
# llama_signoz.py
import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.anthropic import Anthropic

# --- Observability: SigNoz via OTLP ---
headers = {}
if key := os.getenv("SIGNOZ_INGESTION_KEY"):
    headers["signoz-access-token"] = key

provider = TracerProvider(resource=Resource.create({"service.name": "llamaindex-demo"}))
provider.add_span_processor(
    BatchSpanProcessor(
        OTLPSpanExporter(
            endpoint=os.getenv("SIGNOZ_ENDPOINT", "http://localhost:4318/v1/traces"),
            headers=headers,
        )
    )
)
trace.set_tracer_provider(provider)
LlamaIndexInstrumentor().instrument(tracer_provider=provider)
HTTPXClientInstrumentor().instrument(tracer_provider=provider)  # W3C traceparent on outbound HTTP

# --- RAG pipeline ---
Settings.llm = Anthropic(model="claude-sonnet-4-6")
documents = SimpleDirectoryReader("./docs").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

if __name__ == "__main__":
    response = query_engine.query("Summarize the main themes.")
    print(response)
    # In SigNoz: see RETRIEVER spans with retrieval.documents attribute
    provider.shutdown()
```

```bash
pip install 'llama-index>=0.11' 'llama-index-llms-anthropic' \
            'openinference-instrumentation-llama-index>=2.0' \
            'opentelemetry-sdk>=1.25' 'opentelemetry-exporter-otlp-proto-http>=1.25' \
            'opentelemetry-instrumentation-httpx>=0.48'
mkdir -p docs && echo "Sample document content." > docs/sample.txt
export ANTHROPIC_API_KEY=sk-ant-... SIGNOZ_ENDPOINT=http://localhost:4318/v1/traces
python llama_signoz.py
```

**Sources:** LlamaIndex — https://docs.llamaindex.ai/ · `openinference-instrumentation-llama-index` — https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-llama-index · SigNoz OTLP ingestion — https://signoz.io/docs/instrumentation/opentelemetry-python/

*Last verified: 2026-05-08 with Python 3.12.*

---

## 8. Custom multi-agent loop + Arize Phoenix (manual span hierarchy)

When you don't use a framework, the skill writes an `observent_otel.py` helper module to your project. The helper is **convention-aware**: the convention resolved in Step 3 (`oi`, `otel-genai`, or `both`) is **baked in as a literal at generation time** — no env var, no runtime override. The example below shows what gets written for Phoenix-only (`oi`); for Langfuse/SigNoz the literal is `"otel-genai"`, and for Phoenix + (Langfuse or SigNoz) fan-out it's `"both"`.

```python
# observent_otel.py — generated helper (kept in your repo)
"""observent-generated OpenTelemetry helpers for multi-agent apps."""
from __future__ import annotations
import json
from contextlib import contextmanager
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Resolved by the skill in Step 3 from your chosen backend set and written
# here as a literal. To change it, re-run /observent with a different backend(s).
_CONVENTION = "oi"  # "oi" | "otel-genai" | "both"


def init_tracing(*, service_name: str, exporter) -> trace.TracerProvider:
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return provider


def _set(span, key: str, value: Any) -> None:
    if value is None:
        return
    span.set_attribute(key, value if isinstance(value, (str, int, float, bool)) else json.dumps(value))


def _emit_oi() -> bool:
    return _CONVENTION in ("oi", "both")


def _emit_otel() -> bool:
    return _CONVENTION in ("otel-genai", "both")


@contextmanager
def with_agent_span(name: str, role: str = "", framework: str = "custom"):
    tracer = trace.get_tracer("observent")
    with tracer.start_as_current_span(f"agent.{name}") as span:
        if _emit_oi():
            _set(span, "openinference.span.kind", "AGENT")
            _set(span, "agent.name", name)
            _set(span, "agent.role", role)
            _set(span, "agent.framework", framework)
        if _emit_otel():
            _set(span, "gen_ai.operation.name", "invoke_agent")
            _set(span, "gen_ai.agent.name", name)
            _set(span, "gen_ai.agent.description", role)
        yield span


def set_llm_attrs(span, *, model: str, provider: str, input_messages, output_messages,
                  prompt_tokens: int, completion_tokens: int,
                  cache_read_tokens: int = 0, cache_write_tokens: int = 0,
                  invocation_parameters: dict | None = None,
                  finish_reasons: list[str] | None = None) -> None:
    if _emit_oi():
        _set(span, "openinference.span.kind", "LLM")
        _set(span, "llm.model_name", model)
        _set(span, "llm.provider", provider)
        _set(span, "llm.input_messages", input_messages)
        _set(span, "llm.output_messages", output_messages)
        _set(span, "input.value", input_messages)
        _set(span, "input.mime_type", "application/json")
        _set(span, "output.value", output_messages)
        _set(span, "output.mime_type", "application/json")
        _set(span, "llm.token_count.prompt", prompt_tokens)
        _set(span, "llm.token_count.completion", completion_tokens)
        _set(span, "llm.token_count.total", prompt_tokens + completion_tokens)
        if cache_read_tokens:
            _set(span, "llm.token_count.prompt_details.cache_read", cache_read_tokens)
        if cache_write_tokens:
            _set(span, "llm.token_count.prompt_details.cache_write", cache_write_tokens)
        if invocation_parameters:
            _set(span, "llm.invocation_parameters", invocation_parameters)
        if finish_reasons:
            _set(span, "llm.finish_reasons", finish_reasons)
    if _emit_otel():
        _set(span, "gen_ai.operation.name", "chat")
        _set(span, "gen_ai.provider.name", provider)
        _set(span, "gen_ai.request.model", model)
        _set(span, "gen_ai.response.model", model)
        _set(span, "gen_ai.usage.input_tokens", prompt_tokens)
        _set(span, "gen_ai.usage.output_tokens", completion_tokens)
        if cache_read_tokens:
            _set(span, "gen_ai.usage.cache_read.input_tokens", cache_read_tokens)
        if cache_write_tokens:
            _set(span, "gen_ai.usage.cache_creation.input_tokens", cache_write_tokens)
        if invocation_parameters:
            for k, v in invocation_parameters.items():
                _set(span, f"gen_ai.request.{k}", v)
        if finish_reasons:
            _set(span, "gen_ai.response.finish_reasons", finish_reasons)


def set_tool_attrs(span, *, name: str, description: str = "", parameters: dict | None = None,
                   input_value: Any = None, output_value: Any = None) -> None:
    if _emit_oi():
        _set(span, "openinference.span.kind", "TOOL")
        _set(span, "tool.name", name)
        _set(span, "tool.description", description)
        if parameters is not None:
            _set(span, "tool.parameters", parameters)
        if input_value is not None:
            _set(span, "input.value", input_value)
        if output_value is not None:
            _set(span, "output.value", output_value)
    if _emit_otel():
        _set(span, "gen_ai.operation.name", "execute_tool")
        if parameters is not None:
            _set(span, "gen_ai.tool.definitions", {"name": name, "description": description, "parameters": parameters})
```

```python
# main.py — your custom multi-agent app
import os
import anthropic
from opentelemetry import trace
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from phoenix.otel import register
from observent_otel import with_agent_span, set_llm_attrs, set_tool_attrs

tracer_provider = register(
    project_name=os.getenv("PHOENIX_PROJECT_NAME", "custom-agent-demo"),
    endpoint=os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces"),
)
HTTPXClientInstrumentor().instrument(tracer_provider=tracer_provider)  # W3C traceparent on outbound HTTP
tracer = trace.get_tracer("custom-agent")
client = anthropic.Anthropic()


def planner(question: str) -> str:
    with with_agent_span("planner", role="Decompose user questions into steps") as span:
        msgs = [{"role": "user", "content": f"Plan steps to answer: {question}"}]
        with tracer.start_as_current_span("llm.call") as llm_span:
            resp = client.messages.create(model="claude-sonnet-4-6", max_tokens=512, messages=msgs)
            output = resp.content[0].text
            set_llm_attrs(
                llm_span, model="claude-sonnet-4-6", provider="anthropic",
                input_messages=msgs, output_messages=[{"role": "assistant", "content": output}],
                prompt_tokens=resp.usage.input_tokens, completion_tokens=resp.usage.output_tokens,
            )
        span.set_attribute("output.value", output)
        return output


def executor(plan: str, question: str) -> str:
    with with_agent_span("executor", role="Execute the plan") as span:
        with tracer.start_as_current_span("tool.call") as tool_span:
            set_tool_attrs(tool_span, name="lookup", description="Web lookup",
                           parameters={"q": "string"}, input_value={"q": question},
                           output_value={"result": "stub"})
        msgs = [{"role": "user", "content": f"Plan:\n{plan}\n\nAnswer: {question}"}]
        with tracer.start_as_current_span("llm.call") as llm_span:
            resp = client.messages.create(model="claude-sonnet-4-6", max_tokens=512, messages=msgs)
            output = resp.content[0].text
            set_llm_attrs(
                llm_span, model="claude-sonnet-4-6", provider="anthropic",
                input_messages=msgs, output_messages=[{"role": "assistant", "content": output}],
                prompt_tokens=resp.usage.input_tokens, completion_tokens=resp.usage.output_tokens,
            )
        span.set_attribute("output.value", output)
        return output


if __name__ == "__main__":
    q = "What is observability for multi-agent systems?"
    plan = planner(q)
    print(executor(plan, q))
    tracer_provider.shutdown()
```

**Sources:** OpenInference span kinds (`AGENT`, `LLM`, `TOOL`) — https://github.com/Arize-ai/openinference/blob/main/spec/semantic_conventions.md · OTel-GenAI operations (`invoke_agent`, `chat`, `execute_tool`) — https://opentelemetry.io/docs/specs/semconv/gen-ai/ · Anthropic Messages API (usage fields) — https://docs.anthropic.com/en/api/messages · See `openinference.md` and `otel_genai.md` for the canonical key tables this helper writes.

*Last verified: 2026-05-08 with Python 3.12.*

---

## 9. Microsoft Agent Framework + Elastic APM (native agent — transactions + LLM spans)

The Elastic APM Python agent gets you transaction tracing and infrastructure / runtime metrics out of the box, and its built-in OTel bridge picks up spans from MAF's native OTel emission and from `OpenAIInstrumentor` so the LLM calls show up in the same Kibana service map. This example uses the **native agent** (the slash-command default); see `matrix.md` § Elastic APM for the OTLP-only variant.

```python
# maf_elastic.py
import asyncio
import os
import elasticapm
from openinference.instrumentation.openai import OpenAIInstrumentor

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient

# --- Observability: native Elastic APM agent ---
# Reads ELASTIC_APM_SERVER_URL / SECRET_TOKEN / API_KEY from the environment.
elasticapm.Client(
    service_name=os.getenv("ELASTIC_APM_SERVICE_NAME", "maf-demo"),
    environment=os.getenv("ELASTIC_APM_ENVIRONMENT", "dev"),
)
elasticapm.instrument()  # auto-instruments asyncio / urllib3 / requests / httpx / ...

# MAF emits OTel spans natively and OI instrumentor adds raw model spans;
# the Elastic APM agent's OTel bridge ingests both alongside the
# auto-instrumented transaction spans.
OpenAIInstrumentor().instrument()


async def main() -> None:
    client = OpenAIChatClient(model_id="gpt-4o")
    assistant = Agent(
        client=client,
        name="assistant",
        instructions="You are a concise expert.",
    )
    critic = Agent(
        client=client,
        name="critic",
        instructions="Critique the assistant's answer in 1 sentence.",
    )
    answer = await assistant.run("Explain how LLM caching works.")
    review = await critic.run(f"Assistant answered:\n{answer}")
    print(review)


if __name__ == "__main__":
    asyncio.run(main())
```

```bash
# Start Elastic APM Server + Kibana via docker-compose (Elastic Stack quickstart),
# or use Elastic Cloud and set ELASTIC_APM_SERVER_URL + ELASTIC_APM_SECRET_TOKEN.

pip install 'elastic-apm>=6.20' \
            'agent-framework>=1.4' \
            'openinference-instrumentation-openai>=0.1'
export OPENAI_API_KEY=sk-...
export ELASTIC_APM_SERVER_URL=http://localhost:8200
# Cloud only:
# export ELASTIC_APM_SECRET_TOKEN=...
python maf_elastic.py
# Kibana APM UI: http://localhost:5601/app/apm → Services → maf-demo
```

**Sources:** Elastic APM Python agent — https://www.elastic.co/guide/en/apm/agent/python/current/index.html · Elastic APM OpenTelemetry bridge — https://www.elastic.co/guide/en/apm/agent/python/current/opentelemetry-bridge.html · Microsoft Agent Framework observability — https://learn.microsoft.com/en-us/agent-framework/python/observability · Note: `elasticapm.instrument()` auto-instruments `httpx`/`requests`/`urllib3` and injects W3C `traceparent` on outbound HTTP — no separate `HTTPXClientInstrumentor` needed for this path.

*Last verified: 2026-05-17 with Python 3.12.*

---

## 10. LangGraph + LangSmith (pure OTLP — LangChain's hosted UI)

LangSmith is LangChain's hosted observability platform. observent uses its OTLP HTTP endpoint so the same `OTLPSpanExporter` + `LangChainInstrumentor` stack works across cloud (US / EU) and enterprise self-host. No `langsmith` SDK code is generated — LangSmith maps OTel-GenAI conventions to its native trace schema on ingest.

```python
# langgraph_langsmith.py
import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

# --- Observability: LangSmith via OTLP HTTP ---
_ls_base = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com").rstrip("/")
_ls_headers = {"x-api-key": os.environ["LANGSMITH_API_KEY"]}
if project := os.getenv("LANGSMITH_PROJECT"):
    _ls_headers["Langsmith-Project"] = project

exporter = OTLPSpanExporter(endpoint=f"{_ls_base}/otel/v1/traces", headers=_ls_headers)
provider = TracerProvider(resource=Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", "langgraph-langsmith-demo")}))
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

LangChainInstrumentor().instrument(tracer_provider=provider)
HTTPXClientInstrumentor().instrument(tracer_provider=provider)  # W3C traceparent on outbound HTTP

# --- Agent ---
llm = ChatAnthropic(model="claude-sonnet-4-6")


def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"It's sunny in {city}."


agent = create_react_agent(llm, tools=[get_weather])
result = agent.invoke({"messages": [{"role": "user", "content": "Weather in Paris?"}]})
print(result["messages"][-1].content)

provider.shutdown()  # flush before exit
```

```bash
pip install 'langgraph>=0.2' 'langchain-anthropic' \
            'openinference-instrumentation-langchain>=0.1' \
            'opentelemetry-sdk>=1.25' 'opentelemetry-exporter-otlp-proto-http>=1.25' \
            'opentelemetry-instrumentation-httpx>=0.48'
export ANTHROPIC_API_KEY=sk-...
export LANGSMITH_API_KEY=ls_...
# Optional: route to a named project (default: "default")
# export LANGSMITH_PROJECT=langgraph-demo
# Optional: EU region or self-host
# export LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
python langgraph_langsmith.py
# UI: https://smith.langchain.com → your project → Traces
```

**Sources:** LangSmith OTLP ingestion (`/otel/v1/traces`) — https://docs.smith.langchain.com/observability/how_to_guides/trace_with_opentelemetry · LangSmith API key auth (`x-api-key`) — https://docs.smith.langchain.com/observability/how_to_guides/trace_with_opentelemetry#1-set-up-environment · LangSmith regions / endpoints — https://docs.smith.langchain.com/administration/concepts#regions · `openinference-instrumentation-langchain` — https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-langchain

*Last verified: 2026-05-15 with Python 3.12.*

---

## 11. Google ADK + Arize Phoenix (OpenInference instrumentor)

Google's Agent Development Kit (ADK) builds agents around a `Runner` + `Session`. `openinference-instrumentation-google-adk` wraps the runner so agent runs, tool calls, and the underlying Gemini model requests land as a connected span tree. The instrumentor emits OpenInference attributes natively — Phoenix consumes them directly; swap the exporter (see Example 3 / 6 / 10 / 12 / 13) to target SigNoz / Langfuse / Elastic APM / LangSmith / Opik / Jaeger instead.

```python
# google_adk_phoenix.py
import asyncio
import os
from phoenix.otel import register
from openinference.instrumentation.google_adk import GoogleADKInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# --- Observability: Phoenix local ---
tracer_provider = register(
    project_name=os.getenv("PHOENIX_PROJECT_NAME", "google-adk-demo"),
    endpoint=os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces"),
)
GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)
HTTPXClientInstrumentor().instrument(tracer_provider=tracer_provider)  # W3C traceparent on outbound HTTP


# --- Agent ---
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"It's 72F and sunny in {city}."


agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    instruction="You answer weather questions concisely using the get_weather tool.",
    tools=[get_weather],
)


async def main() -> None:
    runner = InMemoryRunner(agent=agent, app_name="weather-app")
    session = await runner.session_service.create_session(
        app_name="weather-app", user_id="demo-user", session_id="demo-session-001"
    )
    content = types.Content(role="user", parts=[types.Part(text="What's the weather in Tokyo?")])
    async for event in runner.run_async(
        user_id=session.user_id, session_id=session.id, new_message=content
    ):
        if event.is_final_response() and event.content:
            print(event.content.parts[0].text)
    tracer_provider.shutdown()  # flush before exit


if __name__ == "__main__":
    asyncio.run(main())
    # Open http://localhost:6006 — you should see:
    #   Runner.run_async -> agent_run [weather_agent] -> tool: get_weather -> LLM (gemini-2.0-flash)
```

```bash
phoenix serve &  # background Phoenix UI on :6006
pip install 'google-adk>=2.3' 'openinference-instrumentation-google-adk>=0.1.15' \
            'arize-phoenix>=15.0' \
            'opentelemetry-sdk>=1.41' 'opentelemetry-exporter-otlp-proto-http>=1.41' \
            'opentelemetry-instrumentation-httpx>=0.48'
export GOOGLE_API_KEY=...   # or set GOOGLE_GENAI_USE_VERTEXAI=TRUE + Vertex creds
python google_adk_phoenix.py
```

**Sources:** Google ADK docs — https://google.github.io/adk-docs/ · ADK `Runner` / `Session` quickstart — https://google.github.io/adk-docs/get-started/quickstart/ · `openinference-instrumentation-google-adk` — https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk · Phoenix `register()` — https://docs.arize.com/phoenix/tracing/how-to-tracing/setup-tracing/setup-tracing-python

*Last verified: 2026-06-25 with Python 3.12.*

---

## Multi-Backend Fan-Out (Phoenix + Langfuse + SigNoz + Elastic APM + LangSmith + Opik + Jaeger)

Single `TracerProvider` with one `BatchSpanProcessor` per OTLP backend (Phoenix, Langfuse, SigNoz, LangSmith, Opik, Jaeger), plus a native `elasticapm.Client` next to it — the agent's OTel bridge attaches to the same global tracer provider, so the same spans flow to all seven destinations. Because the set contains Phoenix **and** at least one of {Langfuse, SigNoz, Elastic APM, LangSmith, Opik, Jaeger}, the convention rule resolves to **`both`** — every span must carry OpenInference and OTel-GenAI keys. See `openinference.md` and `otel_genai.md` for canonical key lists.

```python
# fanout.py
import os
import base64
import elasticapm
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

provider = TracerProvider(resource=Resource.create({"service.name": "fanout-demo"}))

# Phoenix
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
    endpoint=os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces"),
    headers={"Authorization": f"Bearer {os.environ['PHOENIX_API_KEY']}"} if os.getenv("PHOENIX_API_KEY") else {},
)))

# Langfuse
_lf_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com").rstrip("/")
_lf_auth = base64.b64encode(
    f"{os.environ['LANGFUSE_PUBLIC_KEY']}:{os.environ['LANGFUSE_SECRET_KEY']}".encode()
).decode()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
    endpoint=f"{_lf_host}/api/public/otel/v1/traces",
    headers={"Authorization": f"Basic {_lf_auth}"},
)))

# SigNoz
_sn_headers = {"signoz-access-token": os.environ["SIGNOZ_INGESTION_KEY"]} if os.getenv("SIGNOZ_INGESTION_KEY") else {}
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
    endpoint=os.getenv("SIGNOZ_ENDPOINT", "http://localhost:4318/v1/traces"),
    headers=_sn_headers,
)))

# LangSmith
_ls_base = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com").rstrip("/")
_ls_headers = {"x-api-key": os.environ["LANGSMITH_API_KEY"]}
if os.getenv("LANGSMITH_PROJECT"):
    _ls_headers["Langsmith-Project"] = os.environ["LANGSMITH_PROJECT"]
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
    endpoint=f"{_ls_base}/otel/v1/traces",
    headers=_ls_headers,
)))

# Opik — self-host needs no auth; cloud needs Authorization + Comet-Workspace.
_op_base = os.getenv("OPIK_URL_OVERRIDE", "http://localhost:5173/api").rstrip("/")
_op_headers = {}
if os.getenv("OPIK_API_KEY"):
    _op_headers["Authorization"] = os.environ["OPIK_API_KEY"]
if os.getenv("OPIK_WORKSPACE"):
    _op_headers["Comet-Workspace"] = os.environ["OPIK_WORKSPACE"]
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
    endpoint=f"{_op_base}/v1/private/otel/v1/traces",
    headers=_op_headers,
)))

# Jaeger — local OTLP receiver, no auth.
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
    endpoint=os.getenv("JAEGER_ENDPOINT", "http://localhost:4318/v1/traces"),
)))

trace.set_tracer_provider(provider)
HTTPXClientInstrumentor().instrument(tracer_provider=provider)  # W3C traceparent on outbound HTTP

# Elastic APM (native agent — coexists with the TracerProvider above; bridges OTel spans).
elasticapm.Client(service_name=os.getenv("ELASTIC_APM_SERVICE_NAME", "fanout-demo"))
elasticapm.instrument()

tracer = trace.get_tracer("fanout-demo")

# Every span must carry BOTH conventions when fanning out across Phoenix + (Langfuse|SigNoz|Elastic APM).
with tracer.start_as_current_span("smoke-llm") as span:
    # OpenInference
    span.set_attribute("openinference.span.kind", "LLM")
    span.set_attribute("llm.model_name", "claude-sonnet-4-6")
    span.set_attribute("llm.provider", "anthropic")
    span.set_attribute("llm.token_count.prompt", 12)
    span.set_attribute("llm.token_count.completion", 8)
    span.set_attribute("llm.token_count.total", 20)
    # OTel-GenAI
    span.set_attribute("gen_ai.operation.name", "chat")
    span.set_attribute("gen_ai.provider.name", "anthropic")
    span.set_attribute("gen_ai.request.model", "claude-sonnet-4-6")
    span.set_attribute("gen_ai.usage.input_tokens", 12)
    span.set_attribute("gen_ai.usage.output_tokens", 8)

provider.shutdown()
# Spans now in all seven backends. Failure in one doesn't affect the others.
```

For Phoenix-less fan-out (e.g. `langfuse,signoz`, `signoz,elastic-apm`, or `langsmith,jaeger`), drop the OI block — `otel-genai` alone is sufficient.

**Sources:** OTel multi-exporter (multiple `BatchSpanProcessor` on one `TracerProvider`) — https://opentelemetry.io/docs/languages/python/exporters/ · Phoenix OTLP — https://docs.arize.com/phoenix/tracing/how-to-tracing/setup-tracing/setup-tracing-python · Langfuse OTLP — https://langfuse.com/docs/opentelemetry/get-started · SigNoz OTLP — https://signoz.io/docs/instrumentation/opentelemetry-python/ · Elastic APM OpenTelemetry bridge — https://www.elastic.co/guide/en/apm/agent/python/current/opentelemetry-bridge.html · LangSmith OTLP — https://docs.smith.langchain.com/observability/how_to_guides/trace_with_opentelemetry · Opik OTLP — https://www.comet.com/docs/opik/tracing/opentelemetry/overview · Jaeger OTLP — https://www.jaegertracing.io/docs/latest/apis/#opentelemetry-protocol

*Last verified: 2026-05-15 with Python 3.12.*

---

## 12. CrewAI + Opik (pure OTLP — Comet's open-source UI)

Opik is Comet's open-source LLM observability platform. observent uses its OTLP HTTP endpoint so the same `OTLPSpanExporter` + `CrewAIInstrumentor` stack works across self-host (free, Docker) and Opik Cloud. No `opik` SDK code is generated — Opik maps OTel-GenAI conventions to its native trace schema on ingest, so it's mechanically identical to the SigNoz / LangSmith paths. The example defaults to a local self-hosted Opik (no auth); uncomment the cloud block to target Opik Cloud.

```python
# crew_opik.py
import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from openinference.instrumentation.crewai import CrewAIInstrumentor
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# --- Observability: Opik via OTLP HTTP ---
# Self-host default: http://localhost:5173/api ; Opik Cloud: https://www.comet.com/opik/api
_op_base = os.getenv("OPIK_URL_OVERRIDE", "http://localhost:5173/api").rstrip("/")
_op_headers = {}
if api_key := os.getenv("OPIK_API_KEY"):  # cloud only; self-host needs no auth
    _op_headers["Authorization"] = api_key
if workspace := os.getenv("OPIK_WORKSPACE"):
    _op_headers["Comet-Workspace"] = workspace
if project := os.getenv("OPIK_PROJECT_NAME"):
    _op_headers["projectName"] = project

exporter = OTLPSpanExporter(endpoint=f"{_op_base}/v1/private/otel/v1/traces", headers=_op_headers)
provider = TracerProvider(resource=Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", "crewai-opik-demo")}))
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

CrewAIInstrumentor().instrument(tracer_provider=provider, use_event_listener=True)  # required for LLM spans — see matrix.md § CrewAI
LangChainInstrumentor().instrument(tracer_provider=provider)  # CrewAI's underlying LLM calls
HTTPXClientInstrumentor().instrument(tracer_provider=provider)  # W3C traceparent on outbound HTTP

# --- Agents ---
llm = ChatOpenAI(model="gpt-4o")

researcher = Agent(
    role="Senior Research Analyst",
    goal="Find accurate, source-backed information",
    backstory="You are a meticulous researcher.",
    llm=llm, verbose=True,
)
writer = Agent(
    role="Technical Writer",
    goal="Turn research into clear summaries",
    backstory="You write for a developer audience.",
    llm=llm, verbose=True,
)

research = Task(
    description="Research the latest developments in {topic}",
    expected_output="A structured summary with sources",
    agent=researcher,
)
write = Task(
    description="Write a 3-paragraph summary based on the research",
    expected_output="A polished 3-paragraph summary",
    agent=writer,
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research, write],
    process=Process.sequential,
    verbose=True,
)

if __name__ == "__main__":
    result = crew.kickoff(inputs={"topic": "multi-agent observability"})
    print(result)
    provider.shutdown()  # flush before exit
```

```bash
pip install 'crewai>=0.80' 'langchain-openai>=0.2' \
            'openinference-instrumentation-crewai>=1.1' \
            'openinference-instrumentation-langchain>=0.1' \
            'opentelemetry-sdk>=1.25' 'opentelemetry-exporter-otlp-proto-http>=1.25' \
            'opentelemetry-instrumentation-httpx>=0.48'
export OPENAI_API_KEY=sk-...
# Self-host (default): start Opik locally, then point at it (no auth needed)
#   git clone https://github.com/comet-ml/opik.git && cd opik && ./opik.sh
export OPIK_URL_OVERRIDE=http://localhost:5173/api
# Opik Cloud instead:
# export OPIK_URL_OVERRIDE=https://www.comet.com/opik/api
# export OPIK_API_KEY=... OPIK_WORKSPACE=your-workspace
# Optional: route to a named project (default: "Default Project")
# export OPIK_PROJECT_NAME=crewai-demo
python crew_opik.py
# Self-host UI: http://localhost:5173 → Projects → Traces
```

**Sources:** Opik OpenTelemetry integration (`/v1/private/otel/v1/traces`) — https://www.comet.com/docs/opik/tracing/opentelemetry/overview · Opik self-host (Docker, port 5173) — https://www.comet.com/docs/opik/self-host/local_deployment · `openinference-instrumentation-crewai` — https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-crewai

*Last verified: 2026-07-02 with Python 3.12.*

---

## 13. smolagents + Jaeger (pure OTLP — local trace view, zero account)

Jaeger is the CNCF distributed-tracing system. Run the all-in-one container, point the
`OTLPSpanExporter` at its OTLP receiver (`:4318`), and the same `SmolagentsInstrumentor` stack used
for SigNoz/Langfuse works unchanged. No auth, no account, no SDK — Jaeger stores and displays the
spans generically (`gen_ai.*` attributes show as ordinary span tags; there's no LLM-cost panel).
Great for a fast, dependency-free local view of the span tree.

```python
# smolagents_jaeger.py
import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from smolagents import CodeAgent, DuckDuckGoSearchTool, LiteLLMModel

# --- Observability: Jaeger via OTLP HTTP (no auth) ---
endpoint = os.getenv("JAEGER_ENDPOINT", "http://localhost:4318/v1/traces")
provider = TracerProvider(resource=Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", "smolagents-jaeger-demo")}))
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
trace.set_tracer_provider(provider)

SmolagentsInstrumentor().instrument(tracer_provider=provider)
HTTPXClientInstrumentor().instrument(tracer_provider=provider)  # W3C traceparent on outbound HTTP

# --- Agent ---
model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-6")
agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=model)

if __name__ == "__main__":
    answer = agent.run("Who won the latest Formula 1 Grand Prix?")
    print(answer)
    provider.shutdown()  # flush before exit
```

```bash
# Start Jaeger locally (UI on :16686, OTLP on :4318):
docker run -d --name jaeger -e COLLECTOR_OTLP_ENABLED=true \
  -p 16686:16686 -p 4318:4318 -p 4317:4317 jaegertracing/jaeger:2.19.0

pip install 'smolagents>=1.0' 'openinference-instrumentation-smolagents>=0.1' \
            'opentelemetry-sdk>=1.25' 'opentelemetry-exporter-otlp-proto-http>=1.25' \
            'opentelemetry-instrumentation-httpx>=0.48'
export ANTHROPIC_API_KEY=sk-ant-...
# Default endpoint is http://localhost:4318/v1/traces; override with JAEGER_ENDPOINT if needed.
python smolagents_jaeger.py
# UI: http://localhost:16686 → Service "smolagents-jaeger-demo" → Find Traces
```

**Sources:** smolagents — https://huggingface.co/docs/smolagents · Jaeger OTLP ingestion — https://www.jaegertracing.io/docs/latest/apis/#opentelemetry-protocol · Jaeger all-in-one image — https://hub.docker.com/r/jaegertracing/jaeger · `openinference-instrumentation-smolagents` — https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-smolagents

*Last verified: 2026-06-25 with Python 3.12.*

---

## 14. Claude Code (vendor runtime) -> litellm proxy + Langfuse (grouped by session id)

You can't instrument Claude Code's loop, but every model call it makes can be routed through a litellm proxy you *do* control. A `CustomLogger` on the proxy reads a per-run id off the request header Claude Code injects and stamps it as `session.id` / `gen_ai.conversation.id`, so the run's calls group in Langfuse. This is **grouping, not one trace** — see `references/gateway.md` for the full engine and the honest ceiling.

```python
# observent_litellm.py — compact form of the gateway.md reference adapter.
# Register in the proxy:  litellm_settings: { callbacks: ["observent_litellm.handler"] }
import os
from datetime import datetime
from litellm.integrations.custom_logger import CustomLogger
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.trace import SpanKind, Status, StatusCode

# Proxy is its own process -> it needs its own exporter to Langfuse.
provider = TracerProvider(resource=Resource.create({"service.name": "litellm-gateway"}))
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))  # reads OTEL_EXPORTER_OTLP_* env
trace.set_tracer_provider(provider)
_tracer = trace.get_tracer("observent.gateway")
_HEADER = os.getenv("OBSERVENT_CORRELATION_HEADER", "x-observent-session-id").lower()


def _emit(kwargs, response_obj, start_time, end_time, ok):
    req = (kwargs.get("litellm_params") or {}).get("proxy_server_request") or {}
    headers = {str(k).lower(): str(v) for k, v in dict(req.get("headers") or {}).items()}
    cid = headers.get(_HEADER)
    span = _tracer.start_span("chat", kind=SpanKind.CLIENT,
                              start_time=int(start_time.timestamp() * 1e9) if isinstance(start_time, datetime) else None)
    try:
        if cid:                                   # otel-genai convention (Langfuse)
            span.set_attribute("gen_ai.conversation.id", cid)
            span.set_attribute("session.id", cid)
        if kwargs.get("model"):
            span.set_attribute("gen_ai.request.model", kwargs["model"])
        usage = getattr(response_obj, "usage", None)
        if usage is not None:
            span.set_attribute("gen_ai.usage.input_tokens", getattr(usage, "prompt_tokens", 0))
            span.set_attribute("gen_ai.usage.output_tokens", getattr(usage, "completion_tokens", 0))
        span.set_status(Status(StatusCode.OK if ok else StatusCode.ERROR))
    finally:
        span.end(end_time=int(end_time.timestamp() * 1e9) if isinstance(end_time, datetime) else None)


class _Logger(CustomLogger):
    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        _emit(kwargs, response_obj, start_time, end_time, True)
    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        _emit(kwargs, response_obj, start_time, end_time, False)


handler = _Logger()
```

```bash
# 1. Install (proxy side):
pip install 'litellm[proxy]>=1.86' 'opentelemetry-sdk>=1.41' \
            'opentelemetry-exporter-otlp-proto-http>=1.41'

# 2. Proxy config + point spans at Langfuse:
cat > litellm_config.yaml <<'YAML'
model_list:
  - model_name: claude-sonnet-4-6
    litellm_params:
      model: anthropic/claude-sonnet-4-6
litellm_settings:
  callbacks: ["observent_litellm.handler"]
YAML
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://localhost:3000/api/public/otel/v1/traces
export OTEL_EXPORTER_OTLP_TRACES_HEADERS="Authorization=Basic $(printf '%s:%s' "$LANGFUSE_PUBLIC_KEY" "$LANGFUSE_SECRET_KEY" | base64)"
export ANTHROPIC_API_KEY=sk-ant-...
litellm --config litellm_config.yaml --port 4000

# 3. Point Claude Code at the proxy and inject a per-run id (vendor-runtime side):
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_CUSTOM_HEADERS="x-observent-session-id: $(uuidgen)"
claude -p "summarize the README"

# Langfuse -> Sessions: every model call from that Claude Code run groups under the one id.
```

For Phoenix (OI) instead of Langfuse, set the convention to `oi` and emit `session.id` only (Phoenix groups sessions natively); see `references/gateway.md`.

**Sources:** litellm custom callbacks — https://docs.litellm.ai/docs/observability/custom_callback · litellm proxy logging / request headers — https://docs.litellm.ai/docs/proxy/logging · Claude Code env vars (`ANTHROPIC_BASE_URL`, `ANTHROPIC_CUSTOM_HEADERS`) — https://code.claude.com/docs/en/env-vars · Langfuse OTLP endpoint — https://langfuse.com/docs/opentelemetry/get-started

*Last verified: 2026-06-27 with Python 3.12 (engine reviewed; not yet re-run end-to-end — see `gateway.md`).*

---

## Verification Checklist

```
[ ] Required packages installed (pip list | grep <backend>)
[ ] Required env vars set (use validate_setup.py to check)
[ ] App runs without import errors
[ ] Trace appears in backend UI within 10s of running the app
[ ] LLM spans show non-zero token counts
[ ] LLM spans show recognised model name (cost is non-zero in UI)
[ ] Span tree shows correct hierarchy (Crew → Agent → LLM, or Workflow → Step → LLM)
[ ] Multi-turn conversations group under one session.id
[ ] No credentials hardcoded; .env is in .gitignore
```

Or just run (`<skill-dir>` is this skill's own folder — in Claude Code substitute `${CLAUDE_SKILL_DIR}`; other agents use the skill folder they loaded `SKILL.md` from — see SKILL.md § Step 1.1):

```bash
# single backend
python "<skill-dir>/scripts/validate_setup.py" <backend> --smoke-test
# multi-backend fan-out (comma-separated)
python "<skill-dir>/scripts/validate_setup.py" phoenix,signoz --smoke-test
```

---

## Common Issues

- **No traces appear** → check env vars loaded, force-flush before exit (`provider.shutdown()` or `langfuse.flush()`).
- **Token counts missing** → instrumentor mismatch or custom LLM wrapper not surfacing `usage`. For Custom path, set explicitly via `set_llm_attrs()`.
- **Cost shows $0** → backend can't recognise the model name; verify `llm.model_name` matches the backend's price table.
- **Orphan spans / broken trace tree** → context propagation. Check Python ≥ 3.11 (or use `copy_context().run`); use `start_as_current_span`; enable HTTPX/Requests instrumentors for cross-service.
- **OpenAI Agents SDK shows raw HTTP not handoffs** → switch from `openinference-instrumentation-openai` to `openinference-instrumentation-openai-agents` and register via `set_trace_processors()`.
- **SigNoz Cloud 401** → header name is `signoz-access-token` (not `signoz-ingestion-key`); verify against current docs.
