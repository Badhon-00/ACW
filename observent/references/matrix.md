# observent Reference

Complete reference for frameworks, backends, integration mechanics, span attributes, and context propagation. `../SKILL.md` references this document during code generation.

---

## Maintainer's sources

Re-verify each section against the upstream artifacts listed under it (per-subsection `**Sources:**` lines) or via the consolidated list below. Bump the per-section `Last verified` date when you re-check.

**Specs & SDK:**
- OpenInference semantic conventions — https://github.com/Arize-ai/openinference/blob/main/spec/semantic_conventions.md
- OTel semantic conventions (GenAI) — https://github.com/open-telemetry/semantic-conventions/tree/main/docs/gen-ai
- OTel Python SDK & instrumentation — https://opentelemetry.io/docs/languages/python/
- W3C Trace Context (Level 1) — https://www.w3.org/TR/trace-context/
- OTel baggage API — https://opentelemetry.io/docs/specs/otel/baggage/api/

**Backends:**
- Arize Phoenix — https://docs.arize.com/phoenix
- Langfuse — https://langfuse.com/docs
- SigNoz — https://signoz.io/docs
- Elastic APM Python agent — https://www.elastic.co/guide/en/apm/agent/python/current/index.html
- LangSmith — https://docs.smith.langchain.com
- Opik (Comet) — https://www.comet.com/docs/opik/
- Jaeger — https://www.jaegertracing.io/docs/

**Frameworks (also linked in per-framework subsections):**
- LangGraph — https://langchain-ai.github.io/langgraph/
- CrewAI — https://docs.crewai.com
- Microsoft Agent Framework — https://github.com/microsoft/agent-framework
- Anthropic Agents — https://docs.anthropic.com/en/docs/agents
- OpenAI Agents SDK — https://openai.github.io/openai-agents-python/
- smolagents — https://huggingface.co/docs/smolagents
- LlamaIndex — https://docs.llamaindex.ai
- Google ADK — https://google.github.io/adk-docs/

**OpenInference instrumentors (PyPI):**
- https://github.com/Arize-ai/openinference/tree/main/python — canonical Python monorepo; each per-instrumentor README has install + usage.

Last reviewed: 2026-06-20.

---

## 9 × 7 Compatibility Matrix

| Framework | Arize Phoenix<br>*OI* | Langfuse<br>*OTel-GenAI* | SigNoz<br>*OTel-GenAI* | Elastic APM<br>*OTel-GenAI* | LangSmith<br>*OTel-GenAI* | Opik<br>*OTel-GenAI* | Jaeger<br>*OTel-GenAI* |
|---|---|---|---|---|---|---|---|
| LangGraph | OI: `LangChainInstrumentor` | LangChain callback (`langfuse.langchain.CallbackHandler`) | OTLP + OI: `LangChainInstrumentor` | Native agent + OI: `LangChainInstrumentor` | OTLP + OI: `LangChainInstrumentor` | OTLP + OI: `LangChainInstrumentor` | OTLP + OI: `LangChainInstrumentor` |
| CrewAI | OI: `CrewAIInstrumentor` (+ LangChain) | LangChain callback (CrewAI inherits) | OTLP + OI: `CrewAIInstrumentor` | Native agent + OI: `CrewAIInstrumentor` | OTLP + OI: `CrewAIInstrumentor` | OTLP + OI: `CrewAIInstrumentor` | OTLP + OI: `CrewAIInstrumentor` |
| Microsoft Agent Framework | OI: `OpenAIInstrumentor` + MAF native OTel | OTLP exporter + MAF native OTel + `OpenAIInstrumentor` | OTLP + MAF native OTel + `OpenAIInstrumentor` | Native agent + MAF native OTel + `OpenAIInstrumentor` | OTLP + MAF native OTel + `OpenAIInstrumentor` | OTLP + MAF native OTel + `OpenAIInstrumentor` | OTLP + MAF native OTel + `OpenAIInstrumentor` |
| Anthropic Agents SDK | OI: `AnthropicInstrumentor` | `langfuse` decorator `@observe` (or `OpenAIInstrumentor`-style for Anthropic) | OTLP + OI: `AnthropicInstrumentor` | Native agent + OI: `AnthropicInstrumentor` | OTLP + OI: `AnthropicInstrumentor` | OTLP + OI: `AnthropicInstrumentor` | OTLP + OI: `AnthropicInstrumentor` |
| OpenAI Agents SDK | **Native trace processor** (`phoenix.otel.OpenAIAgentsTracingProcessor`) | **Native trace processor** (Langfuse OpenAIAgents processor) | **Native trace processor** with OTLP backend | Native APM agent + OpenAI Agents SDK trace processor (OTel bridge) | **Native trace processor** with OTLP backend | **Native trace processor** with OTLP backend | **Native trace processor** with OTLP backend |
| smolagents | OI: `SmolagentsInstrumentor` | OI: `SmolagentsInstrumentor` (exporter sends to Langfuse OTLP) | OTLP + OI: `SmolagentsInstrumentor` | Native agent + OI: `SmolagentsInstrumentor` | OTLP + OI: `SmolagentsInstrumentor` | OTLP + OI: `SmolagentsInstrumentor` | OTLP + OI: `SmolagentsInstrumentor` |
| LlamaIndex | OI: `LlamaIndexInstrumentor` | `langfuse.llama_index` callback | OTLP + OI: `LlamaIndexInstrumentor` | Native agent + OI: `LlamaIndexInstrumentor` | OTLP + OI: `LlamaIndexInstrumentor` | OTLP + OI: `LlamaIndexInstrumentor` | OTLP + OI: `LlamaIndexInstrumentor` |
| Google ADK | OI: `GoogleADKInstrumentor` | OTLP + OI: `GoogleADKInstrumentor` | OTLP + OI: `GoogleADKInstrumentor` | Native agent + OI: `GoogleADKInstrumentor` | OTLP + OI: `GoogleADKInstrumentor` | OTLP + OI: `GoogleADKInstrumentor` | OTLP + OI: `GoogleADKInstrumentor` |
| Custom | Manual spans + helper functions | Manual spans + `langfuse` decorator | Manual spans + OTLP exporter | Manual spans + `elasticapm.Client` (OTel bridge) | Manual spans + OTLP exporter | Manual spans + OTLP exporter | Manual spans + OTLP exporter |

**Reading the matrix:** the italic label under each backend's header (e.g. *OI*, *OTel-GenAI*) is the **semantic convention** that backend prefers — Phoenix is OpenInference-native; the other six are OTel-GenAI-native. The convention observent emits at generation time is derived mechanically from the backend set you pick (see SKILL.md § Step 3): single Phoenix → OI only; any Phoenix-less subset → OTel-GenAI only; Phoenix + any other → both.

**OI** = OpenInference instrumentor (`openinference-instrumentation-*`). The OI instrumentor itself emits raw OTel spans regardless of which backend you target — only the exporter destination and the *attribute keys* the backend reads differ. For Elastic APM, the OI instrumentor still emits OTel spans; the `elasticapm.Client` agent picks them up via its OTel bridge (no separate exporter needed) and ingests them alongside auto-instrumented transaction spans.

**Sources:** matrix entries are derived from the per-framework and per-backend reference subsections below — re-verify there when bumping a row or column.

---

## Verified Versions

Last verified: 2026-07-03 against Python 3.12.

| Package | Pinned version |
|---|---|
| arize-phoenix | ==17.15.0 |
| langfuse | ==4.13.0 |
| elastic-apm | ==6.26.2 |
| langsmith | ==0.9.7 |
| opik | ==2.1.14 |
| opentelemetry-sdk | ==1.43.0 |
| opentelemetry-exporter-otlp-proto-http | ==1.43.0 |
| langgraph | ==1.2.7 |
| crewai | ==1.15.1 |
| agent-framework | ==1.10.0 |
| anthropic | ==0.116.0 |
| openai-agents | ==0.17.7 |
| smolagents | ==1.26.0 |
| llama-index | ==0.14.23 |
| openinference-instrumentation-langchain | ==0.1.67 |
| openinference-instrumentation-crewai | ==1.1.10 |
| openinference-instrumentation-openai | ==0.1.52 |
| openinference-instrumentation-openai-agents | ==1.6.1 |
| openinference-instrumentation-anthropic | ==1.0.6 |
| openinference-instrumentation-llama-index | ==4.4.3 |
| openinference-instrumentation-smolagents | ==0.1.32 |
| google-adk | ==2.3.0 |
| openinference-instrumentation-google-adk | ==0.1.17 |

These are the exact versions `examples.md` and the per-framework install commands below target. When bumping any pin, update this table **and** the matching per-backend Install line, the per-framework `pip install` snippet, and the `*Last verified: …*` footer of any example in `examples.md` that was re-run.

**Sources:** each row's PyPI page at `https://pypi.org/project/<package-name>/` — pins are the exact version the most recent re-verification pass installed.

