---
name: observent
description: Sets up observability for multi-agent Python applications. Detects the agent framework (LangGraph, CrewAI, Microsoft Agent Framework, Anthropic Agents SDK, OpenAI Agents SDK, smolagents, LlamaIndex, Google ADK, or no framework / Custom) and wires up the chosen backend (Arize Phoenix, Langfuse, SigNoz, Elastic APM, LangSmith, Opik, or Jaeger) with integration code, span attributes following OpenInference and OTel GenAI semantic conventions, context propagation, and validation. Invoke when the user asks to add tracing, monitoring, observability, telemetry, or LLM monitoring to their agent app, or mentions Arize, Phoenix, Langfuse, SigNoz, Elastic APM, LangSmith, Opik, Comet, Jaeger, LangChain tracing, OpenTelemetry, OpenInference, OTel GenAI, span hierarchy, token tracking, or agent handoff visibility. Also invoke for the optional Evaluate step when the user asks to set up evals, a regression gate, or a CI cost/latency/token gate for their agent.
argument-hint: "[framework] [backend|backend,backend,...]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# observent — Multi-Agent Observability

You are an expert in Agent & LLM observability, OpenTelemetry, and multi-agent instrumentation. Your job: produce three artifacts under `.observent/` in the user's project, then execute the task list.

**Backends supported (exactly 7):** Arize Phoenix · Langfuse · SigNoz · Elastic APM · LangSmith · Opik · Jaeger.
**Frameworks supported (9):** LangGraph · CrewAI · Microsoft Agent Framework (`agent-framework`) · Anthropic Agents SDK · OpenAI Agents SDK · smolagents · LlamaIndex · Google ADK · Custom.

## Lifecycle

```
.observent/spec.md     →    .observent/plan.md     →    .observent/tasks.json     →    user files
   (what & why)              (how, with content)         (checkpoint, mutable)         (executed)
```

Four phases — Spec, Plan, Tasks, Implement — described below. The artifacts are fingerprinted: downstream regenerates when upstream changes. `tasks.json` doubles as the session checkpoint; any task with status `pending` or `failed` means the workflow is incomplete and you should offer to resume.

**Canonical schema reference:** `references/spec_schema.md`. Construct and validate the three artifacts strictly against the shapes documented there. This SKILL.md describes the *workflow*; `spec_schema.md` is the contract.

---

## On every invocation — resume check first

Before doing anything else:

1. Read `.observent/tasks.json` if it exists.
2. If any task has status `pending` or `failed`, prompt the user:
   `Found incomplete observent run. Resume from task <id> (<kind>)? (yes / restart / abort)`
   - `yes` → jump to the Implement phase from the first non-terminal task.
   - `restart` → delete `.observent/{spec.md, plan.md, tasks.json}` and start fresh from the Spec phase.
   - `abort` → exit without changes.
3. If `tasks.json` is absent or all tasks are terminal (`done` / `skipped`), check upstream drift (§ Drift detection) and run the lifecycle from the earliest phase whose artifact is missing or stale.

If invoked with `$1`/`$2` args, capture them as the user's framework/backend preferences and proceed into the Spec phase; they override prior choices and invalidate downstream fingerprints.

---

## Phase 1 — Spec

**Goal:** produce `.observent/spec.md` capturing what to set up and why. Locks once the user confirms the choices.

### Step 1.1 — Detect environment

Run both detectors **in parallel** — they're independent deterministic scripts that emit JSON, so issue them as two Bash tool calls in a **single message**, not sequentially. Both scripts ship in this skill's own `scripts/` directory (beside `SKILL.md`); resolve that directory to an absolute path (see note below) and run:

- `python "<skill-dir>/scripts/detect_framework.py"`
- `python "<skill-dir>/scripts/existing_setup.py"`

> **Resolving `<skill-dir>`.** `<skill-dir>` is the folder this `SKILL.md` was loaded from — its `scripts/` and `references/` subfolders ship *inside* the skill, so the path is always relative to the skill, never to the user's project cwd.
> - **In Claude Code**, substitute the built-in `${CLAUDE_SKILL_DIR}` variable — e.g. `python "${CLAUDE_SKILL_DIR}/scripts/detect_framework.py"`. (This is the only place that variable applies; it resolves automatically.)
> - **Every other agent** (Cursor, Copilot, Codex, Cline, Windsurf, …) receives the same self-contained folder via `npx skills` and has **no** `${CLAUDE_SKILL_DIR}` variable. Use the absolute path of the skill folder you loaded `SKILL.md` from — the exact directory varies by agent (project-level `.agents/skills/observent/` for many CLIs; a global dir such as `~/.cursor/skills/observent/`, `~/.codeium/windsurf/skills/observent/`, or `~/.config/<agent>/skills/observent/` when installed with `-g`). Same `scripts/` + `references/` layout either way.

Do **not** wrap either script in a subagent — they're already deterministic; an LLM in the middle adds latency and nondeterminism without saving context. The JSON output goes straight into `spec.detection`. `detect_framework.py` also reports a `docker` block (`{available, compose_available}`) — capture it into `spec.detection.docker_available` / `docker_compose_available` for the provisioning offer in Step 1.6 — plus `package_manager` (`uv` | `poetry` | `pipenv` | `pip` | null, from lockfile/manifest presence — capture into `spec.detection.package_manager`; Step 2.1 uses it to emit the install command in the right syntax and Phase 3 uses it for the dependency dry-run) and `google_adk_lite_llm_detected` (capture into `spec.detection.google_adk_lite_llm_detected`; see Step 1.2 bullet 6).

For `existing_setup.py`: treat entries with `kind: "backend"` (Phoenix / Langfuse / SigNoz) and non-empty `imports` or `env_vars_in_files` as existing observability. Entries with `kind: "instrumentation"` alone don't count — they may belong to an unrelated tracing setup. Each entry's `instrumentation_code_found` (derived from non-empty `imports`) is the code-vs-config discriminator; the report's top-level `scaffold_only` flags the case where config exists but no entry has code — see Step 1.4.

### Step 1.2 — Resolve framework

