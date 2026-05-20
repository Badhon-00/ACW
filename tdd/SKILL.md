---
name: tdd
description: Test-driven development cycle — red test first, minimal green, refactor only inside scope. Never write production code before a failing test.
---

# TDD — Test-Driven Development

Strict red/green/refactor cycle. Prevents over-engineering, ensures every line of code has a test, and keeps commits small and verifiable.

## When to Use This Skill

- Adding new behavior with clear inputs and outputs
- Any logic that could be unit tested
- When you want to commit with confidence

## The Cycle

1. **Write the failing test first.** Run it. Confirm it fails with the expected error — `ImportError`, `AssertionError`, not a crash or syntax error.
2. **Write the minimum code to pass.** No extra logic, no preemptive abstractions.
3. **Run the test.** Green → commit → next test. Red → fix only what the test says.

## Rules

- Never write production code before the red test exists (unless explicitly exempted).
- Each test names a behavior, not an implementation detail.
- Refactor only inside touched paths, and only after green.
- Run the focused test after every change — not the full suite until you're done.
- Commit each green state. Never batch test + implementation into one commit.

## MCP/Hook Testing Pattern

When testing code that calls external tools or hooks, mock at the call boundary — not deep inside the implementation:

```python
from unittest.mock import patch

def test_behavior_calls_tool(tmp_path):
    with patch("mymodule.external_call") as mock_call:
        mock_call.return_value = {"status": "ok"}
        result = my_behavior("arg")
    mock_call.assert_called_once_with("expected_arg")
```

## Tips

- The failing test is the spec. If you can't write a test, you don't have a clear enough requirement.
- "Minimum code to pass" means embarrassingly minimal — no error handling for cases not yet tested.
- The refactor phase is where you clean up. Resist the urge to clean up during green.
