# Eval Gate — close the loop on telemetry

observent's wiring ends the moment spans land in a backend. The **eval gate** is
the optional 5th lifecycle step (**Evaluate**) that turns the telemetry observent
already produces into a deterministic, **offline, zero-dependency CI quality
gate**: run the agent once in eval mode, collect spans to a local file, and assert
budgets + behavior from a declarative `.observent/eval.json`, exiting non-zero on
violation. **No backend required** — the gate reads captured spans, not a live UI.

This is the canonical reference for the eval engine (peer to `capture.md`). `SKILL.md`
Phase 5 links here.

---

## Pieces

| Piece | Where | What |
|---|---|---|
| `scripts/eval_gate.py` | this skill (stdlib-only) | The deterministic runner — parses spans, normalizes across conventions, asserts the gate, exits 0/1 |
| `observent_eval.py` | generated in the user's project | Span collector — activated by `OBSERVENT_EVAL=1`, writes finished spans to `.observent/eval/spans.jsonl`; **no-op in prod** |
| `.observent/eval.json` | the user's project (artifact) | The declarative assertions spec (JSON, not YAML — a plain script parses it) |
| `.observent/eval/spans.jsonl` | runtime output | One OTel `ReadableSpan.to_json()` object per line (ephemeral) |
| `.observent/eval/baseline.json` | runtime output | Committed reference metrics for relative regression checks |

---

## Why JSON, not YAML

`eval_gate.py` is stdlib-only (like `validate_setup.py`), so its spec is **JSON** —
no PyYAML dependency. `spec.md` / `plan.md` use YAML because *Claude* parses them;
the gate is parsed by a plain script, so JSON.

---

## Cross-convention alias table

The gate normalizes every span to canonical fields so the same `eval.json` works
for `oi`, `otel-genai`, and `both` captures. First present non-null key wins (OI
tried first, then OTel-GenAI). Every key below exists in `openinference.md` /
`otel_genai.md` (asserted by `tests/test_docs_consistency.py`).

| Canonical field | OpenInference key(s) | OTel-GenAI key(s) |
|---|---|---|
| `span_kind` | `openinference.span.kind` | `gen_ai.operation.name` |
| `model` | `llm.model_name` | `gen_ai.request.model`, `gen_ai.response.model` |
| `provider` | `llm.provider`, `llm.system` | `gen_ai.provider.name` |
| `prompt_tokens` | `llm.token_count.prompt` | `gen_ai.usage.input_tokens` |
| `completion_tokens` | `llm.token_count.completion` | `gen_ai.usage.output_tokens` |
| `total_tokens` | `llm.token_count.total` | *(derived: input + output)* |
| `cache_read_tokens` | `llm.token_count.prompt_details.cache_read` | `gen_ai.usage.cache_read.input_tokens` |
| `cache_write_tokens` | `llm.token_count.prompt_details.cache_write` | `gen_ai.usage.cache_creation.input_tokens` |
| `tool_name` | `tool.name`, `tool_call.function.name` | *(span name `execute_tool {name}`)* |
| `finish_reasons` | `llm.finish_reasons` | `gen_ai.response.finish_reasons` |

**Span-kind normalization.** OI kinds (`LLM`, `TOOL`, `AGENT`, `CHAIN`,
`RETRIEVER`, `EMBEDDING`, …) and OTel-GenAI operations (`chat` / `text_completion`
→ `llm`, `execute_tool` → `tool`, `invoke_agent` / `create_agent` → `agent`,
`retrieval` → `retriever`, `embeddings` → `embedding`, `invoke_workflow` →
`chain`) both fold into lowercase canonical kinds.

---

## `eval.json` schema