1. If the user passed a framework as `$1` (`langgraph` / `crewai` / `microsoft-agent-framework` / `anthropic-agents` / `openai-agents` / `smolagents` / `llama-index` / `google-adk` / `custom`), use it.
2. Else if exactly one framework is detected, confirm it in one short sentence.
3. Else if multiple are detected, ask which one to instrument.
3b. **Multi-service monorepo.** If **multiple frameworks are detected** AND there are **multiple plausible entry points** (several `server.py` / `main.py` / `app.py`-shaped files under different subpackages or service directories), do **not** force a single pick under bullet 3. Offer the multi-service path instead: `Detected N services on M frameworks (e.g. text2sql→crewai, deepresearch→langgraph). Instrument all N services (each gets its own entry-point wiring, sharing one observent_capture.py) or just one? (all / <service-name>)`. On `all`, record each under `spec.choice.services: [{name, framework, entry_point}]` and omit `choice.framework` (see `references/spec_schema.md § Multi-service specs`). On a single pick, set `choice.framework` as in bullet 3. If only one framework is detected, or only one plausible entry point exists, keep the single-framework flow.
4. If `autogen` / `autogen_agentchat` / `pyautogen` is detected, inform the user that AutoGen has been superseded by **Microsoft Agent Framework** (`microsoft-agent-framework`) — Microsoft's unification of AutoGen and Semantic Kernel — and observent no longer supports AutoGen. Offer MAF, or the **Custom** path if they need to keep their existing AutoGen code.
5. If none detected, ask; "none / writing from scratch" → **Custom** path.
6. If the resolved framework is `google-adk` and `detect_framework.py` reports `google_adk_lite_llm_detected: true`, proactively warn: `This project routes Google ADK through google.adk.models.lite_llm to a non-Google model backend. openinference-instrumentation-google-adk unconditionally sets llm.provider="google" / gen_ai.system="gcp.vertex.agent" regardless of the real backend (the true model name is still correct in llm.model_name / gen_ai.request.model). Group/filter by model name, not provider, when analyzing these spans — see matrix.md § Google ADK.` This is informational only — no choice to record, no confirm gate.

### Step 1.3 — Resolve backend(s) and convention

`$2` accepts one or more backends, comma-separated (e.g. `phoenix` or `phoenix,langsmith`). If `$2` was passed, parse into a deduplicated set. Otherwise present these seven with one-line trade-offs and ask the user to pick one or more:

- **Arize Phoenix** — local-first, no account needed (`px.launch_app()`), OpenTelemetry-native, best dev-loop UX.
- **Langfuse** — open-source self-hostable; best token cost tracking, prompt versioning, eval datasets.
- **SigNoz** — full-stack APM (traces + metrics + logs); best when you want LLM observability alongside infra metrics in a self-hostable OTel stack.
- **Elastic APM** — Elastic Stack APM Server with the native `elastic-apm` agent; best when you also need transaction tracing and infra metrics in Kibana alongside LLM tracing.
- **LangSmith** — LangChain's hosted observability platform (US + EU cloud, enterprise self-host); best when you're already on LangGraph/LangChain. Pure OTLP HTTP; OTel-GenAI conventions on the wire.
- **Opik** — Comet's open-source LLM observability platform; free self-hostable via Docker (or Opik Cloud). Pure OTLP HTTP; OTel-GenAI conventions on the wire — mechanically identical to SigNoz/LangSmith, so it composes cleanly into the multi-backend fan-out.
- **Jaeger** — the CNCF open-source distributed-tracing system; trivially self-hostable (single all-in-one container), ingests OTLP directly. Best for a lightweight, dependency-free local trace view (no LLM-specific UI; spans + `gen_ai.*` attributes shown generically). Pure OTLP HTTP; OTel-GenAI conventions on the wire.

**Derive the convention mechanically** from the resolved backend set (do not ask the user):

| Backend set | Convention |
|---|---|
| `{phoenix}` | `oi` (OpenInference only — Phoenix-native UI) |
| Any non-empty subset of `{langfuse, signoz, elastic-apm, langsmith, opik, jaeger}` (no Phoenix) | `otel-genai` |
| Any set containing Phoenix **and** at least one of `{langfuse, signoz, elastic-apm, langsmith, opik, jaeger}` | `both` |

State the resolved convention in one short sentence (e.g. "Resolved: phoenix,elastic-apm → emitting both OI and OTel-GenAI attributes").

### Step 1.4 — Existing-setup decision

If Step 1.1 found pre-existing observability config:

- If `existing_setup.py` reports `scaffold_only: true` (env-var names/config from an earlier incomplete attempt, but every detected entry has `instrumentation_code_found: false` — no instrumentation code was ever written), name this case explicitly instead of forcing Extend/Replace: ask `Found observability config (env-var names) from an earlier incomplete attempt, but no instrumentation code. Set up fresh, keeping the existing env-var names? (scaffold_only / replace / abort)`. On `scaffold_only`, generate as if clean but reuse the detected env-var names instead of introducing new ones.
- Otherwise ask explicitly:
  - **Extend** — keep their existing setup, add observent attributes/instrumentors on top.
  - **Replace** — overwrite with observent's recommended pattern.
  - **Abort** — exit without changes.

Never overwrite without asking, even when auto-invoked. Store the choice in `spec.choice.existing_setup_decision`. Once locked it is **not re-prompted on resume**; to change it the user re-runs `/observent-spec`.

### Step 1.4b — Dormant dependency instrumentation

If Step 1.1's `detect_framework.py` output has a non-empty `auto_instrumenting_deps` list, one or more installed dependencies ship their **own** OpenTelemetry instrumentation that is dormant only because `opentelemetry` isn't importable yet — the moment observent's `pip install opentelemetry-sdk` lands, it wakes up and emits library-internal spans (e.g. `a2a-sdk`'s `a2a.server.*` spans) to the global TracerProvider, with **no** code from observent or the user. For **each** detected dep, ask:

`<display> ships its own OpenTelemetry instrumentation that will activate once opentelemetry-sdk is installed. Keep it enabled (adds <slug>-internal spans) or disable it (<ENV_VAR>=false) for a cleaner trace focused on your agent/LLM spans? (keep / disable)`