---

## Per-Backend Reference

### Arize Phoenix

- **Type:** Open source (Apache 2.0). Local UI at `http://localhost:6006` via `pip install arize-phoenix`. Cloud at `app.phoenix.arize.com`.
- **Modern setup API:** `phoenix.otel.register(project_name=..., auto_instrument=True)` returns a `TracerProvider` and (with `auto_instrument=True`) auto-loads any installed OpenInference instrumentors.
- **Endpoints:**
  - Local OTLP HTTP: `http://localhost:6006/v1/traces`
  - Local OTLP gRPC: `localhost:4317`
  - Cloud OTLP HTTP: `https://app.phoenix.arize.com/v1/traces`
- **Auth:** None for local. Cloud uses `PHOENIX_API_KEY` as `Authorization: Bearer <key>`.
- **Required env vars:** None local. Cloud: `PHOENIX_API_KEY`, optional `PHOENIX_COLLECTOR_ENDPOINT`.
- **Optional env vars:** `PHOENIX_PROJECT_NAME` (groups traces into projects).
- **Install:** `pip install 'arize-phoenix==17.15.0' 'opentelemetry-sdk==1.43.0' 'opentelemetry-exporter-otlp-proto-http==1.43.0'`
- **Sources:** Phoenix docs — https://docs.arize.com/phoenix · `phoenix.otel.register` — https://docs.arize.com/phoenix/tracing/how-to-tracing/setup-tracing/setup-tracing-python · OpenInference instrumentors — https://github.com/Arize-ai/openinference/tree/main/python

**Canonical setup snippet:**

```python
import os
from phoenix.otel import register

tracer_provider = register(
    project_name=os.getenv("PHOENIX_PROJECT_NAME", "my-agent-app"),
    endpoint=os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces"),
    auto_instrument=True,  # picks up installed openinference-instrumentation-* packages
)
```

> **`PHOENIX_PROJECT_NAME` in a multi-backend fan-out.** `register(project_name=...)` is
> the **only** thing that reads `PHOENIX_PROJECT_NAME` — the manual `TracerProvider`
> fan-out (§ Multi-Backend Fan-Out, the recommended path when Phoenix is combined with
> another backend) never calls `register()`, so setting `PHOENIX_PROJECT_NAME` there has
> **zero effect** and every trace silently lands in Phoenix's `default` project. For raw
> OTLP, Phoenix routes on the **`openinference.project.name` resource attribute**, so fold
> the env var into the resource instead:
>
> ```python
> resource_attrs = {"service.name": service_name}
> if phoenix_project := os.getenv("PHOENIX_PROJECT_NAME"):
>     resource_attrs["openinference.project.name"] = phoenix_project
> provider = TracerProvider(resource=Resource.create(resource_attrs))
> ```

For local development with no Phoenix server running, start one inline:

```python
import phoenix as px
session = px.launch_app()  # UI on http://localhost:6006
```

### Langfuse

- **Type:** Open source (MIT). Self-hostable via Docker. Cloud at `cloud.langfuse.com` (EU) and `us.cloud.langfuse.com` (US).
- **Integration mechanisms:**
  - **LangChain callback** (LangGraph, CrewAI) — `from langfuse.langchain import CallbackHandler`
  - **Decorator** (Custom, Anthropic SDK) — `from langfuse import observe`
  - **OpenAI wrapper** (raw OpenAI SDK use) — `from langfuse.openai import openai`
  - **OTLP** (any OTel pipeline) — POST to `<host>/api/public/otel/v1/traces` with Basic auth
- **Endpoints (OTLP path):**
  - Self-host: `http://localhost:3000/api/public/otel/v1/traces`
  - Cloud US: `https://us.cloud.langfuse.com/api/public/otel/v1/traces`
  - Cloud EU: `https://cloud.langfuse.com/api/public/otel/v1/traces`
- **Auth:** HTTP Basic — `Authorization: Basic base64(public_key:secret_key)`.
- **Required env vars:** `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`. Optional `LANGFUSE_HOST` (defaults to `https://cloud.langfuse.com`).
- **Install:** `pip install 'langfuse==4.13.0'` (plus framework-specific extras as listed below) — required only for the LangChain-callback / `@observe` decorator / OpenAI-wrapper integration mechanisms above. The `langfuse` PyPI package is **not** required for the **OTLP path** observent generates for the multi-backend fan-out (which POSTs to `<host>/api/public/otel/v1/traces` with Basic auth and imports only `opentelemetry-exporter-otlp-proto-http`); install it only if you also want the Langfuse SDK directly (datasets, evals, prompt management).
- **Sources:** Langfuse docs — https://langfuse.com/docs · OTel integration — https://langfuse.com/docs/opentelemetry/get-started · LangChain integration — https://langfuse.com/docs/integrations/langchain · `@observe` decorator — https://langfuse.com/docs/sdk/python/decorators

**Canonical setup snippets:**

LangChain callback (LangGraph, CrewAI):
```python
import os
from langfuse.langchain import CallbackHandler

langfuse_handler = CallbackHandler()  # reads env vars LANGFUSE_PUBLIC_KEY/SECRET_KEY/HOST
```

Decorator (Custom, Anthropic SDK):
```python
from langfuse import observe, get_client

langfuse = get_client()

@observe()
def run_agent(user_input: str) -> str:
    ...
    return result
```

OTLP (when you already have a `TracerProvider`):
```python
import base64, os
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com").rstrip("/")
auth = base64.b64encode(
    f"{os.environ['LANGFUSE_PUBLIC_KEY']}:{os.environ['LANGFUSE_SECRET_KEY']}".encode()
).decode()

exporter = OTLPSpanExporter(
    endpoint=f"{host}/api/public/otel/v1/traces",
    headers={"Authorization": f"Basic {auth}"},
)
```

### SigNoz

- **Type:** Open source. Self-host via Docker Compose. Cloud at `signoz.cloud` with US/EU/IN regions.
- **Integration mechanism:** Pure OTLP — works with any OpenTelemetry-instrumented code. Pair with `openinference-instrumentation-*` for LLM-specific attributes.
- **Endpoints:**
  - Self-host OTLP HTTP: `http://localhost:4318/v1/traces`
  - Self-host OTLP gRPC: `localhost:4317`
  - Self-host UI: `http://localhost:8080` (Foundry-generated stack; older `docker-compose` releases used `3301`)
  - Cloud OTLP: `https://ingest.{us,eu,in}.signoz.cloud:443/v1/traces`
  - Cloud UI: `https://<tenant>.{us,eu,in}.signoz.cloud`
- **Auth:** None for self-host. Cloud requires header `signoz-access-token: <token>`. (Verify against current SigNoz docs — header name has changed historically.)
- **Required env vars:** `SIGNOZ_ENDPOINT` (full OTLP traces URL). Cloud also requires `SIGNOZ_INGESTION_KEY`.
- **Install:** `pip install 'opentelemetry-sdk==1.43.0' 'opentelemetry-exporter-otlp-proto-http==1.43.0'` + relevant `openinference-instrumentation-*` packages.
- **Sources:** SigNoz docs — https://signoz.io/docs · OTel Python instrumentation guide — https://signoz.io/docs/instrumentation/opentelemetry-python/ · Cloud ingestion-key header — https://signoz.io/docs/ingestion/signoz-cloud/keys/

**Self-host quickstart:** SigNoz deprecated its `docker-compose` manifests (2026); self-host now
flows through the **Foundry** CLI, which *generates* a plain compose file you run yourself:
```bash
curl -fsSL https://signoz.io/foundry.sh | bash        # installs foundryctl (checksum-verified)
foundryctl forge -f casting.yaml                       # generates pours/deployment/compose.yaml
docker compose -f pours/deployment/compose.yaml up -d --wait
# UI at http://localhost:8080 · OTLP receiver at http://localhost:4318
```
Full flow (incl. `casting.yaml`, the opamp OTLP-readiness caveat, and the CLI-install confirm gate):
`references/self_host.md § SigNoz`.

**Canonical setup snippet:**
```python
import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

headers = {}
if key := os.getenv("SIGNOZ_INGESTION_KEY"):
    headers["signoz-access-token"] = key

exporter = OTLPSpanExporter(
    endpoint=os.getenv("SIGNOZ_ENDPOINT", "http://localhost:4318/v1/traces"),
    headers=headers,
)

provider = TracerProvider(
    resource=Resource.create({
        "service.name": os.getenv("OTEL_SERVICE_NAME", "my-agent-app"),
    }),
)
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)
```

### Elastic APM

