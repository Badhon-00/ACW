# observent — Spec / Plan / Tasks Schema

This file is the **canonical schema reference** for the three artifacts the observent skill produces and consumes in the **user's project** under `.observent/`. The skill should construct and validate these artifacts strictly against the shapes documented here.

```
<user-project>/
  .observent/
    spec.md       # what & why  — Markdown + YAML frontmatter
    plan.md       # how         — YAML frontmatter + fenced-block bodies referenced by anchor
    tasks.json    # checkpoint  — ordered task list, mutated as work proceeds
```

Three principles:

1. **Each artifact is fingerprinted by its upstream.** `plan.md` stores a sha256 of `spec.md`'s frontmatter; `tasks.json` stores a sha256 of `plan.md`'s frontmatter. Downstream regenerates when the fingerprint mismatches.
2. **`tasks.json` IS the session.** No separate `session.json`. Presence of any task with status `pending` or `failed` means the workflow is incomplete and `/observent` should offer to resume.
3. **No imperative drivers.** The skill reads/writes these files directly via Read/Write/Edit. There is no `run_tasks.py` — task `kind` values map 1:1 to Claude Code tools.

---

## 1. `.observent/spec.md`

**Purpose:** capture the *what* and *why* — detected environment, user choices (framework, backends), the convention derived from those choices, and the existing-setup decision. Locked once the user confirms; downstream artifacts re-derive from this file.

**Format:** YAML frontmatter (structured fields) followed by free-form Markdown (user-editable prose). The skill regenerates the frontmatter on `/observent-spec` re-runs but preserves the prose body.

```yaml
---
schema_version: 1
created_at: 2026-05-19T10:00:00Z
updated_at: 2026-05-19T10:00:00Z
status: draft               # draft | locked
detection:
  frameworks_detected: [langgraph]                       # from detect_framework.py: frameworks[].name
  backends_installed:  []                                # from detect_framework.py: backends[].name
  web_frameworks:      [fastapi]                         # from detect_framework.py: web_frameworks[].name
  existing_setup:                                        # from existing_setup.py: detected[]
    - {name: opentelemetry, kind: instrumentation, imports: [main.py], env_vars_in_files: [], env_files: []}
  docker_available: true                                 # from detect_framework.py: docker.available
  docker_compose_available: true                         # from detect_framework.py: docker.compose_available
  package_manager: uv                                    # from detect_framework.py: package_manager — uv | poetry | pipenv | pip | null (lockfile/manifest presence)
  backends_reachable:                                    # one entry per self-host backend in choice.backends; cloud backends omitted
    phoenix: false                                       # endpoint probed at spec/resume time (false => provisioning may be offered)
  project_fingerprint: sha256:<hex>                      # sha256 of (pyproject.toml + requirements*.txt + poetry.lock) bytes, in that fixed order
choice:
  # EITHER framework (single-service repo) …
  framework: langgraph                                   # one of: langgraph | crewai | microsoft-agent-framework | anthropic-agents | openai-agents | smolagents | llama-index | google-adk | custom
  # … OR services (multi-service monorepo: multiple frameworks across independent
  # entry-point processes). Provide exactly one of `framework` / `services` — see
  # § Multi-service specs below.
  # services:
  #   - {name: text2sql,     framework: crewai,    entry_point: services/text2sql/server.py}
  #   - {name: deepresearch, framework: langgraph, entry_point: services/deepresearch/main.py}
  backends: [phoenix, langsmith]                         # non-empty subset of: phoenix | langfuse | signoz | elastic-apm | langsmith | opik | jaeger
  convention: both                                       # derived mechanically from `backends` — see § Convention derivation below
  existing_setup_decision: extend                        # extend | replace | abort | none | scaffold_only  (none = nothing detected; scaffold_only = env-var names/config exist but no instrumentation code was ever written)
  endpoints:                                             # one entry per backend in `choice.backends`
    phoenix:   {mode: self-host, url: "http://localhost:6006/v1/traces"}
    langsmith: {mode: cloud,     url: "https://api.smith.langchain.com/otel/v1/traces"}
  env_vars_required: [PHOENIX_API_KEY, LANGSMITH_API_KEY, LANGSMITH_PROJECT]
  http_body_capture: true                                # OPTIONAL raw-HTTP-body adapter; true iff detection.web_frameworks contains fastapi/starlette AND raw wire payload is wanted. AI-boundary capture (observent_capture.py) is always generated regardless.
  http_transport_spans: none                             # none | root-only | full — how much web-framework/transport instrumentation to emit. Only meaningful when detection.web_frameworks is non-empty. Default is backend-dependent: `none` for LLM-native-only backend sets ({phoenix,langfuse,opik,langsmith}); `root-only` when any APM backend ({signoz,elastic-apm,jaeger}) is present. See SKILL.md § 2.4 + references/capture.md § HTTP transport spans.
  self_host_provision:                                   # per self-host backend: provision a local Docker stack? (see references/self_host.md)
    phoenix: true                                        # only keys for backends with endpoints.<backend>.mode == self-host; langsmith NEVER appears (no OSS edition)
  auto_instrumenting_deps:                               # OPTIONAL; one key per detect_framework.py `auto_instrumenting_deps` entry (deps that ship dormant OTel instrumentation). Absent/empty when none detected. See SKILL.md § 1.4b + references/matrix.md § Known auto-instrumenting dependencies.
    a2a-sdk: disable                                     # keep | disable — `disable` appends `<ENV_VAR>=false` to .env (e.g. OTEL_INSTRUMENTATION_A2A_SDK_ENABLED=false)
---

# Observability Spec

Free-form rationale and user notes. The skill preserves this body across re-runs of `/observent-spec`; only the frontmatter is regenerated.
```

