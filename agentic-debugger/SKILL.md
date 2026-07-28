---
name: agentic-debugger
description: Reproduce a bug before fixing it, then verify the fix with a guarded test run. Use when a developer hits a runtime error, a failing test, or "almost right" AI-generated code that behaves wrong.
---

# Agentic Debugger

A debugging skill built on one rule: never fix blind. Parse the traceback, build a minimal reproduction, apply the smallest possible fix, then prove the fix with a guarded test run — so every bug fix ships with evidence instead of vibes.

## When to Use This Skill

- A runtime traceback or stack trace was pasted into the chat
- A test is red and the cause is unclear
- AI-generated code "looks about right" but behaves wrong at runtime
- You want a red-before / green-after proof that a fix actually works

## What This Skill Does

1. **Parses the trace**: extracts the exception type, the failing `file:line`, and the call frames from a pasted stack trace, so the hypothesis starts at the deepest frame.
2. **Builds a minimal repro**: generates a pytest reproduction skeleton targeting the enclosing function of the failing line — a bug you cannot reproduce is a bug you cannot prove you fixed.
3. **Guards the fix**: runs the repro and the project's full test suite through a guarded runner with clear PASS/FAIL output and install hints when the test tool is missing.

## How to Use

### Basic Usage

```
Debug this error: <paste your traceback here>
```

Claude will parse the trace, write `test_repro.py` next to the failing source, confirm it is RED, apply the smallest fix, and re-run until green.

### Advanced Usage

```
The test suite in tests/ fails after my refactor. Use the agentic-debugger loop:
reproduce the failure first, keep the fix minimal, then run the full suite to
check for regressions.
```

All helper scripts live in `scripts/` and run on the Python standard library only — no pip installs:

```bash
python scripts/parse_trace.py --file trace.txt        # locate the failing frame
python scripts/make_repro.py --file src/calc.py --line 2 --test-cmd "pytest tests/ -q"
python scripts/run_guard.py pytest test_repro.py -q   # guarded verify
```

## Example

**User**: "My division helper crashes: ZeroDivisionError: division by zero at calc.py:2 in divide. Fix it."

**Output**:
```
=== Trace Report (agentic-debugger) ===
Exception : ZeroDivisionError: division by zero
Location  : calc.py:2 in divide

[make_repro] wrote test_repro.py  -> RED (reproduced)
Fix: guard the zero divisor in divide()
=== Run Guard (agentic-debugger) ===
Status  : PASS (exit 0)           -> GREEN (verified)
```

**Inspired by:** the reproduce-first debugging discipline from [Novera-AI-skills](https://github.com/whaojie797-design/Novera-AI-skills), where this skill is actively maintained with additional references.

## Tips

- Start the hypothesis from the deepest frame in the trace, not the topmost one
- If the fix touches three files, you are probably solving the wrong problem — narrow it
- After the repro turns green, always run the project's full suite to catch regressions
- Do not pile on more changes while a test stays red; revisit the hypothesis instead

## Common Use Cases

- Turning a pasted production traceback into a verified, minimal fix
- Repairing AI-generated code that compiles but fails at runtime
- Confirming a refactor did not change behavior (red-before / green-after evidence)
- Adding a regression test for every fixed bug so it never comes back
