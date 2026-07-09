#!/usr/bin/env python3
"""observent SessionStart hook — detect frameworks/backends and prime the session.

Runs the bundled ``detect_framework.py`` (its sibling in this directory) against
the current project and, when any agent framework or observability backend is
found, injects a one-paragraph summary plus a pointer to ``/observent`` into the
session context.

Wired up as a plugin hook via ``.claude-plugin/plugin.json``. Zero third-party
deps (stdlib only). Fail-safe by construction: a missing detector, a non-zero
exit, malformed JSON, or an empty result all exit 0 with no output, so the hook
can never block or visibly slow a session.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any


def main() -> int:
    try:
        payload: Any = json.load(sys.stdin)
    except Exception:
        return 0

    cwd = payload.get("cwd") or os.getcwd()
    detector = os.path.join(os.path.dirname(os.path.abspath(__file__)), "detect_framework.py")
    if not os.path.isfile(detector):
        return 0

    try:
        proc = subprocess.run(
            [sys.executable, detector],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=12,
        )
    except Exception:
        return 0

    if proc.returncode != 0 or not proc.stdout.strip():
        return 0

    try:
        report: Any = json.loads(proc.stdout)
    except Exception:
        return 0

    frameworks = [str(f.get("name", "?")) for f in report.get("frameworks", [])]
    backends = [str(b.get("name", "?")) for b in report.get("backends", [])]
    if not frameworks and not backends:
        # Nothing observability-relevant in this project — stay silent.
        return 0

    docker = report.get("docker", {}) or {}
    lines = [
        "observent detected this project's observability surface:",
        f"- Agent frameworks: {', '.join(sorted(frameworks)) or 'none'}",
        f"- Observability backends: {', '.join(sorted(backends)) or 'none'}",
    ]
    if docker.get("compose_available"):
        lines.append(
            "- Docker Compose is available — observent can provision an "
            "unreachable self-host backend locally if asked."
        )
    lines.append(
        "Run /observent [framework] [backend] to wire up tracing "
        "(or /observent-detect for the full report)."
    )

    out = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(lines),
        }
    }
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
