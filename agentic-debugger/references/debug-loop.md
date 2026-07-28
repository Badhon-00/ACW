# The repro-first debugging loop

This skill treats debugging as a closed loop, not a one-shot edit. The order
matters: locate, reproduce, fix minimally, verify, regress.

## Steps

### 1. Form a hypothesis

Run `scripts/parse_trace.py` on the trace. The deepest frame is where the
exception was raised. Name the cause in one sentence before touching code:

> "X is None here because the loader skips empty rows."

A written hypothesis is cheap and keeps the later fix窄 (narrow).

### 2. Write a reproduction test

Run `scripts/make_repro.py` to scaffold `test_repro.py` at the reported line.
Replace the placeholder inputs with the minimal arguments that drive the code
to the failing line. Run it and confirm it is RED.

A bug you cannot reproduce is a bug you cannot prove you fixed. If you cannot
build a repro, say so explicitly instead of guessing a fix.

### 3. Apply the minimal fix

Edit only what the hypothesis requires. If the fix needs three lines, that is
fine; if it needs three files, you are probably solving the wrong problem.
One change per iteration so the green result is attributable.

### 4. Verify with run_guard

Run `scripts/run_guard.py` on the repro. Green is the only accepted outcome.
If it stays red, the hypothesis was wrong — go back to step 1. Do not pile on
more changes hoping something sticks.

### 5. Regression check

Run the project's full test command through `run_guard`. New reds mean the
fix bled into other behavior; shrink it until only the intended change remains.

## Anti-patterns

- **Fixing without reproducing.** Editing code because "it looks wrong"
  produces changes you cannot verify and regressions you cannot see.
- **Changing many things at once.** If the test goes green you will not know
  which change mattered, and the unrelated edits become future bugs.
- **Asserting away the failure.** Replacing a real assertion with one that
  always passes hides the bug instead of fixing it.
- **Trusting the message over the trace.** The exception text is a clue, not
  the verdict. The deepest frame is the source of truth.
- **Stopping at one green test.** A single repro going green while the suite
  goes red is not done.