### Convention derivation (mechanical, not user-supplied)

| `choice.backends` set | `choice.convention` |
|---|---|
| `{phoenix}` | `oi` |
| Any non-empty subset of `{langfuse, signoz, elastic-apm, langsmith, opik, jaeger}` (no Phoenix) | `otel-genai` |
| Any set containing Phoenix **and** at least one of `{langfuse, signoz, elastic-apm, langsmith, opik, jaeger}` | `both` |

The skill writes this field — it is never asked of the user. To change the convention the user changes the backend set and re-runs `/observent-spec`.

### Multi-service specs (`choice.services`)

Exactly one of `choice.framework` (singular) or `choice.services` (a list) is present — never both. `choice.services` is for a multi-service monorepo: multiple frameworks across independent entry-point processes (e.g. several A2A services, each its own framework and its own `server.py`/`main.py`). See SKILL.md Step 1.2 bullet 3b for when the skill offers this path instead of forcing a single framework pick.

Each entry is `{name, framework, entry_point}`:

- `name` — a short, stable service identifier. Used for that service's `_SERVICE_NAME` generation-time literal and its `<name>.run` fallback span name.
- `framework` — one of the `choice.framework` enum values above. Drives that service's instrumentor.
- `entry_point` — the project-relative file Phase 2 edits to import `observent_otel` and wrap that service's AI boundary.

`convention`, `backends`, `endpoints`, `env_vars_required`, and the rest of `choice` stay **shared** across all services (derived once from the backend set) — services differ only by framework and entry point. Phase 2 generates **one** shared `observent_capture.py`; each service's wrap point passes its own identity per-call — `open_or_enrich_span(..., agent_name=<name>, agent_framework=<framework>)` — using the `agent_framework` override (`references/capture.md`) instead of relying on a single global `_FRAMEWORK` literal, since that literal can only hold one framework at a time.

### `existing_setup_decision` states

- `none` — `existing_setup.py` detected nothing; no decision needed.
- `extend` — a working setup exists (`instrumentation_code_found: true` on at least one detected entry); keep it and layer observent's attributes/instrumentors on top.
- `replace` — a working setup exists but the user wants observent's recommended pattern instead; overwrite it.
- `abort` — exit without changes.
- `scaffold_only` — `existing_setup.py` reports `scaffold_only: true`: env-var names/config exist (from an earlier, incomplete attempt) but every detected entry has `instrumentation_code_found: false` — there is no working code to either extend or replace. observent generates a fresh setup as if the project were clean, but reuses the already-present env-var names instead of introducing new ones. See SKILL.md Step 1.4.

