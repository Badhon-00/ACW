#!/usr/bin/env python3
"""observent UserPromptSubmit hook — nudge toward /observent on clear intent.

When a prompt clearly expresses observability intent (tracing, telemetry, a
named backend, etc.) and the user is not already invoking observent, this
injects a short reminder that the ``/observent`` workflow exists.

To avoid nagging, it nudges at most once per session: a marker file keyed by
session id is written to the system temp dir on first nudge and short-circuits
subsequent prompts. Zero third-party deps. Fail-safe: any error exits 0 with no
output, so a prompt is never blocked or delayed.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

# Curated intent keywords — kept tight to avoid false positives. The skill's own
# auto-invocation already handles strong matches; this is a lightweight backstop.
_KEYWORDS = (
    "observability",
    "tracing",
    "telemetry",
    "opentelemetry",
    "otel",
    "openinference",
    "instrument",
    "span",
    "phoenix",
    "langfuse",
    "signoz",
    "elastic apm",
    "langsmith",
    "opik",
    "jaeger",
)


def _already_nudged(session_id: str) -> bool:
    if not session_id:
        return False
    marker = os.path.join(tempfile.gettempdir(), f"observent-nudge-{session_id}")
    if os.path.exists(marker):
        return True
    try:
        with open(marker, "w", encoding="utf-8") as fh:
            fh.write("1")
    except Exception:
        # If we cannot persist the marker, fail open and allow this one nudge.
        pass
    return False


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    prompt = (payload.get("prompt") or "").lower()
    if not prompt:
        return 0

    # Already an observent command — nothing to nudge.
    if "/observent" in prompt or "observent" in prompt:
        return 0

    if not any(kw in prompt for kw in _KEYWORDS):
        return 0

    if _already_nudged(payload.get("session_id", "")):
        return 0

    out = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": (
                "observent tip: this project has the observent plugin installed. "
                "For wiring up multi-agent LLM tracing, the /observent workflow "
                "(detect -> spec -> plan -> implement -> validate) generates the "
                "correct span hierarchy, mandatory attributes, and context "
                "propagation for the chosen backend. Suggest it if it fits the "
                "user's request."
            ),
        }
    }
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
