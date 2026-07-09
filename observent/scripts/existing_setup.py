#!/usr/bin/env python3
"""Detect pre-existing observability configuration in the user's project.

Greps for imports, env var references, and OTel TracerProvider setup.
Reports which backend(s) appear to be already configured so SKILL.md can
offer extend-vs-replace instead of blindly overwriting.

Output: JSON to stdout. When run from the observent repo itself,
``self_scan_excluded`` is true and ``skills/observent/`` is skipped to
suppress false-positive matches against the skill's own scripts.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

# Each entry has a `kind`: "backend" (Phoenix/Langfuse/SigNoz) or
# "instrumentation" (OpenTelemetry SDK / OpenInference instrumentors).
# Consumers should treat them differently — e.g., a project that uses the
# OpenTelemetry SDK isn't necessarily wired to any specific backend.
IMPORT_PATTERNS: dict[str, dict[str, Any]] = {
    "phoenix": {
        "kind": "backend",
        "patterns": [
            re.compile(r"^\s*(?:from|import)\s+phoenix\b"),
            re.compile(r"^\s*(?:from|import)\s+arize_phoenix\b"),
            re.compile(r"\bphoenix\.otel\.register\b"),
            re.compile(r"\bpx\.launch_app\b"),
        ],
    },
    "langfuse": {
        "kind": "backend",
        "patterns": [
            re.compile(r"^\s*(?:from|import)\s+langfuse\b"),
            re.compile(r"\blangfuse\.langchain\b"),
            re.compile(r"\blangfuse\.decorators\b"),
            re.compile(r"\bCallbackHandler\b.*langfuse"),
        ],
    },
    "signoz": {
        "kind": "backend",
        # Restrict to high-signal patterns. A bare mention of "signoz" in a
        # comment/README/dep-name is not enough to claim the project is wired
        # up; require the auth header, a signoz.cloud endpoint, or an OTLP
        # exporter pointed at a SigNoz host.
        "patterns": [
            re.compile(r"signoz-access-token", re.IGNORECASE),
            re.compile(r"\bsignoz\.cloud\b", re.IGNORECASE),
            re.compile(r"OTLPSpanExporter\([^)]*signoz", re.IGNORECASE | re.DOTALL),
        ],
    },
    "opentelemetry": {
        "kind": "instrumentation",
        "patterns": [
            re.compile(r"^\s*(?:from|import)\s+opentelemetry\b"),
            re.compile(r"\bTracerProvider\(\)"),
            re.compile(r"\bBatchSpanProcessor\("),
            re.compile(r"\bOTLPSpanExporter\("),
        ],
    },
    "openinference": {
        "kind": "instrumentation",
        "patterns": [
            re.compile(r"^\s*(?:from|import)\s+openinference\b"),
        ],
    },
}

ENV_VAR_PATTERNS: dict[str, re.Pattern[str]] = {
    "phoenix": re.compile(r"\bPHOENIX_(?:API_KEY|COLLECTOR_ENDPOINT|PROJECT_NAME)\b"),
    "langfuse": re.compile(r"\bLANGFUSE_(?:PUBLIC_KEY|SECRET_KEY|HOST)\b"),
    "signoz": re.compile(r"\bSIGNOZ_(?:ENDPOINT|INGESTION_KEY)\b"),
    "opentelemetry": re.compile(r"\bOTEL_(?:EXPORTER_OTLP_ENDPOINT|SERVICE_NAME|RESOURCE_ATTRIBUTES)\b"),
}

EXCLUDE_PARTS = {
    ".git", ".venv", "venv", "env", "__pycache__", "node_modules",
    ".tox", ".mypy_cache", ".ruff_cache", ".claude",
}
SCAN_SUFFIXES = {".py", ".env", ".sh", ".yaml", ".yml", ".toml", ".cfg", ".ini"}


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _scan_file(path: Path, hits: dict[str, dict[str, list[str]]]) -> None:
    text = _read(path)
    if not text:
        return
    for name, spec in IMPORT_PATTERNS.items():
        for pat in spec["patterns"]:
            if pat.search(text):
                hits[name]["imports"].append(str(path))
                break
    for name, pat in ENV_VAR_PATTERNS.items():
        if pat.search(text):
            hits[name]["env_vars"].append(str(path))
    # Look for env files specifically
    if path.name.startswith(".env") or path.suffix == ".env":
        for name, pat in ENV_VAR_PATTERNS.items():
            if pat.search(text):
                hits[name]["env_files"].append(str(path))


def scan(root: Path, max_files: int = 500) -> dict[str, Any]:
    hits: dict[str, dict[str, list[str]]] = {
        name: {"imports": [], "env_vars": [], "env_files": []}
        for name in IMPORT_PATTERNS.keys()
    }
    # Self-scan guard: when run from the observent repo root, skip its own
    # skill tree so the OpenTelemetry imports inside validate_setup.py and
    # the example markdown don't produce a false "opentelemetry detected".
    self_scan = (root / "skills" / "observent" / "SKILL.md").is_file()
    self_skip_root = (root / "skills" / "observent") if self_scan else None
    count = 0
    truncated = False
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDE_PARTS for part in path.parts):
            continue
        if path.suffix not in SCAN_SUFFIXES and not path.name.startswith(".env"):
            continue
        if self_skip_root is not None:
            try:
                path.relative_to(self_skip_root)
                continue
            except ValueError:
                pass
        if count >= max_files:
            truncated = True
            break
        count += 1
        _scan_file(path, hits)

    detected = []
    for name, found in hits.items():
        if any(found.values()):
            detected.append({
                "name": name,
                "kind": IMPORT_PATTERNS[name]["kind"],
                "imports": sorted(set(found["imports"]))[:10],
                "env_vars_in_files": sorted(set(found["env_vars"]))[:10],
                "env_files": sorted(set(found["env_files"]))[:10],
                "instrumentation_code_found": bool(found["imports"]),
            })

    # "Scaffolded but never implemented": env-var names/config exist from an
    # earlier attempt, but zero instrumentation code was ever written for any
    # detected entry. Distinct from both "extend" (nothing working to extend)
    # and "replace" (no working code to overwrite) in SKILL.md Step 1.4.
    any_code = any(e["imports"] for e in detected)
    any_config = any(e["env_vars_in_files"] or e["env_files"] for e in detected)
    scaffold_only = bool(detected) and not any_code and any_config

    return {
        "cwd": str(root),
        "files_scanned": count,
        "files_truncated": truncated,
        "self_scan_excluded": self_scan,
        "detected": detected,
        "scaffold_only": scaffold_only,
    }


def main() -> int:
    report = scan(Path.cwd())
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