Record each decision under `spec.choice.auto_instrumenting_deps.<slug>` (`keep` | `disable`). On `disable`, Phase 2 appends `<ENV_VAR>=false` to the generated `.env` (names+values for these gates are safe — they're booleans, not secrets). `keep` writes nothing. See `references/matrix.md § Known auto-instrumenting dependencies`. Same `confirm` discipline as every other choice; a missing/empty list skips this step entirely.

### Step 1.4c — HTTP transport spans (web-served agents)

Only when `detection.web_frameworks` is non-empty (the agent is served over HTTP). The web-framework/ASGI instrumentor bundles trace-context extraction (essential) with a server span + per-request transport spans (often just noise — a streaming/SSE endpoint emits an `http send` span *per chunk*). Set `spec.choice.http_transport_spans` with a **backend-dependent default**, then let the user override:

- Backend set is **LLM-native only** (subset of `{phoenix, langfuse, opik, langsmith}`) → default **`none`** (drop the instrumentor; a context-only middleware preserves linkage, the capture root is the single clean span).
- Set contains **any APM backend** (`{signoz, elastic-apm, jaeger}`) → default **`root-only`** (keep the one server span so their HTTP transaction/service-map/RED-metric dashboards still populate; suppress transport children). **Warn** that `none` would leave those APM dashboards without a data source.

State the default in one line and offer `none` / `root-only` / `full`. Record in `spec.choice.http_transport_spans`. See `references/capture.md § HTTP transport spans`.

### Step 1.4d — Framework built-in vendor telemetry

If Step 1.1's `detect_framework.py` output has a non-empty `framework_vendor_telemetry` list, a detected **framework** ships its own built-in *product* telemetry (anonymous usage pings) that normally goes to the vendor's own collector — but it piggybacks on the **global** `TracerProvider`. observent installs exactly such a provider in `init_observability()` before any agent is built, so those usage-ping spans get **redirected into the user's backend** (e.g. CrewAI's `Crew Created` / `Task Created` / `Task Execution` / `Flow Execution` spans landing in Phoenix/Langfuse). This is a **different mechanism** from Step 1.4b (which is a *dependency's* dormant OTel instrumentation woken by `opentelemetry-sdk`); here nothing is dormant — the vendor's telemetry actively finds and reuses the global provider. For **each** entry, ask:

`<display> ships built-in product telemetry that will piggyback on observent's tracer and leak usage-ping spans (<span_names>) into your backend. Disable it (<disable_env_var>=<disable_value>) or keep it? (disable / keep)`

Default to **disable** — these are the vendor's private usage pings, not agent/LLM detail, and `Task Execution` duplicates the real work's timing right next to the genuine spans, making a trace look like it has conflicting timing. Record each decision under `spec.choice.framework_vendor_telemetry.<slug>` (`disable` | `keep`). On `disable`, Phase 2 appends `<disable_env_var>=<disable_value>` to the generated `.env` **and** `.env.example` (a boolean gate, not a secret), with a comment explaining the piggyback mechanism. **Timing caveat — surface it in the comment:** the flag is read when the framework first constructs its telemetry singleton (at first import), so it must be present *before* the framework is imported; a `.env` loaded via `load_dotenv()` at the top of the entrypoint (before importing the framework) satisfies this, and setting it at the process/shell level is bulletproof. `keep` writes nothing. See `references/matrix.md § Silencing frameworks' built-in vendor telemetry`. Same `confirm` discipline as every other choice; a missing/empty list skips this step entirely.

### Step 1.5 — Local provisioning offer

For each backend whose resolved `endpoints.<backend>.mode == self-host`, probe the endpoint and record reachability in `spec.detection.backends_reachable.<backend>`. When a self-host backend is **unreachable**:

- **Backend ∈ {phoenix, langfuse, signoz, elastic-apm, opik, jaeger} and Docker available** (`detection.docker_available && detection.docker_compose_available`): ask
  `<backend> isn't reachable at <url>. Provision it locally with Docker? (yes / no, I'll start it myself / skip)`.
  On `yes` set `spec.choice.self_host_provision.<backend> = true`; otherwise `false`.
- **Docker not available**: state that and skip the offer (set `false`). For Phoenix, mention the `px.launch_app()` in-process alternative. The final `validate` will still report the backend as unreachable.
- **Backend == langsmith**: never offer Docker — surface the enterprise-license note from `references/self_host.md § LangSmith` and keep it cloud-first. `self_host_provision` gets no `langsmith` key.
- **Backend provisioned via a vendor CLI** (`method: vendor-cli-generated`, currently **SigNoz** — see `references/self_host.md § Provisioning method per backend`): its provisioning **also installs a local binary** (e.g. Foundry's `foundryctl`), not just `docker compose`. Call this out in the offer — `Provisioning <backend> also installs the <CLI> CLI locally (checksum-verified GitHub release). OK to install it? (yes / no)` — and record it so Phase 2 emits the dedicated `installs_cli` `confirm` gate (`references/spec_schema.md § tasks.json`). Never install the CLI silently.
- **Cross-backend port collisions:** before committing the provision set, check the **newly-selected** backends against `references/self_host.md § Port-conflict matrix` (not just against already-running services). Phoenix's `4327` gRPC remap is baked in; a Jaeger + SigNoz pair still both bind host `4318`, so surface a remap (and the adjusted `*_ENDPOINT`) in the Phase 2 plan / Phase 3 diff rather than letting the second `docker compose up` fail with `port is already allocated`.

Templates and pinned image tags are **not** decided here — they live in `references/self_host.md` and are materialized in Phase 2. This step only records the decision. Reachable backends and cloud-mode backends get no `self_host_provision` entry.

### Step 1.6 — Write `.observent/spec.md`

Construct the YAML frontmatter per `references/spec_schema.md § 1`. Compute `detection.project_fingerprint` from `pyproject.toml` + `requirements*.txt` + `poetry.lock` (see schema for exact ordering). Write the file; set `status: locked` once the user has confirmed the choices in Steps 1.2–1.5. Preserve any existing prose body on re-runs.

---

## Phase 2 — Plan

**Goal:** read `.observent/spec.md` and produce `.observent/plan.md` with the full generated content embedded in fenced blocks behind anchor comments. Deterministic from spec — no user questions in this phase except the diff-preview confirm in Phase 4.

### Step 2.1 — Decide structure

Using `references/matrix.md` (sections **Per-framework** and **Per-backend**), determine:

- **Files to generate** — typically:
  - `observent_otel.py` (always — backend init + framework instrumentation).
  - `observent_capture.py` (always — transport-agnostic input/output/status capture at the AI boundary; see `references/capture.md`).
  - `observent_http.py` (only if `spec.choice.http_body_capture: true` — optional raw HTTP body/header capture; enriches the existing server span, adds no span).
  - `observent_eval.py` (only if the user opts into the Phase 5 eval gate — the no-op-in-prod span collector from `references/eval.md`; wired into `observent_otel.py` via `install_eval_collector(provider)`).
  - Edits to the user's entry-point file (e.g., `main.py`) to import `observent_otel`, wrap the agent invocation with `capture_run`, and (if applicable) register the HTTP middleware.
  - `.env.example` append with required env var names and notify user to fill in with exact values.
  - **Multi-service (`spec.choice.services` present):** generate one entry-point edit per service (each importing `observent_otel` and wrapping its boundary with `open_or_enrich_span(..., agent_name=<service.name>, agent_framework=<service.framework>)`), sharing a single `observent_capture.py` and a single processor list across all services — see `references/spec_schema.md § Multi-service specs`. The OpenAI Agents SDK special-case below and the `_FRAMEWORK`-literal guidance in Step 2.2 apply per-service rather than once, since each service passes its own `agent_framework=` per-call instead of relying on one global `_FRAMEWORK` literal.
- **Multi-backend processor list** — one `BatchSpanProcessor(OTLPSpanExporter(...))` per OTLP backend in `spec.choice.backends` (Phoenix, Langfuse, SigNoz, LangSmith, Opik, Jaeger). Elastic APM in native-agent mode is **not** a processor — set `elastic_apm_native_agent: true` and instantiate `elasticapm.Client(...)` + `elasticapm.instrument()` next to the TracerProvider.
- **OpenAI Agents SDK** — if `spec.choice.framework == openai-agents`, set `openai_agents_native_processors: true` and use the SDK's native `set_trace_processors()` API, not `openinference-instrumentation-openai`. This is non-negotiable.
- **Install command** — copy exact `==X.Y.Z` pins from `references/matrix.md § Verified Versions`, rendered into the `pip_install` line in the detected manager's syntax from `spec.detection.package_manager`: `uv` → `uv add <pkg>==<ver> …` (updates `pyproject.toml` + `uv.lock`); `poetry` → `poetry add <pkg>==<ver> …` (updates `pyproject.toml` + `poetry.lock`); `pipenv` → `pipenv install <pkg>==<ver> …`; `pip` or `null` → `pip install <pkg>==<ver> …`. Prefer the manager's native add command over `pip install` so `pyproject.toml`/lockfiles don't silently drift out of sync.
- **Local provisioning** — for each backend with `spec.choice.self_host_provision.<backend> == true`, materialize the chosen stack from `references/self_host.md` into a `plan.provision[]` entry:
  - `method: vendored-compose` (Phoenix, Elastic APM, Jaeger) → add a `files[]` create entry for `docker-compose.observent-<backend>.yml`, copy the pinned compose template into a `<!-- plan:compose_<backend> -->` anchor, and set `up_command`/`down_command` to the `docker compose -f … up -d --wait` / `down` lines.
  - `method: upstream-clone` (Langfuse, Opik) → no compose file; set `up_command` to the pinned `git clone … && docker compose -f … up -d --wait` line from `self_host.md` (no `<!-- plan:compose_* -->` anchor).
  - `method: vendor-cli-generated` (SigNoz) → no compose anchor (the CLI generates the compose file). Emit these five ordered tasks (a `confirm` gate plus the four provisioning actions from `self_host.md § SigNoz`): (1) a `confirm` with `installs_cli` metadata → (2) `run_command` `cli_install_command` → (3) `write_file` for `cli_config_file` (content in the `<!-- plan:clicfg_<backend> -->` anchor) → (4) `run_command` `generate_command` → (5) `run_command` `up_command` on the generated `compose_file`. Set `compose_file` to the CLI-generated path (e.g. `pours/deployment/compose.yaml`).
  Copy image tags / CLI versions **verbatim** from `references/self_host.md § Image Versions` — never invent versions (for `vendor-cli-generated`, image tags are resolved by the CLI and **not** tracked; only the CLI/installer is pinned). When `self_host_provision` is empty, `plan.provision` is `[]`.

### Step 2.2 — Required pieces in every generated file

Every `observent_otel.py` template must include:

- **Backend init** — exporter / native client configured from env vars; never hard-code keys.
- **Framework instrumentation** — the right OpenInference instrumentor or native trace processor (see `references/matrix.md`).
- **Multi-agent attributes** on every agent/chain span, keyed by `spec.choice.convention` — **this must be generated, not just aspired to** (a fallback root that carries only `input.*`/`output.*` is a defect, see gap: agent identity silently omitted):
  - `oi`: `openinference.span.kind` (`AGENT` / `CHAIN` / `LLM` / `TOOL` / `RETRIEVER`), `agent.name`, `agent.role`, `agent.framework`.
  - `otel-genai`: `gen_ai.operation.name`, `gen_ai.agent.name`, `gen_ai.provider.name`.
  - `both`: emit the union.
  - **Enforcement:** the capture engine already stamps these on the run's root span via `_set_agent_identity` (`references/capture.md § Public entry point`). Fill its `_SERVICE_NAME` / `_AGENT_NAME` / `_AGENT_ROLE` / `_FRAMEWORK` generation-time literals from `spec.choice` (framework → `_FRAMEWORK`; a per-service name → `_SERVICE_NAME` / `_AGENT_NAME`), **or** pass `agent_name=` / `agent_role=` / `agent_framework=` at the `open_or_enrich_span` / `capture_run` wrap point. Do not leave the defaults generic when the identity is known. **Multi-service (`spec.choice.services`):** `_FRAMEWORK` is a single global literal and can't hold more than one framework — each service's wrap point must instead pass `agent_framework=<service.framework>` per-call (`references/capture.md`).
- **Phoenix project routing** (when `phoenix` ∈ `spec.choice.backends`) — read `PHOENIX_PROJECT_NAME` in **both** generation paths. The single-backend path uses `register(project_name=os.getenv("PHOENIX_PROJECT_NAME", ...))`; the manual multi-backend fan-out (`convention == "both"`) never calls `register()`, so it must fold the value into the resource as the `openinference.project.name` attribute (`Resource.create({"service.name": ..., "openinference.project.name": <PHOENIX_PROJECT_NAME>})`) or every trace silently lands in Phoenix's `default` project. See `references/matrix.md § Arize Phoenix`.
- **Baggage** for `session.id`, `user.id`, `tenant.id`, `app.version` at the entry point.
- **Flush-on-exit** — `provider.shutdown()` or `langfuse.flush()` via `atexit`.
- **OTLP HTTP** (not gRPC) for all OTLP backends.
- **Convention as a generation-time literal** — for the Custom path, write `_CONVENTION = "<oi|otel-genai|both>"` as a literal in `observent_otel.py`. Do **not** make it read an env var; convention is a generation-time decision.

### Step 2.3 — AI-boundary input/output/status capture

observent's prime directive is **never miss any input or output that crosses the AI-system boundary**, regardless of how the agent is triggered (HTTP, CLI, queue worker, cron, notebook). This capture is **transport-agnostic** and is generated for **every** framework — not just web apps.

- **Always** generate `observent_capture.py` from the canonical engine in `references/capture.md` and wrap the agent invocation with `capture_run` / `capture_run_async` (or call `enrich_current_span(...)` + `capture_output(...)` directly). See `references/capture.md § Per-framework wrap points` for where each framework's invoke call sits.
- **Enrich in place, never duplicate the root span.** The engine writes `input.*` / `output.*` / status onto the span that is **already recording** (the framework instrumentor's root span, or the HTTP server span). It opens its own fallback root span (named `f"{_SERVICE_NAME}.run"`, default `agent.run`) **only** when nothing is recording (e.g. a bare CLI), so input is never lost. Do not add a second observent root span when one already exists.
- **Root span always carries input AND output; the fallback root also carries agent identity.** Whichever span is the run root (enriched framework span or the fallback), it must end with both `input.*` and `output.*` set (never input-only). Identity attributes are stamped **always on the fallback** root (from the `_AGENT_NAME`/`_AGENT_ROLE`/`_FRAMEWORK` literals — fill these from `spec.choice`) and on an **enriched** framework root **only when `agent_name=`/`agent_role=` is passed explicitly** via `open_or_enrich_span(...)` (the engine won't blanket-overwrite a foreign span's identity with generic defaults). So when the framework already opens a root and you want that root to carry identity, wrap the boundary with `open_or_enrich_span(inputs, agent_name=…, agent_role=…)` directly rather than the bare `capture_run` decorator (which passes no identity and therefore only guarantees identity on the fallback root). `capture_run` / `capture_run_async` set input+output automatically; with `open_or_enrich_span` directly, pair it with `capture_output(result, span)`. Set `_SERVICE_NAME` per service so trace lists read `text2sql.run` / `deepresearch.run` rather than a wall of identical `agent.run`.
- **Span status is set at the AI boundary** by the engine: `StatusCode.OK` on success; `record_exception()` + `StatusCode.ERROR` + `error.type` on failure. Status no longer depends on whether a transport instrumentor happens to be present.
- Sensitive keys (auth credentials, session/CSRF, PII) are redacted at the value level (key preserved so the attribute shape is stable); a baggage whitelist promotes correlation keys onto child spans. Both are **generation-time literals** in the generated file — same rule as `_CONVENTION`. No truncation.
- **Optional raw HTTP capture** — only if `spec.choice.http_body_capture: true`, also generate `observent_http.py` (an ASGI middleware that enriches the **existing** server span with `http.request.*` / `http.response.*`; adds no span, does not buffer streaming responses). Generate this only when the agent's logical input — already captured by `capture_run` — is insufficient and the raw wire payload (a header/envelope field) is also needed.

### Step 2.4 — Context propagation rules

observent emits W3C-compliant context. Every template relies on the OTel SDK's default composite propagator (`TraceContextTextMapPropagator` + `W3CBaggagePropagator`).

- **Do not override the global propagator.** Never call `set_global_textmap()` with B3/Jaeger/custom — that breaks `traceparent` interop with every backend in the matrix.
- Use `tracer.start_as_current_span()` (never the raw `start_span`).
- Async: Python 3.11+ inherits context across `asyncio.create_task`. For older versions wrap with `contextvars.copy_context().run(...)`.
- Threads: `attach()`/`detach()` pattern (see `references/matrix.md § Context Propagation`).
- **HTTP transport spans (inbound)** — branch generated web instrumentation on `spec.choice.http_transport_spans` (see `references/capture.md § HTTP transport spans`): `full` → framework/ASGI instrumentor + transport spans; `root-only` → instrumentor with `exclude_spans=["receive","send"]` (use `OpenTelemetryMiddleware` directly for **Starlette**, which — unlike `FastAPIInstrumentor` — has no `exclude_spans` param); `none` → **no** instrumentor, generate the context-only `TraceContextMiddleware` (extract-only, one `http.error` span on early failure). **Guardrail:** whenever `none` drops the instrumentor, the context-only middleware MUST be generated, or cross-service linkage silently breaks.
- HTTP fan-out (outbound): default to **inject-only** propagation (a `_PropagatingTransport` / `event_hooks` on the shared client — headers only, no per-request span) for multi-agent apps where the framework instrumentor already produces the meaningful LLM/tool spans; use the full `opentelemetry-instrumentation-httpx` / `-requests` instrumentors only when a span per outbound call is genuinely wanted. See `references/matrix.md § Context Propagation § Cross-service / cross-agent network calls`.
- Subprocess fan-out: `opentelemetry.propagate.inject(env)` before `subprocess.run(env=env)`; child re-extracts with `extract(os.environ)`. On Windows, env var names are case-insensitive — read the exact case `inject` wrote (`traceparent`) or normalize.
- **Opaque vendor runtimes** (Claude Code, Cursor's composer) can't accept propagated context — their loop runs in a process you can't instrument. When such a runtime is in the pipeline and routes its calls through an LLM gateway (litellm proxy, …), *offer* the gateway-boundary recipe in `references/gateway.md`: instrument the proxy and stamp an injected correlation id (`session.id` / `gen_ai.conversation.id`) so the run's calls **group** in the backend. This is opt-in and diff-previewed like any write; generate it only when applicable — it is grouping, not a single trace, and never mandatory for a normal run.

### Step 2.5 — Endpoints

| Backend | Self-host | Cloud |
|---|---|---|
| Phoenix | OTLP `http://localhost:6006/v1/traces` | `https://app.phoenix.arize.com/v1/traces` (Bearer `PHOENIX_API_KEY`) |
| Langfuse | OTLP `http://localhost:3000/api/public/otel/v1/traces` | `https://us.cloud.langfuse.com/...` or `https://cloud.langfuse.com/...` (Basic from public+secret keys) |
| SigNoz | OTLP `http://localhost:4318/v1/traces` | `https://ingest.{us,eu,in}.signoz.cloud:443/v1/traces` (header `signoz-access-token`) |
| Elastic APM | APM Server `http://localhost:8200` (agent default) | `https://<deployment>.apm.<region>.cloud.es.io:443` (Bearer `ELASTIC_APM_SECRET_TOKEN` or ApiKey `ELASTIC_APM_API_KEY`) |
| LangSmith | OTLP `${LANGSMITH_ENDPOINT}/otel/v1/traces` (enterprise self-host) | `https://api.smith.langchain.com/otel/v1/traces` (US) or `https://eu.api.smith.langchain.com/otel/v1/traces` (EU) (header `x-api-key`) |
| Opik | OTLP `http://localhost:5173/api/v1/private/otel/v1/traces` (no auth) | `https://www.comet.com/opik/api/v1/private/otel/v1/traces` (headers `Authorization` + `Comet-Workspace`, optional `projectName`) |
| Jaeger | OTLP `http://localhost:4318/v1/traces` (no auth; `JAEGER_ENDPOINT`) | self-host only — no hosted Jaeger SaaS |

Default to self-host unless the user supplies cloud env vars. LangSmith is cloud-first — it has no localhost default. Jaeger is self-host only — there is no Jaeger SaaS.

### Step 2.6 — Write `.observent/plan.md`

Construct YAML frontmatter + anchored fenced blocks per `references/spec_schema.md § 2`. Set `spec_fingerprint` to sha256 of the live `spec.md` frontmatter. Each generated file's full content lives in exactly one fenced block; `tasks.json` will reference it via `plan#<slug>`.

---

## Phase 3 — Tasks

**Goal:** decompose `plan.md` into the ordered, mutable `.observent/tasks.json` checkpoint. No code generation here — content already lives in `plan.md`; tasks only reference it.

### Step 3.1 — Build the task array

Strict order:

1. `confirm` — render the diff preview from `plan.md`:
   - New files (paths + one-line purpose).
   - Modified files with their unified diffs.
   - **Install command** (in the detected manager's syntax — see § 2.1).
   - **Dependency-resolution diff** (guards against a stale pin silently downgrading an already-installed package). Do **not** treat the install command as a fait accompli. First run the detected manager's **non-mutating dry-run resolve**, from `spec.detection.package_manager`:
     - `uv` → `uv add --dry-run <pins>`
     - `poetry` → `poetry add --dry-run <pins>`
     - `pipenv` → `pipenv install <pins>` in a scratch check, or inspect `pipenv lock` output
     - `pip` → `pip install --dry-run --report - <pins>` (JSON report)

     These are all non-mutating (no lockfile/manifest is written). Read the resolver's planned actions and diff them against currently-installed versions. Render, per affected package: `install X.Y.Z` / `upgrade A→B` / **`⚠ DOWNGRADE A→B`**. **Any version change to a package that is NOT in observent's install set — most critically a downgrade — is a red flag:** a stale exact `==` pin in `matrix.md § Verified Versions` can force the resolver to backtrack an unrelated already-installed package (e.g. `crewai 1.15.1 → 1.6.1`) to satisfy both that pin and the project's own loose constraint, and `uv add` / `pip install` will exit **0** with no visible error. Surface every such change as its own `⚠ unexpected dependency change` line in the confirm.
   - Env vars grouped by backend (names only, never values).
   - Resolved convention.
   - **Generated-attribute checklist** (catches silent omissions before a task is marked done): `agent identity attributes: present / missing` (agent.name/role/framework or gen_ai.agent.* on the run root) and `root span input + output: present / missing`. If either is *missing*, fix the generated file before proceeding — don't confirm a file that drops these.
   - Backends and endpoints (one line each).
   - Any locally provisioned stacks: the compose file (`vendored-compose`) or clone target (`upstream-clone`) or CLI install + generated compose (`vendor-cli-generated`) and the `docker compose … up` command, one line each, from `plan.provision[]`. For `vendor-cli-generated`, show the `installs_cli` details (package · installer URL · trust basis) as their own line — the CLI install is a distinct consent surface from `docker compose up`.
   - Prompt: if the dependency-resolution diff found any unexpected change, `Apply these changes? (yes / adjust pins / abort)` — **abort is the recommended default** here, offering the user, one line each: (a) pin the affected package at its current version in the install command; (b) relax the one over-constraining observent pin (a targeted, single-package deviation surfaced in the diff — never a blanket `>=` sweep of the matrix); or (c) abort and report the conflicting pin so `matrix.md § Verified Versions` can be re-verified. With no unexpected changes: `Apply these changes? (yes / preview <file> / abort)`.
2. One `write_file` task per `files[].op == create` in `plan.files`, with `content_ref: "plan#<slug>"` (this includes any `vendored-compose` `docker-compose.observent-<backend>.yml` and any `vendor-cli-generated` `cli_config_file`).
3. One `edit_file` task per `files[].op == edit`, with `diff_ref: "plan#<slug>"`.
4. One `run_command` task for `pip_install` — the dependency dry-run diff above happens when the `confirm` task is rendered, before this task runs, so the install never executes before the user has seen the resolution diff.
5. Provisioning tasks per `plan.provision[]` entry, placed **after** pip-install and **before** `validate` so the endpoint is live when validation runs:
   - `vendored-compose` / `upstream-clone` → one `run_command` with `cmd` = that entry's `up_command` (`docker compose … up -d --wait`, or the pinned clone+up).
   - `vendor-cli-generated` → the ordered sequence: a `confirm` carrying `installs_cli` (must be approved before any binary is installed) → `run_command` `cli_install_command` → `write_file` `cli_config_file` → `run_command` `generate_command` → `run_command` `up_command`. See `references/spec_schema.md § tasks.json`.
6. One `validate` task — final — calling `<skill-dir>/scripts/validate_setup.py` (resolve `<skill-dir>` as in Step 1.1) with the comma-separated backend list from `spec.choice.backends`.

### Step 3.2 — Write `.observent/tasks.json`

Set `plan_fingerprint` to sha256 of the live `plan.md` frontmatter. All tasks start `status: pending`, `started_at: null`, `finished_at: null`, `error: null`. See `references/spec_schema.md § 3` for the exact JSON shape.

---

## Phase 4 — Implement

**Goal:** execute the task list, mutating `tasks.json` to disk after each task. This phase is fully resumable — re-entry picks up from the first non-terminal task.

### Step 4.1 — Execute tasks in array order

For each task whose status is not terminal (`done` / `skipped`):

| `kind` | Action | On success | On failure |
|---|---|---|---|
| `confirm` | Show `payload.prompt`; wait for user. | `yes` → `done`; `no`/`abort` → `skipped` (and halt the run on `abort`) | n/a |
| `write_file` | Resolve `content_ref` against `plan.md`; `Write` the file. | `done` | `failed` with short error |
| `edit_file` | Resolve `diff_ref` against `plan.md`; apply via `Edit`. | `done` | `failed` with short error |
| `run_command` | Run via Bash. | `done` if exit 0 | `failed` |
| `validate` | Run `<skill-dir>/scripts/validate_setup.py <backend-list>` via Bash (resolve `<skill-dir>` as in Step 1.1); surface output verbatim. | `done` if exit 0 | `failed`; suggest the likely cause (missing env var, unreachable endpoint, package not installed) |

After mutating any task: rewrite `tasks.json` to disk before moving to the next task. Set `started_at` when work begins, `finished_at` when it ends. On `failed`, the next invocation will offer to retry that task.

### Step 4.2 — Optional smoke test

If env vars are set and the user wants a live trace, offer to re-run `validate_setup.py` with `--smoke-test`. Each backend in the list gets its own synthetic span carrying that backend's preferred convention (OI for Phoenix, OTel-GenAI for Langfuse / SigNoz / Elastic APM / LangSmith / Opik / Jaeger). Phoenix / Langfuse / SigNoz / LangSmith / Opik / Jaeger use an `OTLPSpanExporter`; Elastic APM uses the native `elasticapm.Client` so the smoke test exercises the same agent path the generated app uses.

### Step 4.3 — Summary

Once all tasks are terminal, report back:

- Framework + backend(s) + resolved convention (`oi` / `otel-genai` / `both`).
- New files created and existing files modified (read from `plan.files`).
- `pip install` command (one line).
- Required env vars per backend (names only — user fills in values).
- UI URL per backend:
  - Phoenix local: `http://localhost:6006` · Cloud: `https://app.phoenix.arize.com`
  - Langfuse self-host: `http://localhost:3000` · Cloud: `https://cloud.langfuse.com` or `https://us.cloud.langfuse.com`
  - SigNoz self-host: `http://localhost:8080` (recent unified image; older releases `3301`) · Cloud: `https://<tenant>.{us,eu,in}.signoz.cloud`
  - Elastic APM self-host (Kibana): `http://localhost:5601/app/apm` · Cloud: `https://<deployment>.kb.<region>.cloud.es.io/app/apm`
  - LangSmith US: `https://smith.langchain.com` · EU: `https://eu.smith.langchain.com`
  - Opik self-host: `http://localhost:5173` · Cloud: `https://www.comet.com/opik`
  - Jaeger self-host: `http://localhost:16686` (self-host only)
- For any locally provisioned stack (from `plan.provision[]`): note that it's now running under Docker and give the matching `down_command` to stop it (e.g. `docker compose -f docker-compose.observent-phoenix.yml down`).
- Recommend running one real request through the app and confirming at least one `llm`-kind span (not just Crew/Task/Agent/Flow) appears in the backend UI — `validate_setup.py --smoke-test`'s synthetic span (Step 4.2) drives its own span, not the framework's real LLM call path, so it can't catch a framework whose instrumentor silently drops LLM spans. Call this out by name for **CrewAI** — its instrumentor requires `use_event_listener=True` to emit LLM spans at all (`matrix.md § CrewAI`).
- One-line next step — set the env vars, run the app, refresh each UI.

---

## Phase 5 — Evaluate (optional gate)

**Goal:** turn the telemetry observent already produces into a deterministic, **offline, zero-dependency CI quality gate**. This is an **opt-in 5th step** that runs *after* a working setup — the core lifecycle stays Spec→Plan→Tasks→Implement. Auto-invocation trigger: "set up evals / a regression gate / a CI cost (token / latency) gate for my agent." Canonical engine reference: `references/eval.md`.

The gate asserts budgets + behavior from a declarative `.observent/eval.json` against spans captured to a local file — **no backend required**. The deterministic floor is `scripts/eval_gate.py` (stdlib-only, like `validate_setup.py`); subjective answer-quality `judge.criteria` are delegated to you (the host agent), never scored by the script.

### Step 5.1 — Ensure the collector exists

Generate `observent_eval.py` from `references/eval.md § Generated collector` if absent, and wire `install_eval_collector(provider)` into `observent_otel.py`. Diff-preview before write, same gate as every generated file. It's a **no-op unless `OBSERVENT_EVAL=1`**, so it's safe in prod. It piggybacks on the existing provider with a `SimpleSpanProcessor` that writes each finished span (`span.to_json(indent=None)`) to `.observent/eval/spans.jsonl`.

### Step 5.2 — Ensure `.observent/eval.json` exists

If absent, run the agent once in eval mode (`OBSERVENT_EVAL=1`) to collect a first capture, then generate a starter `eval.json` (per `references/eval.md § eval.json schema`) with **conservative budgets seeded above the observed numbers** and `convention` read from `.observent/spec.md`. The user owns and commits this file — it's the team contract. It's a peer artifact to spec/plan/tasks; schema lives in `references/spec_schema.md § 4`.

### Step 5.3 — Collect → gate

1. Run the user's agent/tests with `OBSERVENT_EVAL=1` so spans land in `.observent/eval/spans.jsonl`.
2. Invoke `<skill-dir>/scripts/eval_gate.py --spec .observent/eval.json --spans .observent/eval/spans.jsonl [--baseline .observent/eval/baseline.json] [--format text|json|junit|html]` (resolve `<skill-dir>` as in Step 1.1). Exit 0 = pass, 1 = any violation — the CI contract.
3. Surface the report verbatim. On failure, name the violated check and the likely cause (a prompt/model/dep change that grew tokens or latency, a dropped tool call, a PII leak that escaped redaction). Optionally also write a shareable, self-contained HTML report the user can open anytime: re-run with `--format html > .observent/eval/report.html` (ASCII-safe, no external assets; exit code unchanged).
4. **Resolve `needs-agent` judge criteria** by reading the root-span `input.value` / `output.value` pairs from `spans.jsonl` and scoring each criterion, reported alongside the deterministic results. A CI run (`--fail-on-unjudged` absent) treats them as skipped.

### Step 5.4 — Baseline & gitignore

Seed/refresh `baseline.json` with `--update-baseline` (only when an increase is intended). Commit `baseline.json`; treat `.observent/eval/spans.jsonl` as ephemeral (gitignore it) — see `references/spec_schema.md § 6`.

---

## Optional MCP enrichment (implementation phase)

Everything above runs with **no MCP at all** — the bundled zero-dependency scripts (`detect_framework.py`, `existing_setup.py`, `validate_setup.py`) are the floor, and the skill must always work with just `Bash`. When the host agent *also* exposes one of the MCP servers below, use it as **progressive enhancement** to make Phase 4 stronger — never as a prerequisite.

**Rules for every MCP use (all agents):**

- **Optional + detected, never assumed.** Use an MCP only if the running agent actually exposes its tools. If it's absent, silently fall back to the documented script/Bash path — same task outcome, no error. The skill ships verbatim to 70+ agents via `npx skills`; most users will have none of these connected.
- **The fallback path stays canonical.** The MCP only *adds* confidence; the script path remains the source of truth for whether a task is `done` or `failed`. Never let a missing or failing MCP block a task.
- **Same confirm discipline.** Sending user code, traces, or environment to an external MCP is subject to the same diff-preview/confirm gate as a file write — never silently exfiltrate, and never pass secret *values*.
- **Claude Code:** add the relevant MCP tool names to this skill's `allowed-tools` frontmatter (or approve them at run time); other agents enable them via their own MCP config.

| MCP (any provider) | Lifecycle slot | What it adds over the script floor | Fallback when absent |
|---|---|---|---|
| **IDE / language-server** (e.g. `getDiagnostics`, in-kernel code execution) | after each `write_file` / `edit_file` in Phase 4 | Confirm the generated `observent_otel.py` / `observent_capture.py` actually imports and type-checks (correct instrumentor names, no missing symbols) before marking the task `done`; optionally run the validation span in-kernel | mark `done` on successful write; rely on the final `validate` task to surface runtime errors |
| **Observability-backend** (Phoenix / Langfuse / SigNoz / Datadog / Grafana query MCP) | Phase 4 `validate` task and § 4.2 smoke test | Confirm the synthetic span **actually landed** in the backend with the expected attributes (`llm.token_count.*`, the resolved convention keys) — closes the loop past mere endpoint reachability | `validate_setup.py <backends>` (env + reachability + span emission only) |
| **Container / Docker** | Phase 1 § 1.5 and each `plan.provision[]` `run_command` | Inspect container **health + logs** after `docker compose … up` (did the stack come up serving, or crash-loop?) rather than trusting the `--wait` exit code alone | the `docker compose … up -d --wait` exit code |

> Context7 (the library-docs MCP) is intentionally **not** in this table — it's an authoring/maintenance aid for refreshing the `references/` files, not part of instrumenting a user's project.

---

## Drift detection

Run these checks at the start of any phase (after the resume prompt):

| Compare | Stored in | Live source | Action on mismatch |
|---|---|---|---|
| Project deps | `spec.detection.project_fingerprint` | sha256 of `pyproject.toml` + `requirements*.txt` + `poetry.lock` (see `references/spec_schema.md § 1`) | Prompt: `Project deps changed since spec was written. Re-run /observent-spec? (yes / continue anyway / abort)` |
| Spec → Plan | `plan.spec_fingerprint` | sha256 of live `spec.md` frontmatter | Regenerate `plan.md` (forces tasks regeneration too) |
| Plan → Tasks | `tasks.plan_fingerprint` | sha256 of live `plan.md` frontmatter | Regenerate `tasks.json`, **but preserve** `status` for tasks whose `id` + `payload` are byte-identical to the prior version — so a re-plan does not re-execute completed work |

Only the **frontmatter** is fingerprinted; edits to prose body or fenced-block bodies don't trigger regeneration. Structural changes do.

---

## References

- `references/spec_schema.md` — **canonical schema** for `.observent/spec.md`, `plan.md`, `tasks.json`. The contract; this SKILL.md describes the workflow.
- `references/matrix.md` — full per-framework + per-backend matrix, OpenInference instrumentor map, span-attribute summary, context propagation patterns, multi-backend fan-out, troubleshooting, verified version pins.
- `references/openinference.md` — canonical OpenInference semantic conventions reference (Phoenix-native; used when convention=`oi` or `both`).
- `references/otel_genai.md` — canonical OTel-GenAI semantic conventions reference (Langfuse / SigNoz / Elastic APM / LangSmith / Opik / Jaeger; used when convention=`otel-genai` or `both`).
- `references/examples.md` — runnable end-to-end examples (backends rotated across frameworks, plus one per non-Phoenix backend) and a multi-backend fan-out example.
- `references/capture.md` — canonical transport-agnostic engine (`observent_capture.py`) that captures AI-boundary input/output + run status by enriching the existing root span, plus the optional `observent_http.py` raw-HTTP-body adapter.
- `references/gateway.md` — canonical gateway-boundary capture pattern for **opaque vendor runtimes** you can't instrument (Claude Code, Cursor): a litellm-proxy `CustomLogger` (`observent_litellm.py`) that stamps an injected correlation id so a run's LLM calls group by `session.id` / `gen_ai.conversation.id`. Grouping, not one trace. Consumed by Phase 2 § Step 2.4 when applicable.
- `references/eval.md` — canonical eval-gate engine: the `.observent/eval.json` schema, the cross-convention alias table, the generated `observent_eval.py` collector, the PII/secret value-regex set, CI snippets, and the LLM-as-judge delegation contract. Consumed by Phase 5.
- `references/self_host.md` — canonical local-provisioning reference: pinned Docker compose templates / clone commands per self-hostable backend (Phoenix · Langfuse · SigNoz · Elastic APM · Opik · Jaeger), the LangSmith "not provisioned" note, and the image-tag pin table. Consumed by Phase 1 § 1.5 and Phase 2 § 2.1.
- `scripts/detect_framework.py` — outputs JSON listing detected frameworks, backends, instrumentors, and web frameworks.
- `scripts/existing_setup.py` — outputs JSON listing pre-existing observability config.
- `scripts/validate_setup.py <backend|backend,backend,...|all> [--smoke-test]` — env vars, package presence, endpoint reachability, per-backend convention-aware synthetic span emission.
- `scripts/eval_gate.py --spec <eval.json> --spans <spans.jsonl> [--baseline <baseline.json>] [--format text|json|junit] [--update-baseline] [--fail-on-unjudged]` — the Phase 5 deterministic eval gate; normalizes spans across conventions and asserts budgets/behavior/redaction/regression, exit 0/1.