- **Type:** Open source (Apache 2.0). APM Server is part of the Elastic Stack. Self-host via Docker / Kubernetes; cloud at `elastic.co` with multi-region deployments.
- **Integration mechanism:** **Native `elastic-apm` Python agent** (the default observent generates). The agent posts to APM Server's intake endpoint and includes a built-in OTel bridge that picks up spans from the global OTel SDK — so OpenInference framework instrumentors keep working unchanged. A pure-OTLP path is also supported and documented as the secondary alternative.
- **Endpoints:**
  - Self-host APM Server: `http://localhost:8200` (agent default; intake at `/intake/v2/events`, OTLP at `/v1/traces`)
  - Self-host Kibana UI: `http://localhost:5601/app/apm`
  - Cloud APM Server: `https://<deployment>.apm.<region>.cloud.es.io:443`
  - Cloud Kibana UI: `https://<deployment>.kb.<region>.cloud.es.io/app/apm`
- **Auth:** Self-host — none unless a secret token is configured. Cloud — `Authorization: Bearer <ELASTIC_APM_SECRET_TOKEN>` or `Authorization: ApiKey <ELASTIC_APM_API_KEY>` (the agent reads either from env vars).
- **Required env vars:** `ELASTIC_APM_SERVER_URL` (defaults to `http://localhost:8200`). Cloud also needs `ELASTIC_APM_SECRET_TOKEN` or `ELASTIC_APM_API_KEY`. Optional: `ELASTIC_APM_SERVICE_NAME`, `ELASTIC_APM_ENVIRONMENT`.
- **Install:** `pip install 'elastic-apm==6.26.2'` + relevant `openinference-instrumentation-*` packages.
- **Sources:** Elastic APM Python agent — https://www.elastic.co/guide/en/apm/agent/python/current/index.html · OTel bridge — https://www.elastic.co/guide/en/apm/agent/python/current/opentelemetry-bridge.html · APM Server OTLP intake — https://www.elastic.co/guide/en/observability/current/apm-open-telemetry-direct.html

**Canonical setup (native agent — primary):**
```python
import os
import elasticapm
from openinference.instrumentation.langchain import LangChainInstrumentor

# 1. Native APM agent — picks up env vars and auto-instruments common frameworks.
elasticapm.Client(
    service_name=os.getenv("ELASTIC_APM_SERVICE_NAME", "my-agent-app"),
)
elasticapm.instrument()  # Flask / Django / FastAPI / asyncio / urllib3 / requests / ...

# 2. LLM instrumentor — emits OTel spans; the agent's OTel bridge ingests them.
LangChainInstrumentor().instrument()
```

**Alternative (pure OTLP — secondary):**
```python
import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

headers: dict[str, str] = {}
if token := os.getenv("ELASTIC_APM_SECRET_TOKEN"):
    headers["Authorization"] = f"Bearer {token}"
elif api_key := os.getenv("ELASTIC_APM_API_KEY"):
    headers["Authorization"] = f"ApiKey {api_key}"

server = os.getenv("ELASTIC_APM_SERVER_URL", "http://localhost:8200").rstrip("/")
exporter = OTLPSpanExporter(endpoint=f"{server}/v1/traces", headers=headers)

provider = TracerProvider(resource=Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", "my-agent-app")}))
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)
```

Use the OTLP path only when you have a strong reason to avoid the `elastic-apm` dependency — the native agent gives you transactions + auto-instrumented infra metrics for free, which is the main reason teams pick Elastic APM in the first place.

### LangSmith

- **Type:** Commercial. Cloud-first (US `https://api.smith.langchain.com`, EU `https://eu.api.smith.langchain.com`). Enterprise self-host is offered for paid tiers — point `LANGSMITH_ENDPOINT` at it.
- **Integration mechanism:** **Pure OTLP HTTP** to LangSmith's OTel ingest endpoint. LangSmith maps OTel-GenAI semantic conventions to its native trace schema, so the same `OTLPSpanExporter` + OpenInference framework instrumentor stack used for SigNoz works unchanged. No `langsmith` SDK code is generated — keeping LangSmith mechanically identical to SigNoz means it composes cleanly into the multi-backend fan-out template.
- **Endpoints:**
  - Cloud US OTLP: `https://api.smith.langchain.com/otel/v1/traces`
  - Cloud EU OTLP: `https://eu.api.smith.langchain.com/otel/v1/traces`
  - Self-host OTLP: `${LANGSMITH_ENDPOINT}/otel/v1/traces`
  - Cloud UI: `https://smith.langchain.com` (US), `https://eu.smith.langchain.com` (EU)
- **Auth:** Header `x-api-key: ${LANGSMITH_API_KEY}`. Project routing via optional header `Langsmith-Project: ${LANGSMITH_PROJECT}` (otherwise traces land in the `default` project).
- **Required env vars:** `LANGSMITH_API_KEY`. Optional: `LANGSMITH_ENDPOINT` (default `https://api.smith.langchain.com`), `LANGSMITH_PROJECT`.
- **Install:** Relevant `openinference-instrumentation-*` packages plus `opentelemetry-exporter-otlp-proto-http==1.43.0`. The `langsmith` PyPI package is **not** required for the OTLP path observent generates — install it only if you also want to use the `langsmith` SDK directly (datasets, evals).
- **Sources:** LangSmith docs — https://docs.smith.langchain.com · OTel ingest endpoint — https://docs.smith.langchain.com/observability/how_to_guides/trace_with_opentelemetry · LangSmith regions & endpoints — https://docs.smith.langchain.com/administration/concepts#data-regions

**Canonical setup (pure OTLP):**
```python
import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from openinference.instrumentation.langchain import LangChainInstrumentor

base = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com").rstrip("/")
headers = {"x-api-key": os.environ["LANGSMITH_API_KEY"]}
if project := os.getenv("LANGSMITH_PROJECT"):
    headers["Langsmith-Project"] = project

exporter = OTLPSpanExporter(endpoint=f"{base}/otel/v1/traces", headers=headers)
provider = TracerProvider(resource=Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", "my-agent-app")}))
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

LangChainInstrumentor().instrument(tracer_provider=provider)
```

LangSmith is cloud-first and has no localhost default — `LANGSMITH_API_KEY` must be set or the exporter will receive 401s.

### Opik

- **Type:** Open-source (Comet). Free self-host via Docker (Apache-2.0), or Opik Cloud at `https://www.comet.com`. Unlike LangSmith, the self-host edition is fully free — so observent *can* provision it locally.
- **Integration mechanism:** **Pure OTLP HTTP** to Opik's OTel ingest endpoint. Opik maps OTel-GenAI semantic conventions to its native trace schema, so the same `OTLPSpanExporter` + OpenInference framework instrumentor stack used for SigNoz / LangSmith works unchanged. No `opik` SDK code is generated — keeping Opik mechanically identical to SigNoz means it composes cleanly into the multi-backend fan-out template.
- **Endpoints:**
  - Self-host OTLP: `http://localhost:5173/api/v1/private/otel/v1/traces`
  - Cloud OTLP: `https://www.comet.com/opik/api/v1/private/otel/v1/traces`
  - Self-host UI: `http://localhost:5173` · Cloud UI: `https://www.comet.com/opik`
- **Auth:** Self-host requires no auth by default (single-user local). Opik Cloud needs header `Authorization: ${OPIK_API_KEY}` + `Comet-Workspace: ${OPIK_WORKSPACE}`; project routing via optional header `projectName: ${OPIK_PROJECT_NAME}` (otherwise traces land in the `Default Project`).
- **Required env vars:** Self-host: `OPIK_URL_OVERRIDE=http://localhost:5173/api`. Cloud: `OPIK_API_KEY`, `OPIK_WORKSPACE` (plus `OPIK_URL_OVERRIDE=https://www.comet.com/opik/api`). Optional: `OPIK_PROJECT_NAME`. The OTLP traces endpoint is `${OPIK_URL_OVERRIDE}/v1/private/otel/v1/traces`.
- **Install:** Relevant `openinference-instrumentation-*` packages plus `opentelemetry-exporter-otlp-proto-http==1.43.0`. The `opik` PyPI package is **not** required for the OTLP path observent generates — install it only if you also want to use the `opik` SDK directly (datasets, evals, the `@track` decorator).
- **Sources:** Opik docs — https://www.comet.com/docs/opik/ · OTel integration — https://www.comet.com/docs/opik/tracing/opentelemetry/overview · Self-host — https://www.comet.com/docs/opik/self-host/local_deployment

**Canonical setup (pure OTLP):**
```python
import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from openinference.instrumentation.langchain import LangChainInstrumentor

base = os.getenv("OPIK_URL_OVERRIDE", "https://www.comet.com/opik/api").rstrip("/")
headers = {}
if api_key := os.getenv("OPIK_API_KEY"):  # cloud only; self-host needs no auth
    headers["Authorization"] = api_key
if workspace := os.getenv("OPIK_WORKSPACE"):
    headers["Comet-Workspace"] = workspace
if project := os.getenv("OPIK_PROJECT_NAME"):
    headers["projectName"] = project

exporter = OTLPSpanExporter(endpoint=f"{base}/v1/private/otel/v1/traces", headers=headers)
provider = TracerProvider(resource=Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", "my-agent-app")}))
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

LangChainInstrumentor().instrument(tracer_provider=provider)
```

