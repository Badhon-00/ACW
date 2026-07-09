#!/usr/bin/env python3
"""observent PostToolUse hook — syntax-check generated observent helpers.

After an Edit/Write/MultiEdit, if the touched file is one of observent's own
generated Python helpers (``observent_*.py`` — e.g. ``observent_otel.py``,
``observent_capture.py``, ``observent_http.py``), this compiles its source to
catch syntax errors immediately, surfacing any failure back to Claude so it can
fix it in the same turn.

Scope is intentionally narrow (only ``observent_*.py``) so it never interferes
with the user's own files. Zero third-party deps; uses the stdlib ``compile``
builtin (no ``.pyc`` written, no subprocess). Fail-safe: anything other than a
real syntax error in an observent file exits 0 silently.
"""
from __future__ import annotations

import json
import os
import sys


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or ""
    if not file_path:
        return 0

    base = os.path.basename(file_path)
    # Only validate observent's own generated helpers.
    if not (base.startswith("observent_") and base.endswith(".py")):
        return 0

    if not os.path.isfile(file_path):
        return 0

    try:
        with open(file_path, encoding="utf-8") as fh:
            source = fh.read()
    except Exception:
        return 0

    try:
        compile(source, file_path, "exec")
    except SyntaxError as exc:
        # Surface to Claude via stderr + exit 2 so it self-corrects this turn.
        location = f"{base}:{exc.lineno}" if exc.lineno else base
        sys.stderr.write(
            f"observent: generated file {location} has a syntax error: "
            f"{exc.msg}. Fix it before continuing.\n"
        )
        return 2
    except Exception:
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