```json
{
  "schema_version": 1,
  "convention": "oi",
  "budgets": {
    "max_total_tokens": 8000,
    "max_prompt_tokens": 6000,
    "max_completion_tokens": 2000,
    "max_root_latency_ms": 25000,
    "max_llm_calls": 6,
    "max_cost_usd": 0.05
  },
  "behavior": {
    "require_span_kinds": ["agent", "llm", "tool"],
    "require_tools": ["web_search"],
    "forbid_tools": ["shell"],
    "expect_llm_calls": [1, 6],
    "no_error_status": true
  },
  "redaction": { "assert_no_leaks": true },
  "regression": {
    "max_increase_pct": 20,
    "metrics": ["total_tokens", "root_latency_ms", "cost_usd"]
  },
  "cost_rates": {
    "claude-sonnet-4-6": { "input_per_1k": 0.003, "output_per_1k": 0.015 }
  },
  "judge": {
    "criteria": [
      { "id": "answer_relevant", "prompt": "Is the final output a relevant answer to the input?" }
    ]
  }
}
```

Every family and every key is **independently optional** — omit a key and its
check is simply not run. Notes:

- **`budgets`** — absolute ceilings (`<=`). `max_cost_usd` is enforced **only** when
  `cost_rates` is supplied; otherwise it's reported `skip`. observent ships **no**
  bundled model→price table (no pricing-drift maintenance liability).
- **`behavior`** — `expect_llm_calls` accepts an exact int or a `[min, max]` range.
  `require_tools` / `forbid_tools` match canonical tool names.
- **`redaction.assert_no_leaks`** — scans **all** string attribute values with the
  PII/secret regex set below; proves the generated redaction actually fired.
- **`regression`** — relative check vs the committed `baseline.json`. Fails when any
  listed metric grew beyond `max_increase_pct`. Skipped (not failed) when no baseline.
- **`judge.criteria`** — never scored by the script; emitted as `needs-agent` for the
  host agent (or an optional generated judge) to resolve. See § LLM-as-judge.

### `baseline.json`

```json
{
  "created_at": "2026-06-25T10:00:00+00:00",
  "metrics": {
    "total_tokens": 5200, "prompt_tokens": 4100, "completion_tokens": 1100,
    "cost_usd": 0.041, "root_latency_ms": 18000.0, "llm_calls": 4
  }
}
```

Seed / refresh it with `eval_gate.py --update-baseline`. Commit it so the gate is a
team contract. `spans.jsonl` is ephemeral (gitignore it); `baseline.json` is committed.

---

## PII / secret value-regex set

Applied to every string attribute value (redacted values are `***REDACTED***` and
never match). Mirrors the intent of `capture.md` `_REDACT_KEYS`, at the value level.

| Label | Shape |
|---|---|
| `email` | `user@host.tld` |
| `ssn` | `NNN-NN-NNNN` |
| `credit_card` | 13–16 digits (optionally space/dash grouped) |
| `openai_key` | `sk-…` (20+ chars) |
| `aws_access_key` | `AKIA…` (16 chars) |
| `google_key` | `AIza…` (20+ chars) |
| `bearer_token` | `Bearer <16+ chars>` |

Token-count attributes are skipped to avoid false-positiving the credit-card pattern.

---

## Generated collector — `observent_eval.py`

Generated into the user's project. Depends only on the OTel SDK (already installed by
`observent_otel.py`). Activated by `OBSERVENT_EVAL=1`; a complete **no-op in prod**.
It piggybacks on the existing provider and adds a `SimpleSpanProcessor` whose exporter
writes each finished span via the SDK's own `span.to_json(indent=None)` — no custom
serializer.

```python
# observent_eval.py
"""Eval-mode span collector. Writes finished spans to .observent/eval/spans.jsonl
as one OTel ReadableSpan.to_json() object per line, for the offline eval gate
(skills/observent/scripts/eval_gate.py).

No-op unless OBSERVENT_EVAL=1, so it is safe to import unconditionally from
observent_otel.py. Generated by observent.
"""
from __future__ import annotations

import os
from pathlib import Path

from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult

_SPANS_PATH = Path(".observent/eval/spans.jsonl")


class _JsonlFileExporter(SpanExporter):
    """Append each finished span as a single JSON line (ReadableSpan.to_json)."""

    def __init__(self, path: Path) -> None:
        self._path = path
        path.parent.mkdir(parents=True, exist_ok=True)

    def export(self, spans: tuple[ReadableSpan, ...]) -> SpanExportResult:
        with self._path.open("a", encoding="utf-8") as fh:
            for span in spans:
                fh.write(span.to_json(indent=None) + "\n")
        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        return None


def install_eval_collector(provider: TracerProvider) -> None:
    """Attach the JSONL collector to `provider` when OBSERVENT_EVAL=1; else no-op."""
    if os.environ.get("OBSERVENT_EVAL") != "1":
        return
    if _SPANS_PATH.exists():
        _SPANS_PATH.unlink()  # fresh capture per eval run
    provider.add_span_processor(SimpleSpanProcessor(_JsonlFileExporter(_SPANS_PATH)))
```