For self-host, set `OPIK_URL_OVERRIDE=http://localhost:5173/api` and leave the auth env vars unset; for Opik Cloud, `OPIK_API_KEY` + `OPIK_WORKSPACE` must be set or the exporter receives 401s.

### Jaeger

- **Type:** Open-source (CNCF graduated). **Self-host only** — there is no Jaeger SaaS. Trivially provisioned as a single all-in-one container.
- **Integration mechanism:** **Pure OTLP HTTP** to Jaeger's built-in OTLP receiver. Jaeger ingests OTLP natively (v2 by default; v1 all-in-one needs `COLLECTOR_OTLP_ENABLED=true`) and stores/visualizes the spans generically — it has **no LLM-specific UI**, so `gen_ai.*` attributes show up as ordinary span tags. The same `OTLPSpanExporter` + OpenInference framework instrumentor stack used for SigNoz works unchanged. No Jaeger SDK exists or is generated — mechanically identical to SigNoz, so it composes cleanly into the multi-backend fan-out template.
- **Endpoints:**
  - Self-host OTLP HTTP: `http://localhost:4318/v1/traces` (gRPC on `:4317`)
  - Self-host UI: `http://localhost:16686`
- **Auth:** None (local service).
- **Required env vars:** `JAEGER_ENDPOINT` (default `http://localhost:4318/v1/traces`). No keys.
- **Install:** `opentelemetry-exporter-otlp-proto-http==1.43.0` plus the relevant `openinference-instrumentation-*` packages. Jaeger itself is a Docker image, not a pip dependency — nothing to add to `requirements.txt`.
- **Sources:** Jaeger docs — https://www.jaegertracing.io/docs/ · OTLP ingestion — https://www.jaegertracing.io/docs/latest/apis/#opentelemetry-protocol · all-in-one image — https://hub.docker.com/r/jaegertracing/jaeger

**Canonical setup (pure OTLP):**
```python
import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from openinference.instrumentation.langchain import LangChainInstrumentor

endpoint = os.getenv("JAEGER_ENDPOINT", "http://localhost:4318/v1/traces")
exporter = OTLPSpanExporter(endpoint=endpoint)  # no auth for a local Jaeger
provider = TracerProvider(resource=Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", "my-agent-app")}))
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

LangChainInstrumentor().instrument(tracer_provider=provider)
```

Jaeger is a generic trace store/UI — great for a fast, dependency-free local span view. For LLM-cost/token dashboards use Phoenix/Langfuse/SigNoz instead; Jaeger shows the same spans, just without GenAI-aware panels.

---

## Per-Framework Reference

### LangGraph (`langgraph`)

- **Tracing model:** LangChain callback system + standard OTel via `LangChainInstrumentor`.
- **Key entry points:** `StateGraph.compile()` → `.invoke()`, `.stream()`, `.astream()`.
- **Where to thread `session_id`:** `RunnableConfig.configurable["session_id"]` and as OTel baggage.
- **Phoenix / SigNoz:** `pip install 'openinference-instrumentation-langchain==0.1.67'` then call `LangChainInstrumentor().instrument(tracer_provider=provider)`.
- **Langfuse:** `langfuse.langchain.CallbackHandler` passed via `config={"callbacks": [handler]}`.
- **Sources:** LangGraph docs — https://langchain-ai.github.io/langgraph/ · `openinference-instrumentation-langchain` — https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-langchain · Langfuse LangChain callback — https://langfuse.com/docs/integrations/langchain

### CrewAI (`crewai`)

- **Tracing model:** Native CrewAI events + LangChain callbacks for the underlying LLM calls.
- **Key entry points:** `Crew.kickoff()`, `Agent`, `Task` (delegations create child spans).
- **Where to thread `session_id`:** Pass via `inputs` dict and set OTel baggage at the top.
- **Phoenix / SigNoz:** `pip install 'openinference-instrumentation-crewai==1.1.10' 'openinference-instrumentation-langchain==0.1.67'` then:

  **Canonical setup snippet:**
  ```python
  from openinference.instrumentation.crewai import CrewAIInstrumentor
  CrewAIInstrumentor().instrument(tracer_provider=provider, use_event_listener=True)
  ```
  Captures Crew → Agent → Task → LLM hierarchy.
