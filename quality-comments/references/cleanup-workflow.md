# Cleanup Workflow: Flag and Ask

The procedure for removing comment noise from existing code without deleting anything the
user didn't agree to lose.

## Why this is a separate procedure

Generating a comment and deleting one carry very different risks. A bad new comment is
visible in the diff and costs a moment to fix. A deleted comment leaves no trace: the user
sees clean code, has no idea anything was removed, and only discovers the loss months later
when the constraint it recorded gets violated.

You also have less information than the comment's author did. A line that reads as pure
redundancy may be there because someone hit a bug, a reviewer demanded it, a compliance
process requires it, or it documents behavior of a system you can't see from this file.

So: propose, don't perform. Flagging costs one line of output. Getting a deletion wrong
costs information nobody can recover.

## The four steps

### 1. Categorize every candidate

Read the whole file first — a comment that looks redundant in isolation sometimes explains
something twenty lines away. Then group candidates by *kind*, not by location, so the user
can accept or reject in batches instead of adjudicating dozens of individual lines.

| Category | What it is | Default recommendation |
|---|---|---|
| Transliteration | Restates the line below it | Remove |
| Closing-brace label | `} // end for`, `# end if` | Remove |
| Byline / date stamp | `// Added by A. Kowalski, 2019` | Remove — git has it |
| Commented-out code | Disabled code with no explanation | Ask: restore, delete, or ticket it |
| Mumbling | Half-thought, ambiguous | Rewrite if the intent is recoverable, else ask |
| Ceremonial docstring | Mandated boilerplate on trivial members | Remove or make substantive |
| Stale | Contradicts current code | **Never auto-remove** — see step 4 |
| Section banner | `// ===== HELPERS =====` | Keep — navigation someone relies on. Propose splitting the file instead |
| Functional directive | `# noqa`, `//go:build`, shebang, license | **Never touch** |

### 2. Report

Line numbers, the text, and a short reason each. Keep reasons specific — "restates the
assignment below" beats "redundant" because the user can check it at a glance.

State counts up front so the scale is clear before the detail.

### 3. Show the proposed result

Show the rewritten region, not just a list of removals. Two reasons: the user is really
deciding whether the *result* reads well, and a diff of deletions makes it hard to see
whether anything of value survived.

If the cleanup revealed something worth documenting — a constraint the narration was
circling without stating — propose the replacement comment in the same pass. Removing six
noise comments and adding one real one is a better outcome than removing six.

### 4. Ask, then wait

End with a direct question and make no edits until answered. Offer the categories as the
unit of choice ("all of them", "everything but the commented-out block").

Handle these two cases separately from the delete pile:

- **Contradictions.** When a comment disagrees with the code, one of them is wrong, and
  which one matters enormously. `// retries 3 times` above `MAX_RETRIES = 5` is either a
  stale comment or a bug that just became visible. Report it as a question, never as a
  deletion.
- **Can't-tell cases.** If a comment might encode outside context — a business rule, a
  regulatory constraint, a reference to a system not in this repo — say so and leave it out
  of the recommendation. Uncertainty reported is useful; a confident wrong deletion isn't.

## When to skip the asking

The rule exists to prevent *unrequested* deletion, not to nag. Go ahead without asking when:

- The user already said to strip redundant comments without checking in, in this session.
- You are removing comments you wrote yourself earlier in this same session.
- The comments are inside a block you are rewriting wholesale at the user's request, and
  they describe code that no longer exists.

Even then, say what came out in a single summary line. The user should never learn about a
deletion by noticing an absence.

## Worked example

**Input** (`orders.py`, 22 lines, 11 comments):

```python
# Order processing module
# Added by A. Kowalski 2019-03-04

import datetime

# function to process orders
def process_orders(orders, tax_rate):
    # create empty list
    results = []
    # loop through orders
    for o in orders:
        # skip if cancelled
        if o.status == "cancelled":
            continue  # skip it
        # calculate total
        total = o.subtotal * (1 + tax_rate)
        # round to 2 places
        total = round(total, 2)
        # add to results
        results.append((o.id, total))
    # end for
    # return the results
    return results

# def process_orders_v2(orders):
#     return [(o.id, o.subtotal) for o in orders]
```

**Report:**

> Found 11 comments in `orders.py`; 10 look removable and 1 needs your call.
>
> **Transliteration (7)** — each restates the line below it:
> - L6 `# function to process orders` — the `def` line says this
> - L8 `# create empty list` — restates `results = []`
> - L10 `# loop through orders` — restates the `for`
> - L12 `# skip if cancelled` — restates the `if o.status == "cancelled"`
> - L14 `# skip it` — restates `continue`
> - L17 `# round to 2 places` — restates `round(total, 2)`
> - L19 `# add to results` — restates `results.append(...)`
>
> **Closing-brace label (1)**
> - L21 `# end for` — Python has no closing brace; the dedent is the marker
>
> **Byline (1)**
> - L2 `# Added by A. Kowalski 2019-03-04` — `git log` has this, accurately
>
> **Redundant summary (1)**
> - L22 `# return the results` — restates `return results`
>
> **Needs your call (1)**
> - L26–27, commented-out `process_orders_v2` — a different implementation that drops tax
>   entirely. I can't tell if it's abandoned, a work in progress, or a rollback path. Delete
>   it (git keeps the history), or should it become a `TODO` with the condition for
>   finishing it?
>
> One thing worth **adding**: L16 rounds after applying tax, which is a real decision —
> rounding per-line versus on the order total gives different figures, and finance systems
> usually mandate one. If you know which rule applies, that's the comment this file is
> actually missing.
>
> Proposed result:
>
> ```python
> """Order total calculation."""
>
> def process_orders(orders, tax_rate):
>     """Return (order_id, taxed_total) for every non-cancelled order.
>
>     Args:
>         orders: Order records; those with status "cancelled" are skipped.
>         tax_rate: Fractional rate, e.g. 0.08 for 8%. Applied to subtotal.
>
>     Returns:
>         List of (id, total) tuples, rounded to 2 decimal places, in input order.
>     """
>     results = []
>     for o in orders:
>         if o.status == "cancelled":
>             continue
>         # Rounded per-order after tax, not per-line-item — matches the invoice totals
>         # the finance export expects.
>         total = round(o.subtotal * (1 + tax_rate), 2)
>         results.append((o.id, total))
>     return results
> ```
>
> Apply all 10 removals? Or pick categories — happy to keep any of them.

Note what the report does: it never touches the file, it gives the user a category-level
decision rather than eleven line-level ones, it separates the one genuinely ambiguous item
from the obvious ones, and it converts the noise into one comment that actually carries
information — flagged as a proposal, since the rounding rule is a claim about the business
that only the user can confirm.