### Project fingerprint

`detection.project_fingerprint` is sha256 over the concatenated bytes of, in this order:

1. `pyproject.toml` (if present)
2. `requirements.txt`, `requirements-dev.txt`, `requirements/*.txt` sorted lexicographically (each if present)
3. `poetry.lock` (if present)

Missing files contribute nothing (not a placeholder). Computed at spec generation and on every resume. A mismatch on resume triggers the drift prompt (§ "Resume mechanics" in SKILL.md).

### Local self-host provisioning (`detection.docker_*`, `detection.backends_reachable`, `choice.self_host_provision`)

When a backend's resolved endpoint `mode` is `self-host`, the skill probes it for reachability and records the result in `detection.backends_reachable.<backend>`. If unreachable **and** Docker is available (`detection.docker_available && detection.docker_compose_available`) **and** the backend is one of `{phoenix, langfuse, signoz, elastic-apm, opik, jaeger}`, the skill offers to stand it up locally; a `yes` sets `choice.self_host_provision.<backend> = true`. Rules:

- `choice.self_host_provision` only has keys for backends whose `endpoints.<backend>.mode == self-host`. Cloud backends never appear.
- `langsmith` **never** appears — it has no free OSS/Docker edition (self-host is enterprise-licensed). See `references/self_host.md § LangSmith`.
- The compose templates / clone commands themselves are **not** stored here — they live in `references/self_host.md`. The spec only records the *decision*; the plan materializes it.

---

## 2. `.observent/plan.md`

**Purpose:** capture the *how* — the deterministic mapping from `spec.choice` to concrete file operations, install commands, env vars, and the multi-backend processor shape. The plan body holds the **actual generated content** for every file as fenced blocks behind anchor comments; `tasks.json` refers to those anchors instead of duplicating content.

**Format:** YAML frontmatter followed by anchored fenced blocks.

