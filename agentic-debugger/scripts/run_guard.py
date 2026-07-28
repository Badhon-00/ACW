#!/usr/bin/env python3
"""Run a test/command and report a pass/fail summary.

Captures stdout/stderr of the given command, counts failed/passed cases
when detectable, and prints a clear summary. If the command is missing,
prints an install hint instead of a cryptic error.

Pure Python standard library. Deterministic for a given command + output.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from typing import List, Optional

INSTALL_HINTS = {
    "pytest": "pip install pytest",
    "py.test": "pip install pytest",
    "tox": "pip install tox",
    "jest": "npm install --save-dev jest",
    "npm": "install Node.js from https://nodejs.org",
    "go": "install Go from https://go.dev",
    "cargo": "install Rust from https://rustup.rs",
    "mvn": "install Maven from https://maven.apache.org",
    "gradle": "install Gradle from https://gradle.org",
}


def count_pattern(text: str, pattern: str) -> Optional[int]:
    m = re.search(pattern, text)
    return int(m.group(1)) if m else None


def first_error(text: str) -> str:
    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
    markers = ("Error", "Exception", "assert", "FAILED",
               "AssertionError", "Error:")
    for i, ln in enumerate(lines):
        if any(mk in ln for mk in markers):
            window = lines[max(0, i - 1) : i + 3]
            return "\n".join(window)
    return lines[-1] if lines else "(no error detail captured)"


def summarize(proc: subprocess.CompletedProcess, command: List[str]) -> dict:
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    failed = count_pattern(out, r"(\d+)\s+failed")
    passed = count_pattern(out, r"(\d+)\s+passed")
    errored = count_pattern(out, r"(\d+)\s+error")
    rc = proc.returncode

    if rc == 0:
        status = "PASS"
    elif failed is not None and failed > 0:
        status = "FAIL"
    elif errored is not None and errored > 0:
        status = "ERROR"
    else:
        status = "FAIL" if rc != 0 else "PASS"

    missing = None
    if "No module named" in (proc.stderr or ""):
        mm = re.search(r"No module named ['\"]?([\w.]+)", proc.stderr)
        if mm and mm.group(1) in INSTALL_HINTS:
            missing = INSTALL_HINTS[mm.group(1)]
        elif mm:
            missing = f"pip install {mm.group(1)}"

    return {
        "command": " ".join(command),
        "status": status,
        "returncode": rc,
        "failed": failed,
        "passed": passed,
        "errors": errored,
        "first_error": first_error(out) if status != "PASS" else "",
        "install_hint": missing,
    }


def print_summary(report: dict) -> None:
    print("=== Run Guard (agentic-debugger) ===")
    print(f"Command : {report['command']}")
    print(f"Status  : {report['status']} (exit {report['returncode']})")
    if report["passed"] is not None:
        print(f"Passed  : {report['passed']}")
    if report["failed"] is not None:
        print(f"Failed  : {report['failed']}")
    if report["errors"] is not None and report["errors"]:
        print(f"Errors  : {report['errors']}")
    if report["first_error"]:
        print("-" * 58)
        print("First error:")
        print(report["first_error"])
    if report["install_hint"]:
        print("-" * 58)
        print(f"Missing dependency. Install with: {report['install_hint']}")
    print("=" * 58)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a test command and summarize pass/fail."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args, rest = parser.parse_known_args(argv)

    command = [c for c in rest if c]
    if not command:
        sys.exit(
            "[run_guard] no command given. Example: "
            "run_guard.py pytest tests/ -q"
        )

    try:
        proc = subprocess.run(command, capture_output=True, text=True)
    except FileNotFoundError:
        name = command[0]
        hint = INSTALL_HINTS.get(name)
        print("=== Run Guard (agentic-debugger) ===")
        print(f"Command not found: {name}")
        if hint:
            print(f"Install with: {hint}")
        else:
            print("Ensure the command is installed and on your PATH.")
        print("=" * 58)
        if args.json:
            print(json.dumps(
                {"status": "MISSING", "command": " ".join(command),
                 "install_hint": hint},
                ensure_ascii=False, indent=2,
            ))
        return 2

    report = summarize(proc, command)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_summary(report)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
