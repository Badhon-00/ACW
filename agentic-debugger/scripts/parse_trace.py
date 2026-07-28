#!/usr/bin/env python3
"""Parse a runtime error or stack trace into a structured report.

Reads trace text from standard input or a file, extracts the failing
file:line location, the exception type and message, and the call frames,
then prints a human-readable table or JSON.

Pure Python standard library. Same input always yields the same output.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from typing import List, Optional

# Whitelist of source-file extensions used by the generic path:line matcher
# so we do not mistake floats (e.g. "0.5:10") or URLs for stack frames.
SRC_EXT = (
    r"py|js|jsx|ts|tsx|java|go|rb|rs|cpp|c|cc|h|hpp|cs|php|m|swift|"
    r"kt|scala|sh|sql|html|css"
)

# Python:  File "/path/file.py", line 10, in func
PY_FRAME_RE = re.compile(r'File "([^"]+)", line (\d+)(?:, in (.+))?')
# Node/JS: at func (/path/file.js:12:5)
NODE_FRAME_RE = re.compile(r"\(([^()]+?\.(?:" + SRC_EXT + r")):(\d+):(\d+)\)")
# Generic:  /path/file.ext:123
GENERIC_RE = re.compile(r"([^\s\"'()]*\.(?:" + SRC_EXT + r")):(\d+)")
# Exception line:  SomeError: message
EXC_RE = re.compile(r"^([A-Z][A-Za-z0-9_.]*)\s*:\s*(.+)$")


@dataclass
class Frame:
    path: str
    line: int
    func: Optional[str] = None
    col: Optional[int] = None


@dataclass
class TraceReport:
    exception_type: Optional[str] = None
    exception_message: str = ""
    failed_location: Optional[str] = None
    frames: List[Frame] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "exception_type": self.exception_type,
            "exception_message": self.exception_message,
            "failed_location": self.failed_location,
            "frame_count": len(self.frames),
            "frames": [
                {"path": f.path, "line": f.line, "func": f.func, "col": f.col}
                for f in self.frames
            ],
        }


def parse_trace(text: str) -> TraceReport:
    """Scan trace text and build a TraceReport."""
    report = TraceReport()
    lines = text.splitlines()
    for line in lines:
        m = PY_FRAME_RE.search(line)
        if m:
            report.frames.append(
                Frame(path=m.group(1), line=int(m.group(2)), func=m.group(3))
            )
            continue
        m = NODE_FRAME_RE.search(line)
        if m:
            report.frames.append(
                Frame(path=m.group(1), line=int(m.group(2)), col=int(m.group(3)))
            )
            continue
        # Python frame already captured above; skip its raw "File " form.
        if 'File "' in line:
            continue
        m = GENERIC_RE.search(line)
        if m:
            report.frames.append(Frame(path=m.group(1), line=int(m.group(2))))

    # Exception line: last non-frame line that looks like "Type: message".
    for line in reversed(lines):
        stripped = line.strip()
        if stripped.startswith("Traceback"):
            continue
        if (
            PY_FRAME_RE.search(line)
            or NODE_FRAME_RE.search(line)
            or GENERIC_RE.search(line)
        ):
            continue
        m = EXC_RE.match(stripped)
        if m:
            report.exception_type = m.group(1)
            report.exception_message = m.group(2).strip()
            break

    if report.frames:
        last = report.frames[-1]
        loc = f"{last.path}:{last.line}"
        if last.func:
            loc += f" in {last.func}"
        report.failed_location = loc
    return report


def print_table(report: TraceReport) -> None:
    print("=== Trace Report (agentic-debugger) ===")
    exc = report.exception_type or "(unknown)"
    if report.exception_message:
        exc += f": {report.exception_message}"
    print(f"Exception : {exc}")
    print(f"Location  : {report.failed_location or '(unknown)'}")
    print(f"Frames    : {len(report.frames)}")
    if report.frames:
        print("-" * 58)
        print(f"{'#':<4}{'File':<34}{'Line':<7}Function")
        print("-" * 58)
        for i, f in enumerate(report.frames, 1):
            path = f.path if len(f.path) <= 32 else "..." + f.path[-29:]
            func = f.func or ""
            if f.col is not None:
                func = f"{func}:{f.col}" if func else f":{f.col}"
            print(f"{i:<4}{path:<34}{f.line:<7}{func}")
    print("=" * 58)


def read_input(args: argparse.Namespace) -> str:
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as fh:
                return fh.read()
        except OSError as exc:
            sys.exit(f"[parse_trace] cannot read file {args.file!r}: {exc}")
    if sys.stdin.isatty():
        sys.exit(
            "[parse_trace] no input. Pipe trace text via stdin "
            "(e.g. cat err.log | parse_trace.py) or pass --file <path>."
        )
    return sys.stdin.read()


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Parse an error/stack trace into a structured report."
    )
    parser.add_argument("--file", help="Path to a file containing the trace text.")
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table).",
    )
    args = parser.parse_args(argv)

    text = read_input(args)
    report = parse_trace(text)

    if args.format == "json":
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print_table(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