```markdown
---
schema_version: 1
generated_from_spec_at: 2026-05-19T10:01:00Z
spec_fingerprint: sha256:<hex of spec.md frontmatter>
files:
  - {path: "observent_otel.py",                  op: create, purpose: "TracerProvider + per-backend BatchSpanProcessors"}
  - {path: "observent_capture.py",               op: create, purpose: "Transport-agnostic AI-boundary input/output/status capture (redacted)"}
  - {path: "observent_http.py",                  op: create, purpose: "OPTIONAL raw-HTTP-body adapter (only if http_body_capture)"}
  - {path: "docker-compose.observent-phoenix.yml", op: create, purpose: "Local Phoenix stack (vendored-compose provisioning)"}
  - {path: "main.py",                            op: edit,   purpose: "Import observent_otel; wrap agent invocation with capture_run"}
  - {path: ".env",                               op: append, purpose: "Env var stubs (names only, no values)"}
pip_install: "uv add opentelemetry-sdk==X.Y.Z openinference-instrumentation-langchain==X.Y.Z arize-phoenix-otel==X.Y.Z ..."  # despite the key name, this holds the resolved manager's install command (uv add / poetry add / pipenv install / pip install) — see SKILL.md § 2.1
env_vars:
  phoenix:   [PHOENIX_API_KEY]
  langsmith: [LANGSMITH_API_KEY, LANGSMITH_PROJECT]
processors:
  - {backend: phoenix,   kind: BatchSpanProcessor, exporter: OTLPSpanExporter}
  - {backend: langsmith, kind: BatchSpanProcessor, exporter: OTLPSpanExporter}
elastic_apm_native_agent: false                # true iff `elastic-apm` ∈ spec.choice.backends
openai_agents_native_processors: false         # true iff spec.choice.framework == openai-agents
provision:                                     # one entry per backend with spec.choice.self_host_provision.<backend> == true; empty list otherwise
  - backend: phoenix
    method: vendored-compose                   # vendored-compose | upstream-clone | vendor-cli-generated (see references/self_host.md § Provisioning method per backend)
    compose_file: docker-compose.observent-phoenix.yml   # vendored-compose: names a files[] entry (plan:compose_<backend> anchor). upstream-clone: null. vendor-cli-generated: the CLI-generated path (e.g. pours/deployment/compose.yaml) — NOT a plan anchor.
    up_command: "docker compose -f docker-compose.observent-phoenix.yml up -d --wait"
    down_command: "docker compose -f docker-compose.observent-phoenix.yml down"
    ui_url: "http://localhost:6006"
    otlp_url: "http://localhost:6006/v1/traces"
  # vendor-cli-generated adds three fields (present only for that method; null/absent otherwise):
  #   cli_install_command: "curl -fsSL https://signoz.io/foundry.sh | bash"   # installs a binary -> needs an installs_cli confirm (below)
  #   cli_config_file:     casting.yaml                                        # a files[] create entry; content in the <!-- plan:clicfg_<backend> --> anchor
  #   generate_command:    "foundryctl forge -f casting.yaml"                  # runs the CLI's forge-equivalent to materialize compose_file
---

<!-- plan:observent_otel -->
```python
# full content of observent_otel.py — emitted verbatim into the user's project at task execution
```

<!-- plan:observent_capture -->
```python
# full content of observent_capture.py
```

<!-- plan:observent_http -->
```python
# full content of observent_http.py (only when http_body_capture: true)
```

<!-- plan:compose_phoenix -->
```yaml
# full content of docker-compose.observent-phoenix.yml — only present for vendored-compose
# backends (phoenix, elastic-apm, jaeger); upstream-clone backends (langfuse, opik) have no anchor,
# their `provision[].up_command` does the git clone + docker compose up. vendor-cli-generated
# backends (signoz) also have no compose anchor — the CLI generates the compose file — but DO carry
# a <!-- plan:clicfg_<backend> --> anchor for the CLI's declarative config. See references/self_host.md.
```

<!-- plan:clicfg_signoz -->
```yaml
# full content of the CLI's declarative config (e.g. Foundry casting.yaml) — only present for
# vendor-cli-generated backends. Written by a write_file task; consumed by provision[].generate_command.
```

<!-- plan:main_edit -->
```diff
# unified diff applied to main.py
```

<!-- plan:env_append -->
```
# lines appended to .env (names only — no values)
PHOENIX_API_KEY=
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=
```
```

### Anchor naming

Each anchor is the comment `<!-- plan:<slug> -->` immediately followed by a single fenced block. Slugs are stable identifiers referenced from `tasks.json` via `content_ref: "plan#<slug>"` (for `write_file`) or `diff_ref: "plan#<slug>"` (for `edit_file`). The skill MUST NOT inline the same content into both files — `plan.md` is the single source of truth.

### Plan invariants

