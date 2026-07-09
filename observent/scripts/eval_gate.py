    #!/usr/bin/env python3
"""observent eval gate — deterministic CI quality gate over captured spans.

Usage:
  python eval_gate.py --spec .observent/eval.json --spans .observent/eval/spans.jsonl
  python eval_gate.py --spec .observent/eval.json --spans .observent/eval/spans.jsonl \
      --baseline .observent/eval/baseline.json --format junit
  python eval_gate.py --spec .observent/eval.json --spans .observent/eval/spans.jsonl \
      --update-baseline
  python eval_gate.py --spec .observent/eval.json --spans .observent/eval/spans.jsonl \
      --format html > .observent/eval/report.html   # shareable, open-anytime report

Reads spans written by the generated ``observent_eval.py`` collector — one OTel
``ReadableSpan.to_json()`` object per line — normalizes each across the
OpenInference / OTel-GenAI conventions via the alias table, and asserts the
budgets / behavior / redaction / regression rules declared in ``eval.json``.

LLM-as-judge criteria are NOT evaluated here: each is reported as ``needs-agent``
for the interactive command (or an optional generated judge) to resolve. A
deterministic CI run treats ``needs-agent`` as skipped unless --fail-on-unjudged.

No third-party dependencies (stdlib only), mirroring validate_setup.py. The
assertions spec is JSON (not YAML) precisely because this plain script parses it.

Exit code: 0 = all enforced checks passed, 1 = any failure.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as _xml_escape

# --------------------------------------------------------------------------- #
# Cross-convention alias table
#
# Canonical field <- OpenInference key(s) / OTel-GenAI key(s). Mirrors the table
# in references/eval.md; every key below exists in references/openinference.md or
# references/otel_genai.md (asserted by tests/test_docs_consistency.py).
# --------------------------------------------------------------------------- #

# canonical span_kind <- openinference.span.kind value
_OI_SPAN_KIND: dict[str, str] = {
    "LLM": "llm",
    "TOOL": "tool",
    "AGENT": "agent",
    "CHAIN": "chain",
    "RETRIEVER": "retriever",
    "RERANKER": "reranker",
    "EMBEDDING": "embedding",
    "GUARDRAIL": "guardrail",
    "EVALUATOR": "evaluator",
    "PROMPT": "prompt",
}

# canonical span_kind <- gen_ai.operation.name value
_OTEL_OP_KIND: dict[str, str] = {
    "chat": "llm",
    "text_completion": "llm",
    "generate_content": "llm",
    "embeddings": "embedding",
    "retrieval": "retriever",
    "execute_tool": "tool",
    "create_agent": "agent",
    "invoke_agent": "agent",
    "invoke_workflow": "chain",
}

# canonical scalar field <- ordered list of attribute keys to try (OI first, then
# OTel-GenAI). First present non-null value wins.
_ALIAS: dict[str, tuple[str, ...]] = {
    "model": ("llm.model_name", "gen_ai.request.model", "gen_ai.response.model"),
    "provider": ("llm.provider", "llm.system", "gen_ai.provider.name"),
    "prompt_tokens": ("llm.token_count.prompt", "gen_ai.usage.input_tokens"),
    "completion_tokens": ("llm.token_count.completion", "gen_ai.usage.output_tokens"),
    "total_tokens": ("llm.token_count.total",),
    "cache_read_tokens": (
        "llm.token_count.prompt_details.cache_read",
        "gen_ai.usage.cache_read.input_tokens",
    ),
    "cache_write_tokens": (
        "llm.token_count.prompt_details.cache_write",
        "gen_ai.usage.cache_creation.input_tokens",
    ),
    "tool_name": ("tool.name", "tool_call.function.name"),
}

# --------------------------------------------------------------------------- #
# Redaction / safety — value regexes (proves the generated redaction fired).
# Applied to every string attribute value; redacted values are "***REDACTED***"
# and so never match. Mirrors the intent of capture.md _REDACT_KEYS, at the value
# level.
# --------------------------------------------------------------------------- #

_LEAK_PATTERNS: dict[str, re.Pattern[str]] = {
    "email": re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "google_key": re.compile(r"\bAIza[0-9A-Za-z_\-]{20,}\b"),
    "bearer_token": re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{16,}"),
}

# Attribute keys we never scan for leaks: ids/hex that would false-positive the
# credit-card pattern without ever carrying user PII.
_LEAK_SKIP_KEYS: frozenset[str] = frozenset({
    "llm.token_count.prompt",
    "llm.token_count.completion",
    "llm.token_count.total",
})


PASS, FAIL, SKIP, NEEDS_AGENT = "pass", "fail", "skip", "needs-agent"


@dataclass
class Check:
    name: str
    status: str
    message: str = ""


@dataclass
class Metrics:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    root_latency_ms: float = 0.0
    llm_calls: int = 0

    def as_dict(self) -> dict[str, float]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": round(self.cost_usd, 6),
            "root_latency_ms": round(self.root_latency_ms, 3),
            "llm_calls": self.llm_calls,
        }


@dataclass
class NormSpan:
    name: str
    kind: str | None
    model: str | None
    provider: str | None
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    duration_ms: float
    is_root: bool
    status_code: str
    tool_name: str | None
    attributes: dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Span loading + normalization
# --------------------------------------------------------------------------- #


def _to_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _first(attrs: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        val = attrs.get(key)
        if val is not None:
            return val
    return None


def _parse_ts(raw: str) -> datetime:
    text = raw.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return datetime.fromisoformat(text)


def _duration_ms(raw: dict[str, Any]) -> float:
    start, end = raw.get("start_time"), raw.get("end_time")
    if not isinstance(start, str) or not isinstance(end, str):
        return 0.0
    try:
        return (_parse_ts(end) - _parse_ts(start)).total_seconds() * 1000.0
    except ValueError:
        return 0.0


def _span_kind(attrs: dict[str, Any]) -> str | None:
    oi = attrs.get("openinference.span.kind")
    if oi is not None:
        return _OI_SPAN_KIND.get(str(oi).upper())
    op = attrs.get("gen_ai.operation.name")
    if op is not None:
        return _OTEL_OP_KIND.get(str(op))
    return None


def _tool_name(name: str, kind: str | None, attrs: dict[str, Any]) -> str | None:
    if kind != "tool":
        return None
    attr_name = _first(attrs, _ALIAS["tool_name"])
    if attr_name is not None:
        return str(attr_name)
    # OTel-GenAI execute_tool spans are named "execute_tool {tool_name}".
    parts = name.split(" ", 1)
    if len(parts) == 2 and parts[0] == "execute_tool":
        return parts[1]
    return name or None


def normalize_span(raw: dict[str, Any]) -> NormSpan:
    attrs = raw.get("attributes") or {}
    if not isinstance(attrs, dict):
        attrs = {}
    kind = _span_kind(attrs)
    prompt = _to_int(_first(attrs, _ALIAS["prompt_tokens"]))
    completion = _to_int(_first(attrs, _ALIAS["completion_tokens"]))
    total_raw = _first(attrs, _ALIAS["total_tokens"])
    total = _to_int(total_raw) if total_raw is not None else prompt + completion
    status = raw.get("status") or {}
    status_code = str(status.get("status_code", "UNSET")) if isinstance(status, dict) else "UNSET"
    name = str(raw.get("name", ""))
    return NormSpan(
        name=name,
        kind=kind,
        model=(str(m) if (m := _first(attrs, _ALIAS["model"])) is not None else None),
        provider=(str(p) if (p := _first(attrs, _ALIAS["provider"])) is not None else None),
        prompt_tokens=prompt,
        completion_tokens=completion,
        total_tokens=total,
        duration_ms=_duration_ms(raw),
        is_root=raw.get("parent_id") in (None, "", "null"),
        status_code=status_code,
        tool_name=_tool_name(name, kind, attrs),
        attributes=attrs,
    )


def load_spans(path: Path) -> list[NormSpan]:
    spans: list[NormSpan] = []
    with path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"eval_gate: {path}:{lineno}: invalid JSON span: {exc}") from exc
            spans.append(normalize_span(raw))
    return spans


# --------------------------------------------------------------------------- #
# Aggregation
# --------------------------------------------------------------------------- #


def _cost_for(span: NormSpan, cost_rates: dict[str, Any]) -> float:
    if not span.model:
        return 0.0
    rate = cost_rates.get(span.model)
    if not isinstance(rate, dict):
        return 0.0
    in_per_1k = float(rate.get("input_per_1k", 0.0))
    out_per_1k = float(rate.get("output_per_1k", 0.0))
    return (span.prompt_tokens / 1000.0) * in_per_1k + (span.completion_tokens / 1000.0) * out_per_1k


def aggregate(spans: list[NormSpan], cost_rates: dict[str, Any]) -> Metrics:
    m = Metrics()
    for span in spans:
        if span.kind == "llm":
            m.prompt_tokens += span.prompt_tokens
            m.completion_tokens += span.completion_tokens
            m.total_tokens += span.total_tokens
            m.cost_usd += _cost_for(span, cost_rates)
            m.llm_calls += 1
        if span.is_root:
            m.root_latency_ms = max(m.root_latency_ms, span.duration_ms)
    return m


# --------------------------------------------------------------------------- #
# Assertion families
# --------------------------------------------------------------------------- #


def _budget_check(name: str, actual: float, limit: Any, unit: str) -> Check:
    cap = float(limit)
    if actual <= cap:
        return Check(name, PASS, f"{actual:g} <= {cap:g} {unit}")
    return Check(name, FAIL, f"{actual:g} exceeds limit {cap:g} {unit}")


def check_budgets(spec: dict[str, Any], spans: list[NormSpan], metrics: Metrics) -> list[Check]:
    budgets = spec.get("budgets") or {}
    out: list[Check] = []
    mapping: list[tuple[str, str, float, str]] = [
        ("max_total_tokens", "budget.total_tokens", float(metrics.total_tokens), "tokens"),
        ("max_prompt_tokens", "budget.prompt_tokens", float(metrics.prompt_tokens), "tokens"),
        ("max_completion_tokens", "budget.completion_tokens", float(metrics.completion_tokens), "tokens"),
        ("max_root_latency_ms", "budget.root_latency_ms", metrics.root_latency_ms, "ms"),
        ("max_llm_calls", "budget.llm_calls", float(metrics.llm_calls), "calls"),
    ]
    for spec_key, check_name, actual, unit in mapping:
        if spec_key in budgets:
            out.append(_budget_check(check_name, actual, budgets[spec_key], unit))
    if "max_cost_usd" in budgets:
        if spec.get("cost_rates"):
            out.append(
                _budget_check("budget.cost_usd", round(metrics.cost_usd, 6), budgets["max_cost_usd"], "usd")
            )
        else:
            out.append(Check("budget.cost_usd", SKIP, "max_cost_usd set but no cost_rates supplied"))
    return out


def _expect_match(expect: Any, actual: int) -> bool:
    if isinstance(expect, list) and len(expect) == 2:
        return int(expect[0]) <= actual <= int(expect[1])
    return actual == int(expect)


def check_behavior(spec: dict[str, Any], spans: list[NormSpan], metrics: Metrics) -> list[Check]:
    behavior = spec.get("behavior") or {}
    out: list[Check] = []
    present_kinds = {s.kind for s in spans if s.kind}
    tools_seen = {s.tool_name for s in spans if s.tool_name}

    if "require_span_kinds" in behavior:
        required = [str(k) for k in behavior["require_span_kinds"]]
        missing = [k for k in required if k not in present_kinds]
        out.append(
            Check("behavior.require_span_kinds", PASS, f"all present: {required}")
            if not missing
            else Check("behavior.require_span_kinds", FAIL, f"missing span kinds: {missing}")
        )
    if "require_tools" in behavior:
        required_tools = [str(t) for t in behavior["require_tools"]]
        missing_tools = [t for t in required_tools if t not in tools_seen]
        out.append(
            Check("behavior.require_tools", PASS, f"all called: {required_tools}")
            if not missing_tools
            else Check("behavior.require_tools", FAIL, f"tools never called: {missing_tools}")
        )
    if "forbid_tools" in behavior:
        forbidden = [str(t) for t in behavior["forbid_tools"]]
        used = [t for t in forbidden if t in tools_seen]
        out.append(
            Check("behavior.forbid_tools", PASS, f"none called: {forbidden}")
            if not used
            else Check("behavior.forbid_tools", FAIL, f"forbidden tools called: {used}")
        )
    if "expect_llm_calls" in behavior:
        expect = behavior["expect_llm_calls"]
        if _expect_match(expect, metrics.llm_calls):
            out.append(Check("behavior.expect_llm_calls", PASS, f"{metrics.llm_calls} llm call(s)"))
        else:
            out.append(
                Check("behavior.expect_llm_calls", FAIL, f"{metrics.llm_calls} calls, expected {expect}")
            )
    if behavior.get("no_error_status"):
        errored = [s.name for s in spans if s.status_code == "ERROR"]
        if not errored:
            out.append(Check("behavior.no_error_status", PASS, "no spans ended in ERROR"))
        else:
            out.append(
                Check("behavior.no_error_status", FAIL, f"{len(errored)} span(s) in ERROR: {errored[:3]}")
            )
    return out


def check_redaction(spec: dict[str, Any], spans: list[NormSpan]) -> list[Check]:
    redaction = spec.get("redaction") or {}
    if not redaction.get("assert_no_leaks"):
        return []
    leaks: list[str] = []
    for span in spans:
        for key, value in span.attributes.items():
            if key in _LEAK_SKIP_KEYS or not isinstance(value, str):
                continue
            for label, pattern in _LEAK_PATTERNS.items():
                if pattern.search(value):
                    leaks.append(f"{label} in {span.name}#{key}")
                    break
    if leaks:
        return [Check("redaction.assert_no_leaks", FAIL, f"{len(leaks)} leak(s): {leaks[:3]}")]
    return [Check("redaction.assert_no_leaks", PASS, "no PII/secret patterns in attribute values")]


def check_regression(
    spec: dict[str, Any], metrics: Metrics, baseline: dict[str, Any] | None
) -> list[Check]:
    regression = spec.get("regression") or {}
    if "max_increase_pct" not in regression:
        return []
    if baseline is None:
        return [Check("regression", SKIP, "no baseline.json supplied (run with --update-baseline to seed)")]
    base_metrics = baseline.get("metrics") or {}
    pct = float(regression["max_increase_pct"])
    _default_metrics = ["total_tokens", "root_latency_ms", "cost_usd"]
    metric_names = [str(m) for m in regression.get("metrics", _default_metrics)]
    live = metrics.as_dict()
    out: list[Check] = []
    for metric in metric_names:
        base_val = base_metrics.get(metric)
        if base_val is None:
            out.append(Check(f"regression.{metric}", SKIP, "metric absent from baseline"))
            continue
        base_f, live_f = float(base_val), float(live.get(metric, 0.0))
        if base_f <= 0:
            out.append(Check(f"regression.{metric}", SKIP, "baseline value is zero"))
            continue
        change = (live_f - base_f) / base_f * 100.0
        if change <= pct:
            out.append(Check(f"regression.{metric}", PASS, f"{change:+.1f}% vs baseline (<= {pct:g}%)"))
        else:
            out.append(Check(f"regression.{metric}", FAIL, f"{change:+.1f}% vs baseline exceeds {pct:g}%"))
    return out


def collect_judge(spec: dict[str, Any]) -> list[Check]:
    judge = spec.get("judge") or {}
    out: list[Check] = []
    for crit in judge.get("criteria", []):
        cid = str(crit.get("id", "criterion"))
        out.append(Check(f"judge.{cid}", NEEDS_AGENT, str(crit.get("prompt", ""))))
    return out


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #

_GLYPH = {PASS: "[OK]  ", FAIL: "[FAIL]", SKIP: "[SKIP]", NEEDS_AGENT: "[?]   "}


def render_text(checks: list[Check], metrics: Metrics, ok: bool) -> str:
    lines = ["=== observent eval gate ===", ""]
    for c in checks:
        lines.append(f"  {_GLYPH.get(c.status, '[?]   ')} {c.name}: {c.message}")
    lines.append("")
    lines.append("  Metrics: " + json.dumps(metrics.as_dict()))
    lines.append("")
    lines.append(f"  {'PASS' if ok else 'FAIL'}")
    return "\n".join(lines)


def render_json(checks: list[Check], metrics: Metrics, ok: bool) -> str:
    return json.dumps(
        {
            "passed": ok,
            "metrics": metrics.as_dict(),
            "checks": [{"name": c.name, "status": c.status, "message": c.message} for c in checks],
        },
        indent=2,
    )


def render_junit(checks: list[Check], ok: bool) -> str:
    failures = sum(1 for c in checks if c.status == FAIL)
    skipped = sum(1 for c in checks if c.status in (SKIP, NEEDS_AGENT))
    rows = [
        f'<testsuite name="observent.eval_gate" tests="{len(checks)}" '
        f'failures="{failures}" skipped="{skipped}">'
    ]
    for c in checks:
        rows.append(f'  <testcase classname="observent.eval" name="{_xml_escape(c.name)}">')
        if c.status == FAIL:
            rows.append(f'    <failure message="{_xml_escape(c.message)}"/>')
        elif c.status in (SKIP, NEEDS_AGENT):
            rows.append(f'    <skipped message="{_xml_escape(c.message)}"/>')
        rows.append("  </testcase>")
    rows.append("</testsuite>")
    return "\n".join(rows)


_HTML_CSS = """
:root{--bg:#0f1117;--panel:#171a23;--line:#2a2f3c;--txt:#e6e8ee;--muted:#9aa3b2;
--green:#3fb950;--red:#f85149;--amber:#d29922;--blue:#6ea8fe;
--mono:'SFMono-Regular',Consolas,Menlo,monospace}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--txt);
font:15px/1.55 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}
.wrap{max-width:880px;margin:0 auto;padding:32px 20px 80px}
.banner{border-radius:12px;padding:18px 22px;margin-bottom:24px;font-weight:700;
font-size:20px;display:flex;align-items:center;gap:12px}
.banner.pass{background:rgba(63,185,80,.12);border:1px solid var(--green);color:var(--green)}
.banner.fail{background:rgba(248,81,73,.12);border:1px solid var(--red);color:var(--red)}
.sub{color:var(--muted);font-size:13px;margin-top:4px;font-weight:400}
h2{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);
margin:28px 0 12px;font-weight:600}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px}
.card .v{font-size:22px;font-weight:700;font-family:var(--mono)}
.card .k{font-size:12px;color:var(--muted);margin-top:4px}
table{width:100%;border-collapse:collapse;background:var(--panel);
border:1px solid var(--line);border-radius:10px;overflow:hidden}
td{padding:10px 14px;border-bottom:1px solid var(--line);font-size:14px;vertical-align:top}
tr:last-child td{border-bottom:none}
td.name{font-family:var(--mono);font-size:13px;white-space:nowrap}
td.msg{color:var(--muted)}
.badge{font-family:var(--mono);font-size:11px;font-weight:700;padding:2px 9px;
border-radius:5px;text-transform:uppercase}
.badge.pass{background:rgba(63,185,80,.15);color:var(--green)}
.badge.fail{background:rgba(248,81,73,.15);color:var(--red)}
.badge.skip{background:rgba(154,163,178,.15);color:var(--muted)}
.badge.needs-agent{background:rgba(110,168,254,.15);color:var(--blue)}
footer{margin-top:46px;color:var(--muted);font-size:12px;text-align:center}
"""


def render_html(checks: list[Check], metrics: Metrics, ok: bool) -> str:
    import html as _html
    from datetime import datetime as _dt

    m = metrics.as_dict()
    cards = "".join(
        f'<div class="card"><div class="v">{_html.escape(str(v))}</div>'
        f'<div class="k">{_html.escape(k)}</div></div>'
        for k, v in m.items()
    )
    rows = ""
    for c in checks:
        rows += (
            f'<tr><td class="name">{_html.escape(c.name)}</td>'
            f'<td><span class="badge {c.status}">{_html.escape(c.status)}</span></td>'
            f'<td class="msg">{_html.escape(c.message)}</td></tr>'
        )
    counts = {s: sum(1 for c in checks if c.status == s) for s in (PASS, FAIL, SKIP, NEEDS_AGENT)}
    verdict = "PASS" if ok else "FAIL"
    now = _dt.now().strftime("%Y-%m-%d %H:%M")
    # ASCII-only output: stdout redirect to a file uses the platform locale
    # (cp1252 on Windows), so non-ASCII separators would corrupt the utf-8 file.
    summary = (
        f"{counts[PASS]} passed | {counts[FAIL]} failed | "
        f"{counts[SKIP]} skipped | {counts[NEEDS_AGENT]} needs-agent"
    )
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<title>observent eval gate report</title>"
        f"<style>{_HTML_CSS}</style></head><body><div class=\"wrap\">"
        f'<div class="banner {verdict.lower()}">eval gate: {verdict}'
        f'<span class="sub">{_html.escape(summary)} | generated {now}</span></div>'
        f'<h2>Metrics</h2><div class="cards">{cards}</div>'
        f'<h2>Checks</h2><table>{rows}</table>'
        '<footer>observent eval gate -- self-contained report, no external assets</footer>'
        "</div></body></html>"
    )


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #


def run_checks(
    spec: dict[str, Any],
    spans: list[NormSpan],
    baseline: dict[str, Any] | None,
) -> tuple[list[Check], Metrics]:
    metrics = aggregate(spans, spec.get("cost_rates") or {})
    checks: list[Check] = []
    checks += check_budgets(spec, spans, metrics)
    checks += check_behavior(spec, spans, metrics)
    checks += check_redaction(spec, spans)
    checks += check_regression(spec, metrics, baseline)
    checks += collect_judge(spec)
    return checks, metrics


def is_passing(checks: list[Check], fail_on_unjudged: bool) -> bool:
    for c in checks:
        if c.status == FAIL:
            return False
        if c.status == NEEDS_AGENT and fail_on_unjudged:
            return False
    return True


def _write_baseline(path: Path, metrics: Metrics) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics.as_dict(),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="observent eval gate — assert budgets/behavior over spans.")
    parser.add_argument("--spec", required=True, type=Path, help="path to .observent/eval.json")
    parser.add_argument("--spans", required=True, type=Path, help="path to captured spans.jsonl")
    parser.add_argument("--baseline", type=Path, help="path to baseline.json for regression checks")
    parser.add_argument(
        "--format",
        choices=("text", "json", "junit", "html"),
        default="text",
        help="output format; 'html' emits a self-contained report (redirect to a .html file)",
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="write current metrics to --baseline (or spans-dir/baseline.json) and exit 0",
    )
    parser.add_argument(
        "--fail-on-unjudged",
        action="store_true",
        help="treat unresolved judge criteria (needs-agent) as failures",
    )
    args = parser.parse_args(argv)

    if not args.spec.is_file():
        raise SystemExit(f"eval_gate: spec not found: {args.spec}")
    if not args.spans.is_file():
        raise SystemExit(f"eval_gate: spans not found: {args.spans}")

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    spans = load_spans(args.spans)

    if args.update_baseline:
        metrics = aggregate(spans, spec.get("cost_rates") or {})
        target = args.baseline or (args.spans.parent / "baseline.json")
        _write_baseline(target, metrics)
        print(f"eval_gate: wrote baseline {target} -> {json.dumps(metrics.as_dict())}")
        return 0

    baseline: dict[str, Any] | None = None
    if args.baseline and args.baseline.is_file():
        baseline = json.loads(args.baseline.read_text(encoding="utf-8"))

    checks, metrics = run_checks(spec, spans, baseline)
    ok = is_passing(checks, args.fail_on_unjudged)

    if args.format == "json":
        print(render_json(checks, metrics, ok))
    elif args.format == "junit":
        print(render_junit(checks, ok))
    elif args.format == "html":
        print(render_html(checks, metrics, ok))
    else:
        print(render_text(checks, metrics, ok))

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