Wire it in `observent_otel.py` right after the provider is built:

```python
from observent_eval import install_eval_collector
install_eval_collector(provider)   # no-op unless OBSERVENT_EVAL=1
```

`SimpleSpanProcessor` (not `Batch`) so spans flush deterministically as they finish —
the gate reads a complete file the moment the run returns.

---

## Running the gate

```bash
# 1. Collect a run
OBSERVENT_EVAL=1 python your_app.py "a representative question"

# 2. Seed a baseline (first time / when an increase is intended)
python <skill-dir>/scripts/eval_gate.py \
  --spec .observent/eval.json --spans .observent/eval/spans.jsonl \
  --baseline .observent/eval/baseline.json --update-baseline

# 3. Gate (exit 1 on any violation)
python <skill-dir>/scripts/eval_gate.py \
  --spec .observent/eval.json --spans .observent/eval/spans.jsonl \
  --baseline .observent/eval/baseline.json

# 4. (optional) Save a shareable HTML report to open anytime
python <skill-dir>/scripts/eval_gate.py \
  --spec .observent/eval.json --spans .observent/eval/spans.jsonl \
  --baseline .observent/eval/baseline.json \
  --format html > .observent/eval/report.html
```

Flags: `--format text|json|junit|html` (default `text`), `--update-baseline`,
`--fail-on-unjudged` (treat unresolved judge criteria as failures rather than skips).

### HTML report

`--format html` emits a **self-contained** report (no external assets — inline CSS, no CDN
links) to stdout; redirect it to a `.html` file to open in any browser, attach to a PR, or
archive. It renders the PASS/FAIL banner, the metric cards (tokens / latency / calls / cost),
and every check with a colored status badge. The output is intentionally **ASCII-only** so the
stdout redirect stays byte-safe under any platform locale (e.g. cp1252 on Windows). Exit code
is unchanged (0/1), so a CI job can both gate *and* publish the report from one run.

---

## CI integration

```yaml
# .github/workflows/eval.yml (excerpt)
- name: Run agent in eval mode
  env:
    OBSERVENT_EVAL: "1"
  run: python your_app.py "representative CI question"

- name: observent eval gate
  run: >-
    python skills/observent/scripts/eval_gate.py
    --spec .observent/eval.json
    --spans .observent/eval/spans.jsonl
    --baseline .observent/eval/baseline.json
    --format junit > eval-results.xml
```

Exit code 1 fails the job; the JUnit XML feeds dashboards / test-report actions.

---

## LLM-as-judge delegation

Subjective answer quality ("is the summary good?") can't be scored by a stdlib
script, so `judge.criteria` are **delegated**:

- The runner emits each criterion as a `needs-agent` check (never `pass`/`fail`).
- The **interactive** `/observent-eval` command resolves them: read the input/output
  pairs from `spans.jsonl` (root-span `input.value` / `output.value`) and have the host
  agent score each criterion, reporting alongside the deterministic results.
- A **deterministic CI run** treats `needs-agent` as skipped — unless
  `--fail-on-unjudged` is passed.
- An optional headless generated judge (a small script that calls an LLM over the
  captured pairs) is a documented *secondary* path; it is never a mandatory dependency.

---

*Last verified: 2026-06-25 with Python 3.12, OpenTelemetry SDK 1.41.*