- `files[].path` is relative to the user's project root.
- `files[].op` is `create` (write a new file), `edit` (apply a unified diff), or `append` (append to file; create if missing).
- `pip_install` is **one** line, even when long; the skill quotes pinned versions from `references/matrix.md § Verified Versions`, rendered in the syntax of `spec.detection.package_manager` (`uv add` / `poetry add` / `pipenv install` / `pip install`).
- `env_vars` keys are exactly the entries in `spec.choice.backends`.
- `processors` lists one entry per OTLP backend in `spec.choice.backends`; Elastic APM in native-agent mode does NOT appear here (it attaches to the global tracer via its OTel bridge — captured by `elastic_apm_native_agent: true` instead).
- `provision` has one entry per backend with `spec.choice.self_host_provision.<backend> == true` (empty list when no provisioning was requested). Per `method`:
  - `vendored-compose` — `compose_file` names a `files[]` create entry whose content lives in the `<!-- plan:compose_<backend> -->` anchor; `up_command` runs `docker compose … up -d --wait` on it.
  - `upstream-clone` — `compose_file` is null; `up_command` performs the pinned `git clone` + `docker compose up`.
  - `vendor-cli-generated` — `compose_file` is the **CLI-generated** path (e.g. `pours/deployment/compose.yaml`), **not** a `plan:compose_*` anchor. Adds `cli_install_command` (installs the vendor CLI — must trigger an `installs_cli` `confirm`, see § tasks.json), `cli_config_file` (a `files[]` create entry with content in the `<!-- plan:clicfg_<backend> -->` anchor), and `generate_command` (runs the CLI's `forge`-equivalent to materialize `compose_file`). Ordered tasks: install-CLI `run_command` → write-config `write_file` → generate `run_command` → `up_command` `run_command`.
  Templates and pinned image/CLI versions come from `references/self_host.md` — never inline them anywhere else.

```

## 3. `.observent/tasks.json`

**Purpose:** ordered, mutable task list that drives the implement phase. **This is the checkpoint** — the skill mutates entries as it executes them. Resume = read this file, find the first non-terminal task, continue.

```json
{
  "schema_version": 1,
  "plan_fingerprint": "sha256:<hex of plan.md frontmatter>",
  "created_at": "2026-05-19T10:02:00Z",
  "updated_at": "2026-05-19T10:02:00Z",
  "tasks": [
    {
      "id": "t01",
      "kind": "confirm",
      "payload": {"prompt": "Apply diff preview? (yes / preview <file> / abort)"},
      "status": "pending",
      "started_at": null,
      "finished_at": null,
      "error": null
    },
    {
      "_comment": "Optional installs_cli confirm — REQUIRED before any vendor-cli-generated provision runs (it installs a local binary, a larger consent surface than `docker compose up`).",
      "id": "t01b",
      "kind": "confirm",
      "payload": {
        "prompt": "Provisioning SigNoz installs the Foundry CLI (foundryctl). Proceed? (yes / no)",
        "installs_cli": {
          "package": "foundryctl",
          "installer_url": "https://signoz.io/foundry.sh",
          "trust_basis": "checksum-verified GitHub release; installs to ~/.local/bin; no arbitrary remote exec"
        }
      },
      "status": "pending", "started_at": null, "finished_at": null, "error": null
    },
    {
      "id": "t02",
      "kind": "write_file",
      "payload": {"path": "observent_otel.py", "content_ref": "plan#observent_otel"},
      "status": "pending", "started_at": null, "finished_at": null, "error": null
    },
    {
      "id": "t03",
      "kind": "write_file",
      "payload": {"path": "observent_capture.py", "content_ref": "plan#observent_capture"},
      "status": "pending", "started_at": null, "finished_at": null, "error": null
    },
    {
      "id": "t04",
      "kind": "edit_file",
      "payload": {"path": "main.py", "diff_ref": "plan#main_edit"},
      "status": "pending", "started_at": null, "finished_at": null, "error": null
    },
    {
      "id": "t05",
      "kind": "run_command",
      "payload": {"cmd": "pip install opentelemetry-sdk==X.Y.Z ..."},
      "status": "pending", "started_at": null, "finished_at": null, "error": null
    },
    {
      "_comment": "t06–t09 are the vendor-cli-generated provision the t01b confirm gates (SigNoz/Foundry): install CLI → write CLI config → generate compose → up. For a vendored-compose backend (Phoenix/Elastic APM/Jaeger) this collapses to a single write_file (docker-compose.observent-<backend>.yml, content_ref plan#compose_<backend>) + one `docker compose … up -d --wait` run_command; for upstream-clone (Langfuse/Opik), a single `git clone … && docker compose … up` run_command.",
      "id": "t06",
      "kind": "run_command",
      "payload": {"cmd": "curl -fsSL https://signoz.io/foundry.sh | bash"},
      "status": "pending", "started_at": null, "finished_at": null, "error": null
    },
    {
      "id": "t07",
      "kind": "write_file",
      "payload": {"path": "casting.yaml", "content_ref": "plan#clicfg_signoz"},
      "status": "pending", "started_at": null, "finished_at": null, "error": null
    },
    {
      "id": "t08",
      "kind": "run_command",
      "payload": {"cmd": "foundryctl forge -f casting.yaml"},
      "status": "pending", "started_at": null, "finished_at": null, "error": null
    },
    {
      "id": "t09",
      "kind": "run_command",
      "payload": {"cmd": "docker compose -f pours/deployment/compose.yaml up -d --wait"},
      "status": "pending", "started_at": null, "finished_at": null, "error": null
    },
    {
      "id": "t10",
      "kind": "validate",
      "payload": {"cmd": "python <skill-dir>/scripts/validate_setup.py phoenix,signoz --smoke-test"},
      "status": "pending", "started_at": null, "finished_at": null, "error": null
    }
  ]
}
```

### Task `kind` reference

| `kind` | Maps to | Required `payload` fields |
|---|---|---|
| `confirm` | User prompt | `prompt` (string); optional `installs_cli` `{package, installer_url, trust_basis}` — set when the confirm gates a `vendor-cli-generated` provision that installs a local binary, so the diff preview shows what's installed and why it's trustworthy |
| `write_file` | Write tool | `path` (project-relative), `content_ref` (`plan#<slug>`) |
| `edit_file` | Edit tool | `path`, `diff_ref` (`plan#<slug>`) |
| `run_command` | Bash tool | `cmd` (string) |
| `validate` | Bash tool, final task | `cmd` (string — calls `validate_setup.py` with the resolved backend list) |

### Status reference

| Status | Terminal? | Meaning |
|---|---|---|
| `pending` | No | Not started yet |
| `failed` | No | Started but errored; resume retries |
| `done` | Yes | Completed successfully |
| `skipped` | Yes | User chose to skip (e.g., declined a `confirm`) |

"Incomplete workflow" = any task with `pending` or `failed`. `/observent` and `/observent-implement` MUST scan for this on every invocation before doing anything else.

### Mutation rules

When the skill starts a task it sets `status: pending` → `started_at` to now (it stays `pending` until done/failed; there is no `in_progress` value). On success: `status: done`, `finished_at` = now, `error` = null. On failure: `status: failed`, `finished_at` = now, `error` = a short string. The `confirm` kind sets `status: done` on `yes`, `skipped` on `no`/`abort` (abort also halts the run).

After mutating any task, the skill rewrites `tasks.json` to disk before moving to the next task. This is what makes the workflow durable across session breaks.

### Task ordering

Tasks execute strictly in array order. The first task is always a `confirm` carrying the rendered diff preview (file list + diffs + pip command + env var groups + any compose files and `docker compose up` commands, mechanically derived from `plan.md` — same content the old Step 5 produced). The last task is always `validate`. Between them: `write_file` entries first (application files, then any `vendored-compose` files), then `edit_file`, then `run_command` for `pip install`, then the **provisioning** `run_command`(s) — one `docker compose ... up -d --wait` per `plan.provision[]` entry. Provisioning runs *after* pip-install and *before* `validate` so the backend endpoint is live when validation probes it. No new task `kind` is introduced — provisioning reuses `write_file` (for `vendored-compose`) and `run_command` (the `up` / clone+up command).

---

## 4. `.observent/eval.json` (optional — Phase 5 eval gate)

**Purpose:** the declarative assertions spec for the optional **Evaluate** step. A peer
artifact to spec/plan/tasks, generated by `/observent-eval` only when the user opts into
the eval gate. Unlike the three core artifacts it is **JSON, not YAML** — it is parsed by
the stdlib-only `scripts/eval_gate.py`, which carries no PyYAML dependency.

**Format:** a single JSON object. Every assertion family and every key is independently
optional; an omitted key means its check is not run.

```json
{
  "schema_version": 1,
  "convention": "oi",
  "budgets": { "max_total_tokens": 8000, "max_root_latency_ms": 25000, "max_llm_calls": 6 },
  "behavior": { "require_span_kinds": ["agent", "llm", "tool"], "require_tools": ["web_search"] },
  "redaction": { "assert_no_leaks": true },
  "regression": { "max_increase_pct": 20, "metrics": ["total_tokens", "root_latency_ms", "cost_usd"] },
  "cost_rates": { "claude-sonnet-4-6": { "input_per_1k": 0.003, "output_per_1k": 0.015 } },
  "judge": { "criteria": [ { "id": "answer_relevant", "prompt": "Is the output a relevant answer?" } ] }
}
```

The **full field reference** (every budget/behavior/redaction/regression/judge key, the
cross-convention alias table, the PII/secret value-regex set, and the generated
`observent_eval.py` collector) lives in `references/eval.md` — not duplicated here.

### Invariants

- `convention` mirrors `spec.choice.convention` (`oi` | `otel-genai` | `both`); the alias
  table normalizes spans either way, so the same file works across backends.
- `budgets.max_cost_usd` is enforced **only** when `cost_rates` is present — observent ships
  no bundled model→price table. Token + latency budgets are the deterministic defaults.
- `judge.criteria[]` are never scored by the runner; they surface as `needs-agent` for the
  host agent (or an optional generated judge) to resolve.

### Runtime outputs (not committed by the skill)

- `.observent/eval/spans.jsonl` — one OTel `ReadableSpan.to_json()` object per line, written
  by the generated `observent_eval.py` collector when `OBSERVENT_EVAL=1`. **Ephemeral** —
  gitignore it (see § 6).
- `.observent/eval/baseline.json` — committed reference metrics for relative regression
  checks; `{created_at, metrics: {total_tokens, prompt_tokens, completion_tokens, cost_usd,
  root_latency_ms, llm_calls}}`. Seed/refresh with `eval_gate.py --update-baseline`.

There is **no fingerprint chain** into `eval.json` — it is hand-tuned and owned by the user
(the seed values come from a baseline run, but the file is then a committed contract, not a
regenerated artifact). It is independent of the spec→plan→tasks fingerprint flow.

---

## 5. Drift detection

Two layers of fingerprints. The skill computes the live value and compares to the stored value at every invocation; mismatches force regeneration of the downstream artifact.

| Compare | Stored in | Live source | Mismatch action |
|---|---|---|---|
| Project deps | `spec.detection.project_fingerprint` | sha256 of `pyproject.toml`+`requirements*.txt`+`poetry.lock` | Prompt: `Project deps changed since spec was written. Re-run /observent-spec? (yes / continue anyway / abort)` |
| Spec → Plan | `plan.spec_fingerprint` | sha256 of live `spec.md` frontmatter | Regenerate `plan.md` (and consequently `tasks.json`) before continuing |
| Plan → Tasks | `tasks.plan_fingerprint` | sha256 of live `plan.md` frontmatter | Regenerate `tasks.json` before continuing — but preserve `status` for tasks whose `id` + `payload` are identical (so a re-plan does not re-execute work already done; see § Resume mechanics in SKILL.md) |

The fingerprint covers **only the YAML frontmatter** of `spec.md` and `plan.md`, not the prose / fenced-block bodies. This way edits to the human-readable parts (a comment in the spec body, a tweak to a generated file's docstring in the plan body) do not force regeneration; only structural changes do.

---

## 6. `.observent/` gitignore guidance

The skill's spec-phase preamble offers two options, with **commit** as the recommended default:

- **Commit `.observent/`** — observability config is reviewable in PRs; teammates see what's wired up. Recommended.
- **Ignore `.observent/`** — treat it as ephemeral local state. Add `.observent/` to `.gitignore`.

Either is valid; the skill does not write a `.gitignore` entry on the user's behalf.

**Eval-gate exception (Phase 5):** regardless of the above choice, `.observent/eval/spans.jsonl`
is a per-run capture and should always be gitignored, while `.observent/eval/baseline.json` is a
committed regression contract. When the user commits `.observent/`, add a narrower
`.observent/eval/spans.jsonl` ignore so the ephemeral capture doesn't churn the repo.