- **Langfuse:** Use `langfuse.langchain.CallbackHandler` — CrewAI's LLM wrapper inherits LangChain callbacks.
- **⚠️ `use_event_listener=True` is required to capture LLM spans.** The instrumentor's default (`use_event_listener=False`) only wraps `Crew.kickoff`/`Task._execute_core`/`Agent.kickoff`/`Flow.kickoff`/`BaseTool.run` — there is **no LLM-call wrapper anywhere in that path**, so it cannot produce an `llm`-kind span regardless of which LLM class CrewAI is configured with (`crewai.LLM`, LangChain's `ChatOpenAI`, anything). CrewAI ≥1.10 fires LLM calls through its internal event bus rather than a directly-wrappable method, so `use_event_listener=True` is the *only* path that emits LLM spans — it subscribes an `OpenInferenceEventListener` to Crew/Task/Agent/LiteAgent/Tool/Flow/Method events **and** `LLMCallStarted`/`LLMCallCompleted`/`LLMCallFailed` events, replacing the wrapper-based hierarchy rather than layering on top of it. Omitting the flag silently drops every LLM span while Crew/Task/Agent spans still show up, making the trace look deceptively complete — worth raising upstream that `use_event_listener=True` should be the instrumentor's own default.
- **⚠️ Known readability limitation — CrewAI's native span names are not human-meaningful.** CrewAI's own instrumentor names spans `Crew_<uuid>.kickoff` (embeds the Crew's per-run UUID — different every run for what is logically "the same" operation) and generic constants like `Task Execution`, `Flow Execution`, `Environment Context`, `Crew Created` (identical across every agent/run, giving no hint which query/service they belong to without opening `input.value`). These are **upstream CrewAI names** — the skill neither generates nor can rename them. Only observent's own root span (the `open_or_enrich_span` fallback, `capture.md § Public entry point`) is nameable, so set `_SERVICE_NAME` per service (`text2sql.run`, …) to give at least the top of each trace a stable, legible name; the CrewAI subtree stays generic.
- **⚠️ Non-primitive attribute warning (`crew_context`).** CrewAI may attach a `CrewContext` object to a span attribute, triggering `Invalid type CrewContext for attribute 'crew_context' value. Expected one of ['bool','str','bytes','int','float']…` from the OTel SDK. It's a benign upstream warning (the attribute is dropped, the span is otherwise fine) — observent's own capture coerces non-primitives to `str` via `_coerce` before `set_attribute`, so nothing observent generates emits it; the warning originates in CrewAI's instrumentor. Ignore it, or filter the OTel `logging` warning.
- **⚠️ CrewAI's built-in product telemetry leaks into your backend — disable it.** CrewAI ships anonymous usage telemetry (`crewai/telemetry/telemetry.py`) that normally pings `telemetry.crewai.com`. It starts its spans on the **global** tracer (`trace.get_tracer("crewai.telemetry")`) and, in `Telemetry.set_tracer()`, if a real (non-`ProxyTracerProvider`) global provider is already installed it **skips installing its own and piggybacks on the existing one**. observent's `init_observability()` sets exactly such a global provider before any Crew is built, so CrewAI's usage pings — spans named `Crew Created`, `Task Created`, `Task Execution`, `Flow Execution` — get exported to Phoenix/Langfuse alongside your real spans. `Task Execution` is the worst: it mirrors the real task's duration and sits next to the genuine OpenInference `Task`/`Agent`/`LLM` spans, so the trace looks like it has duplicated/conflicting timing. **Fix:** set `CREWAI_DISABLE_TELEMETRY=true` in the environment **before the first `crewai` import** (the flag is read when CrewAI constructs its `Telemetry` singleton). `CREWAI_DISABLE_TRACKING=true` is honored too; do **not** use `OTEL_SDK_DISABLED=true` — it would also disable *your* tracing. observent's Step 1.4d emits this into the generated `.env`/`.env.example` by default. See § Silencing frameworks' built-in vendor telemetry.
- **⚠️ Flow span ordering can look inconsistent (needs-investigation).** With CrewAI **Flows**, the `Flow Execution` / step span tree sometimes appears out of sequence in the waterfall from run to run (a reported-but-not-yet-root-caused symptom). If you hit it, it is almost always a **context-propagation** issue rather than a capture bug — check the § "Trace tree is broken / orphan spans" list (async `create_task` context, `start_as_current_span` vs `start_span`, thread `attach`/`detach`), since Flow steps may run on tasks/threads that don't inherit the parent context. Reproduce against a Flow example before changing generated code; observent's own capture doesn't reorder spans.
- **Sources:** CrewAI docs — https://docs.crewai.com · `openinference-instrumentation-crewai` — https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-crewai · `openinference-instrumentation-langchain` (underlying LLM calls) — https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-langchain

### Microsoft Agent Framework (`agent-framework`)

- **Tracing model:** Native OpenTelemetry emission built into `agent-framework`. The framework's spans land on the global `TracerProvider` automatically — just register the provider before constructing any `Agent`. Underlying model calls captured by `OpenAIInstrumentor` (or `AnthropicInstrumentor` for Anthropic-backed agents).
- **Key entry points:** `Agent.run()`, `agent_framework.openai.OpenAIChatClient`, the workflow primitives (sequential, concurrent, handoff, group collaboration) under `agent_framework.workflows`.
- **Where to thread `session_id`:** OTel baggage at the top — MAF's native context propagation carries it across agents and tool calls.
- **Phoenix / SigNoz / Langfuse / LangSmith / Opik / Jaeger via OTLP:** `pip install 'agent-framework==1.10.0' 'openinference-instrumentation-openai==0.1.52'` — MAF emits OTel-GenAI spans natively; the OI instrumentor adds raw model spans.
- **Note:** observent no longer supports AutoGen (v0.2 `pyautogen` or v0.4 `autogen-agentchat`) — Microsoft has unified AutoGen and Semantic Kernel into agent-framework. Migrate AutoGen code to MAF, or use the **Custom** path.
- **Sources:** Microsoft Agent Framework — https://github.com/microsoft/agent-framework · MAF observability guidance — search "Observability" / "OpenTelemetry" in the repo README · `openinference-instrumentation-openai` (raw model spans) — https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-openai

### Anthropic Agents SDK (`anthropic`)

- **Tracing model:** Wrap entry points with the OpenInference Anthropic instrumentor or with Langfuse `@observe` decorators.
- **Key entry points:** `client.messages.create()`, `client.beta.messages.create()`, agent tool-call loops.
- **Where to thread `session_id`:** Set OTel baggage at the top of each conversation turn.
- **Phoenix / SigNoz:** `pip install 'openinference-instrumentation-anthropic==1.0.6'` — captures `prompt_token_count`, `completion_token_count`, **prompt cache read/write tokens**, tool calls.
- **Langfuse:** `@observe(as_type="generation")` and update via `langfuse_context.update_current_observation(usage={...})`.
- **Sources:** Anthropic agents docs — https://docs.anthropic.com/en/docs/agents · `openinference-instrumentation-anthropic` — https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-anthropic · Anthropic prompt caching — https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching

### OpenAI Agents SDK (`openai-agents`)

- **Tracing model:** **Native** — the SDK has its own tracing pipeline configurable via `set_trace_processors()`. This captures handoffs, guardrails, and agent runs as first-class spans, not as raw OpenAI API calls.
- **Key entry points:** `Runner.run()`, `Agent`, `handoff()`, `Guardrail`.
- **Where to thread `session_id`:** Pass via `Runner.run(... metadata={"session.id": ...})`; use OTel baggage as fallback.
- **Phoenix:** `pip install 'openinference-instrumentation-openai-agents==1.6.1'` then:
  ```python
  from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor
  OpenAIAgentsInstrumentor().instrument(tracer_provider=provider)
  ```
- **Langfuse:** Use Langfuse's openai-agents processor (consult Langfuse docs for the current package name) registered via `set_trace_processors([...])`.
- **SigNoz:** Use the same OpenInference instrumentor; the OTLP exporter delivers spans to SigNoz.
- **Do NOT** use plain `openinference-instrumentation-openai` for the Agents SDK — it captures only the underlying HTTP calls and loses agent structure (handoffs, runs, guardrails).
- **Sources:** OpenAI Agents Python — https://openai.github.io/openai-agents-python/ · `set_trace_processors` API — https://openai.github.io/openai-agents-python/tracing/ · `openinference-instrumentation-openai-agents` — https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-openai-agents

### smolagents (`smolagents`)

- **Tracing model:** `openinference-instrumentation-smolagents` covers `CodeAgent.run()`, `ToolCallingAgent.run()`, tool calls, LLM calls.
- **Phoenix / SigNoz / Langfuse:** Same instrumentor — only the exporter destination changes.
- **Install:** `pip install 'openinference-instrumentation-smolagents==0.1.32'`
- **Sources:** smolagents docs — https://huggingface.co/docs/smolagents · `openinference-instrumentation-smolagents` — https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-smolagents

### LlamaIndex (`llama_index`)

- **Tracing model:** `openinference-instrumentation-llama-index` (preferred) or LlamaIndex's `set_global_handler()` API.
- **Key entry points:** `Workflow.run()`, `QueryEngine.query()`, `RetrieverQueryEngine.query()`, `AgentWorker.run_step()`.
- **Phoenix / SigNoz:** `pip install 'openinference-instrumentation-llama-index==4.4.3'`
- **Langfuse:** `from langfuse.llama_index import LlamaIndexCallbackHandler` then `Settings.callback_manager = CallbackManager([handler])`.
- **Sources:** LlamaIndex docs — https://docs.llamaindex.ai · `openinference-instrumentation-llama-index` — https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-llama-index · Langfuse LlamaIndex integration — https://langfuse.com/docs/integrations/llama-index

### Google ADK (`google.adk`)

- **Tracing model:** `openinference-instrumentation-google-adk` wraps the Agent Development Kit's runner and agent execution — captures `Runner.run()` / `Runner.run_async()`, agent invocations, tool calls, and the underlying model (Gemini / LiteLLM) requests as a connected span tree. ADK also emits some native OpenTelemetry spans; the OI instrumentor adds the LLM-specific attributes Phoenix and the OTel-GenAI backends read.
- **Key entry points:** `google.adk.agents.Agent` / `LlmAgent`, `google.adk.runners.Runner` (`run`, `run_async`), tool functions and `google.adk.tools.*`.
- **Where to thread `session_id`:** ADK's own `Session` (`session_service.create_session(...)`) carries an id end-to-end; also set OTel baggage (`session.id`) at the top of the turn so it lands on every span.
- **Phoenix / SigNoz / Langfuse / Elastic APM / LangSmith / Opik / Jaeger:** `pip install 'google-adk==2.3.0' 'openinference-instrumentation-google-adk==0.1.17'` then:
  ```python
  from openinference.instrumentation.google_adk import GoogleADKInstrumentor
  GoogleADKInstrumentor().instrument(tracer_provider=provider)
  ```
  Only the exporter destination changes across backends; the instrumentor is identical.
- **⚠️ Known instrumentor limitation — provider attribution is wrong for non-Gemini ADK agents.** When an ADK agent runs a **non-Google** model through `google.adk.models.lite_llm.LiteLlm` (e.g. OpenRouter / Together / Groq via LiteLLM), the instrumentor still hardcodes `llm.provider: "google"`, `gen_ai.system: "gcp.vertex.agent"`, and the `gcp.vertex.agent.*` attribute namespace — it never inspects the `LiteLlm` model string to correct attribution (though it *does* capture the real model name in `llm.model_name` / `gen_ai.request.model`, e.g. `openrouter/...`). Net effect: filtering or grouping a trace UI by **provider/system** buckets these calls under "google" even though nothing touched GCP/Vertex. **Don't trust `llm.provider` / `gen_ai.system` for LiteLLM-backed ADK agents** — group by `llm.model_name` instead. (Worth raising upstream: derive `llm.provider` from the `LiteLlm` model-string prefix rather than hardcoding `google`.)
- **Sources:** Google ADK docs — https://google.github.io/adk-docs/ · `openinference-instrumentation-google-adk` — https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk

### Custom (no framework)

- **Tracing model:** Manual OTel spans. The skill writes an `observent_otel.py` helper module into the user's project with typed setters: `set_llm_attrs(span, model, input_messages, output_messages, prompt_tokens, completion_tokens, ...)`, `set_tool_attrs(span, name, parameters, input_value, output_value)`, `set_agent_attrs(span, name, role)`.
- **Pattern:** wrap each agent step in `tracer.start_as_current_span("agent.step", attributes={"openinference.span.kind": "AGENT", ...})`.
- **Sources:** OTel Python SDK — https://opentelemetry.io/docs/languages/python/ · OpenInference span kinds — https://github.com/Arize-ai/openinference/blob/main/spec/semantic_conventions.md · OTel-GenAI operation names — https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-spans.md

---

## Mandatory Span Attributes

### Convention resolution

The convention emitted by generated code is fixed by the backend set chosen in `../SKILL.md` Step 3 — **no override**:

| Backend set | Convention | Reference doc |
|---|---|---|
| `{phoenix}` | **OI only** | `openinference.md` |
| Any non-empty subset of `{langfuse, signoz, elastic-apm, langsmith, opik, jaeger}` (no Phoenix) | **OTel-GenAI only** | `otel_genai.md` |
| Any set containing Phoenix **and** at least one of `{langfuse, signoz, elastic-apm, langsmith, opik, jaeger}` | **Both** | `openinference.md` + `otel_genai.md` |

Rationale: Phoenix is OpenInference-native; Langfuse, SigNoz, Elastic APM, LangSmith, Opik, and Jaeger consume OTel-GenAI (SigNoz / Elastic / LangSmith / Opik / Jaeger treat OI keys as opaque attributes — no LLM-specific UI affordances on those backends). Dual-emission is reserved for fan-out cases where both communities are present on the same provider.

### Per-kind summary (quick scan)

For complete attribute lists with types and flattening rules, read `openinference.md` (OI) and `otel_genai.md` (OTel-GenAI). The table below gives you the equivalents at a glance — pick the column that matches the resolved convention.

| Span kind | OI keys | OTel-GenAI keys |
|---|---|---|
| LLM | `openinference.span.kind="LLM"`, `llm.model_name`, `llm.provider`, `llm.invocation_parameters`, `llm.input_messages.<i>.message.*`, `llm.output_messages.<i>.message.*`, `llm.token_count.{prompt,completion,total,prompt_details.cache_read,prompt_details.cache_write}`, `llm.tools`, `llm.finish_reasons` | `gen_ai.operation.name="chat"`, `gen_ai.request.model`, `gen_ai.provider.name`, `gen_ai.request.{temperature,max_tokens,top_p,stop_sequences}`, `gen_ai.usage.{input_tokens,output_tokens,cache_creation.input_tokens,cache_read.input_tokens}`, `gen_ai.response.{model,finish_reasons,id}`, opt-in: `gen_ai.input.messages`, `gen_ai.output.messages` |
| TOOL | `openinference.span.kind="TOOL"`, `tool.name`, `tool.description`, `tool.parameters` | `gen_ai.operation.name="execute_tool"`, opt-in: `gen_ai.tool.definitions` |
| AGENT | `openinference.span.kind="AGENT"`, `agent.name`, `agent.role`, `agent.framework` | `gen_ai.operation.name="invoke_agent"`, `gen_ai.agent.{id,name,version,description}` |
| CHAIN | `openinference.span.kind="CHAIN"` | `gen_ai.operation.name="invoke_workflow"` |
| RETRIEVER | `openinference.span.kind="RETRIEVER"`, `retrieval.documents.<i>.document.{id,content,score,metadata}` | `gen_ai.operation.name="retrieval"`, `gen_ai.data_source.id`, opt-in: `gen_ai.retrieval.documents`, `gen_ai.retrieval.query.text` |

Generic `input.value` / `input.mime_type` / `output.value` / `output.mime_type` are OI-only and useful on every span kind for at-a-glance UI inspection. OTel-GenAI uses structured opt-in content attributes instead.

**Sources:** OI keys → `openinference.md` (canonical) + https://github.com/Arize-ai/openinference/blob/main/spec/semantic_conventions.md · OTel-GenAI keys → `otel_genai.md` (canonical) + https://github.com/open-telemetry/semantic-conventions/tree/main/docs/gen-ai

**LLM token-tracking gotcha (OpenAI Chat Completions vs Responses).** The two OpenAI text endpoints return usage under different field names — Chat Completions: `usage.{prompt_tokens, completion_tokens, total_tokens}`; Responses API: `usage.{input_tokens, output_tokens, total_tokens}`. The OpenInference instrumentor normalizes both into the OI / OTel-GenAI keys above, but only on versions that support the Responses API — check the changelog if a single agent mixes both endpoints. **Streaming + Chat Completions** silently omits usage unless the request passes `stream_options={"include_usage": True}`; the Responses API includes usage automatically. Without the opt-in, `llm.token_count.*` / `gen_ai.usage.*` will be missing on streaming spans. See `openinference.md` § Token counts and `otel_genai.md` § Token usage for the field-name mapping table.

### Cross-cutting (Baggage)

`session.id`, `user.id`, `tenant.id`, `app.version` set once at the entry point and promoted to span attributes via `BaggageSpanProcessor`. These keys are convention-neutral.

### Cost computation

Token counts are captured but **dollar cost** is computed at ingestion time by the backends from a model→price table. Verify the model attribute (`llm.model_name` for OI, `gen_ai.request.model` for OTel-GenAI) is set to a name the backend recognizes — otherwise cost columns show `$0` in the UI. Self-hosted Langfuse and SigNoz allow custom model price configs.

---

## Context Propagation

Multi-agent traces only work if context flows correctly across every boundary.

**Standard.** All wire-level context propagation in observent uses OTel SDK defaults, which implement **W3C Trace Context Level 1** (`traceparent` + `tracestate` per https://www.w3.org/TR/trace-context/) plus W3C Baggage (`baggage` header). The OI / OTel-GenAI semantic conventions govern *span attributes*; W3C TC governs the *cross-process context wire format* — the two are orthogonal. **Never call `set_global_textmap()`** with a non-W3C propagator (legacy B3, Jaeger `uber-trace-id`, etc.) — observent's exporters and all 5 backends assume W3C `traceparent` / `tracestate` on the wire. If interop with a B3-only service is required, use `CompositePropagator([TraceContextTextMapPropagator(), B3Format(), W3CBaggagePropagator()])` so W3C remains primary.

**Sources:** W3C Trace Context — https://www.w3.org/TR/trace-context/ · OTel context API (Python) — https://opentelemetry.io/docs/languages/python/instrumentation/#context-propagation · `BaggageSpanProcessor` (PyPI `opentelemetry-processor-baggage`) — https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/processor/opentelemetry-processor-baggage · AI-boundary input/output capture (transport-agnostic) — see `capture.md`

### Sync execution

`tracer.start_as_current_span()` uses `contextvars.ContextVar` under the hood — context is automatic. **Never** use the lower-level `start_span()` unless you also call `trace.use_span(span, end_on_exit=True)`.

### Async execution

Python 3.11+ inherits `Context` automatically across `asyncio.create_task` (PEP 654 / contextvars). For **older Python** (< 3.11), wrap manually:

```python
import contextvars

def _spawn_with_context(coro):
    ctx = contextvars.copy_context()
    return asyncio.create_task(coro, context=ctx)
```

### Threads / subprocesses

For `concurrent.futures.ThreadPoolExecutor`:

```python
from opentelemetry import context as otel_context

def worker(ctx, payload):
    token = otel_context.attach(ctx)
    try:
        return do_work(payload)
    finally:
        otel_context.detach(token)

ctx = otel_context.get_current()
executor.submit(worker, ctx, payload)
```

For subprocesses, propagate the W3C `traceparent` via env var:

```python
from opentelemetry.propagate import inject

env = os.environ.copy()
inject(env)  # adds traceparent + tracestate (W3C TC §3.2 / §3.3)
subprocess.run([...], env=env)
```

The child process loads it via `from opentelemetry.propagate import extract; extract(os.environ)`.

**Windows note.** Env-var keys are case-insensitive at the Win32 layer but case-sensitive in Python's `os.environ` dict. If the parent inherited `TRACEPARENT` (uppercase) from an upstream caller, `os.environ.copy() + inject(env)` will leave both `TRACEPARENT` and `traceparent` in the dict; on Win32 the OS collapses them and the surviving casing is implementation-defined. To avoid silent loss, normalize before spawning — `env.pop("TRACEPARENT", None); env.pop("TRACESTATE", None)` before `inject(env)`. The W3C HTTP binding (§3) is case-insensitive for headers; that does **not** extend to OS env vars.

### Cross-service / cross-agent network calls

Install `opentelemetry-instrumentation-httpx` and `opentelemetry-instrumentation-requests`. Initialize once:

```python
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

HTTPXClientInstrumentor().instrument()
RequestsInstrumentor().instrument()
```

Outgoing HTTP requests will carry W3C `traceparent` (TC §3.2) and `tracestate` (TC §3.3) headers automatically, so a downstream agent service can resume the trace. **Do not strip `tracestate`** in any custom outbound wrapper — downstream vendors (LangSmith, Elastic, SigNoz) may add list-member entries to it for vendor-specific routing per W3C TC §3.3.1.3.

**Inject-only (no outbound span) — the default for multi-agent apps.** `HTTPXClientInstrumentor().instrument()` bundles two things: header injection **and** a span per httpx request. In a multi-agent app the *meaningful* LLM/tool spans are already produced by the framework instrumentor (CrewAI/ADK/LangChain), so the httpx-level span is pure noise — a bare `POST` with no route/attributes that duplicates the real LLM call one level up (and the same for A2A card-resolver `GET`s). When you want propagation but **not** the span, inject on a shared client instead of instrumenting httpx globally:

```python
import httpx
from opentelemetry.propagate import inject

class _PropagatingTransport(httpx.AsyncHTTPTransport):
    async def handle_async_request(self, request):
        inject(request.headers)  # W3C traceparent/tracestate, no span opened
        return await super().handle_async_request(request)

client = httpx.AsyncClient(transport=_PropagatingTransport())
# equivalently: httpx.AsyncClient(event_hooks={"request": [lambda r: inject(r.headers)]})
```

This is the outbound twin of `capture.md § HTTP transport spans` (`http_transport_spans: none`): keep context flowing, drop the redundant transport span. Use the full `HTTPXClientInstrumentor` only when you genuinely want a span per outbound call (e.g. calling an un-instrumented third-party HTTP API that produces no span of its own). Same `tracestate` rule applies — `inject()` preserves it.

**Sampling-flag note.** When an upstream caller sends `traceparent` with the `sampled` bit (TC §3.2.2.5) cleared, OTel's default `ParentBased(ALWAYS_ON)` sampler propagates the bit unchanged downstream. If you replace the global sampler, keep it parent-aware so cross-service trace integrity holds.

### AI-boundary input/output capture (any transport)

observent captures the input/output that crosses the **AI-system boundary** — the prompt, request state, run config, and result — as `input.*` / `output.*` attributes on the agent run's existing root span, and sets the run's status (OK / ERROR). This is **transport-agnostic**: it works identically whether the agent is triggered by HTTP, a CLI, a queue worker, or a script, because it enriches whatever span is already recording (the framework instrumentor's root, or the HTTP server span) rather than opening its own. Sensitive keys are redacted at the value level; a baggage whitelist promotes correlation keys onto child spans.

When the raw HTTP wire payload is *also* needed (a header or envelope field the agent never receives as an argument), an **optional** ASGI adapter enriches the existing server span with `http.request.*` / `http.response.*` — it adds no span and does not buffer streaming responses. See **`references/capture.md`** for the canonical engine, the per-framework wrap points, the redaction key list, and the optional HTTP adapter.

### Agent handoffs

- **OpenAI Agents SDK** — handoffs are first-class trace events when using `set_trace_processors()`. No manual work.
- **Microsoft Agent Framework** — MAF's native OTel integration captures workflow-level agent handoffs and tool dispatch as first-class spans. Register a global `TracerProvider` before any `Agent(...)` construction; the framework attaches to it automatically.
- **CrewAI** — Task delegation creates parent/child spans automatically via `openinference-instrumentation-crewai`.
- **LangGraph** — Each node transition becomes a span automatically via `LangChainInstrumentor`.
- **Custom** — Use a `with_agent_context` helper to attach agent identity:

```python
from contextlib import contextmanager
from opentelemetry import trace, baggage

@contextmanager
def with_agent_context(name: str, role: str = "", framework: str = "custom"):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(f"agent.{name}") as span:
        span.set_attribute("openinference.span.kind", "AGENT")
        span.set_attribute("agent.name", name)
        span.set_attribute("agent.role", role)
        span.set_attribute("agent.framework", framework)
        yield span
```

### Baggage (cross-cutting attributes)

Set once at the entry point; flows through async/thread/subprocess/HTTP boundaries automatically:

```python
from opentelemetry import baggage, context

ctx = baggage.set_baggage("session.id", session_id)
ctx = baggage.set_baggage("user.id", user_id, context=ctx)
ctx = baggage.set_baggage("app.version", "1.4.2", context=ctx)
token = context.attach(ctx)
try:
    run_agent(user_input)
finally:
    context.detach(token)
```

To turn baggage into span attributes (so they appear in the UI), add `BaggageSpanProcessor`:

```python
from opentelemetry.processor.baggage import BaggageSpanProcessor, ALLOW_ALL_BAGGAGE_KEYS
provider.add_span_processor(BaggageSpanProcessor(ALLOW_ALL_BAGGAGE_KEYS))
```

### Opaque-loop / vendor-runtime correlation

Context propagation needs code running *inside* the agent. That is impossible for a **vendor runtime you don't control** — Claude Code, Cursor's composer — whose loop runs in a process you can't instrument and never emits `traceparent`. You cannot stitch those calls into one trace.

What you **can** do is group them. The only seam you share with such a runtime is the **LLM gateway** every call flows through (a litellm proxy, Portkey, OpenRouter, …). Instrument that boundary and stamp a stable correlation id — injected at invocation (Claude Code's `ANTHROPIC_CUSTOM_HEADERS`, recovered from the proxy's request headers) — onto each call as `session.id` (OI) / `gen_ai.conversation.id` (OTel-GenAI). The backend's session/conversation view then collapses a run's calls into one group. This is **grouping, not a single `trace_id`**, and it sees only egress LLM calls (not the runtime's internal tool/sub-agent spans) — but it recovers the run-level linkage that per-call gateway logs lose. Canonical engine + the litellm reference adapter: **`references/gateway.md`**. When the runtime instead reaches *your* tools over MCP, the in-process counterpart is the `mcp_session_id` baggage key in `references/capture.md § Baggage promotion`.

---

## Multi-Backend Fan-Out

Send the same spans to multiple backends simultaneously by attaching one `BatchSpanProcessor` per backend to a single `TracerProvider`:

**Sources:** `BatchSpanProcessor` configuration — https://opentelemetry.io/docs/languages/python/instrumentation/#configure-the-exporters · per-backend endpoint and auth details — see § Per-Backend Reference above.

```python
import os, base64
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Resource — carry service.name AND (when Phoenix is in the set) the project
# routing key. register() is NOT used here, so PHOENIX_PROJECT_NAME must be folded
# into the resource as openinference.project.name or traces land in Phoenix's
# `default` project. See § Arize Phoenix note.
_res_attrs = {"service.name": "fanout-app"}
if _phx_project := os.getenv("PHOENIX_PROJECT_NAME"):
    _res_attrs["openinference.project.name"] = _phx_project
provider = TracerProvider(resource=Resource.create(_res_attrs))

# Phoenix
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
    endpoint=os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces"),
    headers={"Authorization": f"Bearer {os.environ['PHOENIX_API_KEY']}"} if os.getenv("PHOENIX_API_KEY") else {},
)))

# Langfuse
_lf_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com").rstrip("/")
_lf_auth = base64.b64encode(f"{os.environ['LANGFUSE_PUBLIC_KEY']}:{os.environ['LANGFUSE_SECRET_KEY']}".encode()).decode()
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
_op_base = os.getenv("OPIK_URL_OVERRIDE", "https://www.comet.com/opik/api").rstrip("/")
_op_headers = {}
if os.getenv("OPIK_API_KEY"):
    _op_headers["Authorization"] = os.environ["OPIK_API_KEY"]
if os.getenv("OPIK_WORKSPACE"):
    _op_headers["Comet-Workspace"] = os.environ["OPIK_WORKSPACE"]
if os.getenv("OPIK_PROJECT_NAME"):
    _op_headers["projectName"] = os.environ["OPIK_PROJECT_NAME"]
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
    endpoint=f"{_op_base}/v1/private/otel/v1/traces",
    headers=_op_headers,
)))

# Jaeger — local OTLP receiver, no auth.
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
    endpoint=os.getenv("JAEGER_ENDPOINT", "http://localhost:4318/v1/traces"),
)))

trace.set_tracer_provider(provider)

# Elastic APM — native agent. Picks up the same OTel spans via its bridge,
# no BatchSpanProcessor entry needed. Auto-instruments Flask/Django/FastAPI/etc.
import elasticapm
elasticapm.Client(service_name=os.getenv("ELASTIC_APM_SERVICE_NAME", "fanout-app"))
elasticapm.instrument()
```

Each processor / agent exports independently. If one backend is unreachable, the others still receive spans.

**Convention for fan-out:** when the backend set contains Phoenix **and** at least one of Langfuse / SigNoz / Elastic APM / LangSmith / Opik / Jaeger, the convention resolves to `both` (see § Mandatory Span Attributes) — every span must carry OI **and** OTel-GenAI keys so each backend's UI lights up. For Phoenix-less fan-out (e.g. `langfuse,signoz` or `signoz,elastic-apm` or `langsmith,jaeger`), `otel-genai` alone is sufficient.

---

## OpenInference Instrumentor Map

| Package | Covers |
|---|---|
| `openinference-instrumentation-langchain` | LangGraph, LangChain, CrewAI underlying LLM calls |
| `openinference-instrumentation-crewai` | CrewAI Crew/Agent/Task structure |
| `openinference-instrumentation-openai` | OpenAI SDK, Microsoft Agent Framework (model client) |
| `openinference-instrumentation-openai-agents` | OpenAI Agents SDK (use this — not plain `-openai`) |
| `openinference-instrumentation-anthropic` | Anthropic SDK incl. prompt caching tokens |
| `openinference-instrumentation-llama-index` | LlamaIndex Workflows, QueryEngines, Retrievers |
| `openinference-instrumentation-smolagents` | smolagents CodeAgent/ToolCallingAgent |
| `openinference-instrumentation-google-adk` | Google ADK agents, runners, tools |
| `openinference-instrumentation-bedrock` | AWS Bedrock |
| `openinference-instrumentation-vertexai` | Google Vertex AI |

All are installable from PyPI. They emit OpenInference attributes natively — Phoenix consumes them directly. For Langfuse / SigNoz / Elastic APM / LangSmith / Opik / Jaeger exporters, the user-side code (the Custom path or wrapper code) must additionally emit OTel-GenAI keys per the resolution rule (`openinference.md` and `otel_genai.md`).

**Sources:** OpenInference Python monorepo (canonical) — https://github.com/Arize-ai/openinference/tree/main/python · per-package PyPI pages at `https://pypi.org/project/openinference-instrumentation-<framework>/`.

---

## Troubleshooting

**Sources:** symptoms catalogued here come from observent's own field experience — verify against each backend's official troubleshooting docs (linked in § Per-Backend Reference above) before changing this list.

### "No traces appearing"

1. Verify env vars actually loaded — print them at startup.
2. Force flush before exit: `provider.shutdown()` (OTel) or `langfuse.flush()` (Langfuse client). Add as `atexit` handler.
3. For Phoenix local — confirm UI is at `http://localhost:6006` and `px.launch_app()` was called.
4. For SigNoz self-host — confirm `docker compose ps` on the Foundry-generated compose shows the stack up and the OTLP receiver reachable on port 4318. Note the opamp settle: the collector reports `Healthy` (`:13133`) up to ~2 min before it actually serves OTLP (see `references/self_host.md § SigNoz`).
5. Corporate proxy? OTLP HTTP works through proxies; gRPC often does not.

### "Traces appear but token counts are missing"

Token counts come from the LLM response. The instrumentor extracts them from the API response. If using a custom LLM wrapper, verify it surfaces `usage.input_tokens` / `usage.output_tokens`. For manual span emission (Custom path), set them explicitly using the helper functions in `observent_otel.py`.

### "Cost shows $0"

Backends compute cost from `llm.model_name` lookups in their internal price table. If your model name is non-standard (e.g. an Azure deployment alias), set the canonical model name on the span and use `llm.invocation_parameters` for the deployment id.

### "Trace tree is broken / orphan spans"

Context propagation issue. Check:
- Async — using Python ≥ 3.11 or wrapping `create_task` with `copy_context`.
- Threads — using the `attach()`/`detach()` pattern.
- HTTP — `RequestsInstrumentor` / `HTTPXClientInstrumentor` enabled.
- Manual spans — using `start_as_current_span`, not `start_span`.

### "401 / authentication error"

- **Phoenix Cloud:** `PHOENIX_API_KEY` set.
- **Langfuse:** Public/secret keys not swapped; `LANGFUSE_HOST` matches the workspace where the keys were issued.
- **SigNoz Cloud:** `SIGNOZ_INGESTION_KEY` set; header name (`signoz-access-token`) matches current docs.
- **Elastic APM:** if your deployment uses an API key, set `ELASTIC_APM_API_KEY` (the agent sends `Authorization: ApiKey ...`); if it uses a secret token, set `ELASTIC_APM_SECRET_TOKEN` (the agent sends `Authorization: Bearer ...`). Don't set both. `ELASTIC_APM_SERVER_URL` should NOT have a trailing slash.

### "Elastic APM agent silent / no transactions in Kibana"

- The native agent only flushes on shutdown by default. Make sure your app calls `client.close()` or relies on `atexit`.
- Confirm the APM Server URL is reachable: `curl $ELASTIC_APM_SERVER_URL` should return a small JSON manifest, not 404.
- If you're using the OTLP path instead of the native agent, the endpoint is `<server>/v1/traces` (not `/intake/v2/events`).

### "OpenAI Agents SDK shows raw HTTP calls instead of agent spans"

You're using `openinference-instrumentation-openai`. Switch to `openinference-instrumentation-openai-agents` and register via `set_trace_processors()`.

### "Unexplained `<library>.*` spans I never instrumented"

A dependency ships its **own** OpenTelemetry instrumentation that was dormant until you installed `opentelemetry-sdk` — see § Known auto-instrumenting dependencies below. Set that library's documented gate env var to `false` to silence it.

### "Junk spans like `Crew Created` / `Task Execution` / `Flow Execution` I never created"

Your **framework** is emitting its own built-in product telemetry onto the global provider observent installed — see § Silencing frameworks' built-in vendor telemetry. For CrewAI, set `CREWAI_DISABLE_TELEMETRY=true` before the first `crewai` import.

---

## Known auto-instrumenting dependencies

Some third-party libraries ship **their own** OpenTelemetry instrumentation that is *dormant only because `opentelemetry` isn't importable yet*. The moment you `pip install opentelemetry-sdk` (which observent does), that instrumentation wakes up and emits **library-internal** spans to whatever global `TracerProvider` is registered — with **no** code from observent or from you. This is easy to miss: nothing you wrote produced the spans, and `detect_framework.py` / `existing_setup.py` only scan *your* code, not a dependency's built-in decorators.

`detect_framework.py` carries a small known-list (source of truth: `scripts/observent_matrix.py` `KNOWN_AUTO_INSTRUMENTING_DEPS`) and reports any present dep under `auto_instrumenting_deps` in its JSON, with the env var that gates it. SKILL.md Phase 1 § 1.4b then offers **keep** (add the dep's internal spans) or **disable** (set the gate to `false` for a trace focused on your agent/LLM spans).

| Dependency | Ships instrumentation for | Gate env var | Default |
|---|---|---|---|
| `a2a-sdk` | its own server/handlers/event-queue/client transports — spans like `a2a.server.*` (`JsonRpcDispatcher`, `DefaultRequestHandler*`, `EventQueueSource`, …), built from `@trace_class`/`@trace_function` decorators in `a2a/utils/telemetry.py` | `OTEL_INSTRUMENTATION_A2A_SDK_ENABLED` | `true` (enabled) |

To add a dependency here: append an `AutoInstrumentingDep(...)` to `KNOWN_AUTO_INSTRUMENTING_DEPS` in `scripts/observent_matrix.py` (slug, display, probe modules, gate env var, default) and add a row above. Only list libraries with a **documented** on/off env var — an undocumented internal flag is not a stable gate.

---

## Silencing frameworks' built-in vendor telemetry

**Distinct from the section above.** Auto-instrumenting *dependencies* ship dormant OTel instrumentation that `opentelemetry-sdk` wakes up. This section is about *frameworks* that ship their own **product telemetry** — anonymous usage pings normally sent to the vendor's own collector. Nothing is dormant: the framework's telemetry client checks for an existing real (non-`ProxyTracerProvider`) **global** `TracerProvider` and, finding one, **skips installing its own collector and emits onto the existing global provider instead**.

The moment observent's `init_observability()` installs a real global provider (which it must — the instrumentors need it, and it happens before any agent is built), the vendor's private usage pings get **redirected into the user's backend**. So enabling observent is what causes the leak: without a global provider those spans would quietly go to the vendor's servers. This is a **general pattern** — any framework that emits its own telemetry against the global provider will leak the same way.

`detect_framework.py` carries a small known-list (source of truth: `scripts/observent_matrix.py` `KNOWN_VENDOR_TELEMETRY`) and reports any **detected framework** that has an entry under `framework_vendor_telemetry` in its JSON, with the disable flag. SKILL.md Phase 1 § 1.4d then offers **disable** (default — set the flag) or **keep**, emitting the flag into the generated `.env`/`.env.example` on disable.

| Framework | Built-in telemetry (leaked span names) | Disable flag | Default |
|---|---|---|---|
| CrewAI | anonymous usage pings from `crewai/telemetry/telemetry.py` (python version, cpu count, platform, `crew_number_of_tasks`, `crew_number_of_agents`, …) — spans named `Crew Created`, `Task Created`, `Task Execution`, `Flow Execution` | `CREWAI_DISABLE_TELEMETRY=true` (also honors `CREWAI_DISABLE_TRACKING=true`) | enabled (leaks) |

**Timing.** The disable flag is read when the framework first constructs its telemetry singleton — i.e. at first import. It must be set **before** the framework is imported: a `.env` loaded via `load_dotenv()` at the top of the entrypoint (before importing the framework) works; setting it at the process/shell level is bulletproof. Do **not** reach for `OTEL_SDK_DISABLED=true` to silence one framework — it disables *all* OTel, including the user's own tracing.

To add a framework here: append a `VendorTelemetry(...)` to `KNOWN_VENDOR_TELEMETRY` in `scripts/observent_matrix.py` (framework slug matching a `FRAMEWORKS` entry, display, disable env var, disable value, leaked span names) and add a row above. Only list frameworks with a **documented** disable flag.
