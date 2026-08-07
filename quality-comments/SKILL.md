---
name: quality-comments
description: Write code comments that explain why, not what, and clean up comments that don't. Use whenever writing, reviewing, refactoring, or documenting code, and proactively before emitting any non-trivial code block (more than a few lines, or any public function, class, or exported type) even when comments were never mentioned - over-commenting is the default failure and this prevents it. Also use whenever comments, docstrings, JSDoc, Javadoc, XML doc comments, rustdoc, godoc, header comments, or TODO/FIXME/HACK/XXX/NOTE tags come up, and for requests like "document this function", "add comments", "too many comments here", or "clean up the comments". Covers doc-comment contracts for public APIs, inline why-comments for maintainers, per-language conventions (Python, JS/TS, Go, Rust, Java, C#, C/C++, Swift, Ruby, PHP, shell), task-tag quality standards, and a flag-and-ask workflow for removing redundant comments without ever deleting them unasked.
---

# Quality Comments

Comments compete with code for attention. Every one that says nothing makes the next less
likely to be read — including the one that would have prevented an outage. Write few; make
each carry what the code cannot.

## The core rule: comment the why, not the what

Code already states what it does. Restating it in English produces a second, less precise
copy that has to be maintained in parallel, and that will eventually contradict the first.

**The redundancy test — delete the comment.** If nothing is lost, if a competent reader of
this language recovers the same information from the code in a couple of seconds, leave it
deleted.

```js
// increment the counter                                 ← delete: the code says this
counter++;

// API pages are 1-indexed; the off-by-one is deliberate ← keep: unrecoverable from code
counter++;
```

A comment earns its place by carrying something absent from the syntax: a constraint from
outside the codebase, a trade-off considered and rejected, a bug in someone else's system
being worked around, an invariant the compiler can't check, a unit or a range, an ordering
another module depends on.

**On "what" comments.** The thing to avoid is *transliteration* — restating a line at the
same altitude as the line. A comment that summarizes twenty lines in one sentence sits
*above* the code's altitude and is genuinely useful; it lets a reader skip the block.
Altitude is the test, not the word "what".

**Refactor first, comment second.** When a comment exists to explain a confusing name or a
tangled expression, fix the code instead — a better name can't rot out of sync with itself.
But don't over-apply this: "good code is self-documenting" is only half true. No renaming
conveys *why* the retry limit is 3, that a vendor returns HTTP 200 on failure, or what a
module promises its callers. When the information genuinely cannot live in the code, write
the comment and don't feel bad about it.

## Interface vs. implementation

Two kinds of comments exist, aimed at two different readers. Most commenting mistakes are a
failure to keep them apart — implementation detail leaking into a public contract, or doc
comment ceremony applied to a two-line private helper.

| | **Interface** (doc comments) | **Implementation** (inline comments) |
|---|---|---|
| Reader | Someone calling this without reading the body | Someone changing the body |
| Answers | "What can I rely on?" | "Why is it like this?" |
| Location | Immediately above the declaration | Immediately above the statements it describes |
| Changes when | The contract changes | The local implementation changes |
| Never contains | Private fields, internal data structures, helper names | Restatement of the syntax below it |

### Interface documentation — the contract

Write one on anything reachable without reading the source: exported and public functions,
methods, classes, modules, and non-obvious types. Cover only what a caller needs in order to
use it correctly:

- **Behavior** — what it does in the caller's terms, not the algorithm's.
- **Parameters** — meaning, *units and ranges*, and what null/empty/zero signify.
  `timeoutMs` needs "must be > 0; 0 would busy-loop" far more than it needs "the timeout".
- **Returns** — semantics, including the empty and absent cases. "Returns null when the
  user has no active session" outweighs the rest of the sentence.
- **Errors** — what it throws or returns as an error, under which conditions, and whether
  the operation is safe to retry.
- **Preconditions and side effects** — required state or call ordering, argument mutation,
  I/O, locks acquired.

Skip whatever the signature already states. In a typed language, `@param userId — the user
ID as a string` is noise; `@param userId — canonical UUID, not the legacy integer ID` is the
contract. Keep the first line a standalone one-sentence summary: tools display it alone in
tooltips and index pages, so it has to work without the rest.

### Implementation comments — a map through the tricky parts

Most short functions need none. Add them where a maintainer would otherwise have to
reconstruct your reasoning from scratch:

- A block of nontrivial logic gets a one-line header naming what the block accomplishes, so
  a reader can skip it if it isn't what they came for.
- A workaround gets its reason — the upstream bug, vendor quirk, or platform limitation.
  Without it, the next person "cleans it up" and reintroduces the bug.
- Nonobvious math, bit manipulation, magic constants, and regexes get a worked example.
- Anything surprising gets a warning *before* someone is surprised by it in production.

## When not to comment

Each of these is common, and each damages the codebase in a specific way.

- **Transliteration.** `// loop through the users` above `for (const user of users)`. Takes
  longer to read than what it describes; this is what trains people to skip comments.
- **Closing-brace labels.** `} // end if`, `} // end for`. If a block is long enough to
  need one, the fix is a shorter block — and the label rots silently when nesting changes.
- **Bylines and change logs.** `// Added by A. Kowalski 2019-03-04`,
  `// Modified: see changelog`. Version control knows who and when, and knows it accurately;
  a hand-written byline stopped being verified the day after it was written.
- **Commented-out code.** It poses a question with no answer: is this coming back, is it the
  fix, was it left by accident? Nobody dares delete it, so it accumulates — version control
  is where old code belongs. (One carrying a `TODO` with the exact restore condition is fine.)
- **Ceremonial docstrings on trivial members.** A mandated `/** Gets the name. */` on
  `getName()` is noise, and worse, it teaches readers that doc comments contain nothing.
  Document what has something to say; leave the rest bare.
- **Mumbling.** Half-thoughts like `// no properties file means defaults` leave the reader
  guessing. If a comment needs its author present to interpret, write the full thought or none.
- **Section banners standing in for a file split.** `// ==== HELPERS ====` labels a symptom
  instead of treating it — so don't add new ones. But don't strip existing ones during
  cleanup either: in a file too long to scan they're the navigation someone relies on.
  Propose the split instead.

## Task tags

Use the standard uppercase tokens. Editors, linters, and code-host UIs already highlight and
index them, so a tag is findable by people and tools that never saw your conventions. A
private sigil as the primary marker (`//&`) is invisible to all of it, and to your teammates.

**Format:** `// TAG(owner): description [TICKET-123]`

| Tag | Use for | Must carry |
|---|---|---|
| `TODO` | Planned work, not blocking | Active verb + owner + ticket reference |
| `FIXME` | Known broken or buggy | Exact failure condition + interim mitigation |
| `HACK` | Deliberate workaround | Rationale + what would allow removing it |
| `XXX` | Dangerous or tricky block | The risk + the precaution required |
| `NOTE` | Non-obvious context worth flagging | — |
| `PERF` | Performance constraint | The measurement or the bound |
| `SAFETY` | Invariant that must hold | The invariant itself |

What separates a useful tag from debt that rots is whether a stranger can act on it. Naming
a verb, an owner, and a ticket makes it a work item; `// TODO: fix this` is a smell that
outlives everyone who knew what it meant.

```js
// ✗ TODO: pagination                    — no verb, no owner, no ticket, no trigger
// ✗ TODO: make this faster              — no target, so it can never be "done"
// ✓ TODO(rlee): paginate list_orders once the API exposes cursors [PLAT-4412]

// ✗ FIXME: broken
// ✓ FIXME(dchen): throws on empty payload when Content-Length is 0; the caller
//   retries so failures are currently absorbed [API-208]

// ✗ HACK: temporary
// ✓ HACK(rlee): retry 3x with fixed backoff — the gateway returns 200 with an empty
//   body during failover. Remove once the vendor ships the 503 fix [OPS-1190]

// ✗ XXX: careful here
// ✓ XXX(bmartin): mutates the shared index without taking the write lock; safe only
//   because every current caller already holds it. Verify before adding a caller.

// ✓ NOTE: response order is significant — the dashboard renders in array order.
// ✓ PERF: O(n²), but n ≤ 32 by schema constraint; measured 0.4 ms at n=32.
// ✓ SAFETY: caller guarantees `buf.len() >= HEADER_LEN`; the unchecked slice below
//   depends on it.
```

Two tag types are worth extra care because they routinely rot into nonsense:

- **Restoring disabled code** — name the exact trigger condition, not the action.
  `TODO(fry): re-enable this check once the default becomes NULL_STATS_COUNTER [X-77]`,
  never `TODO: uncomment`.
- **Cleanup requests** — say whether the code should be deleted or moved, and what confirms
  it: `TODO(sam): appears unused; delete after 2.4 confirms no callers [CLEAN-12]`.

## Cleanup mode: flag and ask, never silently delete

When you meet existing over-commented code — whether you were asked to clean it up or just
happened to be editing the file — do not delete comments as a side effect of other work.

The reason is asymmetric risk. A redundant-looking comment may encode a bug someone hit
once, a reviewer's demand, or a constraint invisible from this file. Delete it and you were
right, the user saves seconds of reading; delete it and you were wrong, they lose something
unrecoverable and won't notice it's gone. Flagging costs one line of output.

1. **List each candidate** with line number, the comment text, and a one-line reason it
   looks removable. Group them by category — transliteration, closing brace, byline,
   commented-out code, mumbling, stale — so the user can accept or reject a whole category
   instead of adjudicating line by line.
2. **Show the proposed result.** The rewritten region, so they see what the code reads like
   without the noise, not just a list of what disappears.
3. **Ask, then wait.** Make no edits until they answer.
4. **Flag contradictions separately.** A comment that disagrees with the code is either
   stale documentation or evidence of a bug, and which one it is matters a great deal. Never
   fold these into the delete pile — surface them and say you can't tell which.
5. **Leave functional comments in place.** Some things that look like comments are code:
   shebangs, `# noqa`, `// eslint-disable-next-line`, `// @ts-expect-error`, `//go:build`,
   `#pragma`, `# frozen_string_literal: true`, `# shellcheck disable=`, license headers.
   Deleting these breaks behavior or the build — full list in `references/languages.md`.
   If one looks obsolete, raise it as a question, not a finding: "this `# noqa: E501` may be
   dead — the line looks under the limit, but check before removing." The config that
   decides is usually not in view, so a confident reason to keep it is as wrong as a
   confident deletion. Report the doubt; don't invent a justification for either answer.

If a comment might be load-bearing and you can't tell, say so rather than putting it in the
delete pile. Uncertainty is a useful thing to report; a confident wrong deletion isn't.

When the user has *already* said to go ahead and strip redundant comments without asking,
do that — the point is to never delete unasked, not to nag someone who has asked.

Read `references/cleanup-workflow.md` for the full report format and worked example.

## Optional: sigil emphasis layer

**Swappable convention, not a core rule** — it follows the Better Comments editor extension,
which colorizes these prefixes. Adopt only if the codebase uses it or the user asks.

```js
// * Important — highlight something a reader must not skim past
// ! Alert — warning about a consequence or a footgun
// ? Open question — unresolved, awaiting a decision
```

Sigils layer on top of tags and never replace them, because tooling greps for `TODO`/`FIXME`:
`// ! FIXME(dchen): silently drops events when the queue is full [EVT-88]`.

## Comment-first as a design check

Writing the doc comment before the body is worth trying for the diagnostic it gives you: if
the contract is hard to state — the summary needs three "except when" clauses, or the
parameter docs keep referring to internals — that is usually the API telling you it's wrong.
Fixing the shape then is far cheaper than after there are callers.

## Keeping comments from rotting

- **Document each thing exactly once.** Duplicated documentation drifts apart and then
  disagrees with itself. Describe an invariant in the module header and reference it.
- **Keep comments adjacent to what they describe.** A comment far from its code doesn't get
  updated when the code changes, because nobody sees it.
- **Prefer high-level commentary.** A comment about behavior and rationale survives
  refactoring; one describing specific mechanics is invalidated by any change to them.
- **Update comments in the same edit as the code.** A stale comment is worse than none — it
  is trusted and wrong. When changing code, fix or delete the comments that no longer hold.

## Examples

### TypeScript — a public API

**Before** (narration; the contract is missing entirely):

```ts
// Rate limiter class
export class RateLimiter {
  // the tokens
  private tokens: number;

  // constructor
  constructor(capacity: number, refillRate: number) {
    this.tokens = capacity; // set tokens to capacity
  }

  // try to consume a token
  tryConsume(cost: number): boolean {
    this.refill();          // refill first
    if (this.tokens < cost) return false; // not enough
    this.tokens -= cost;    // subtract
    return true;            // ok
  }
}
```

**After** (contract on the interface, why-comments inside):

```ts
/**
 * Token bucket rate limiter for a single key, capped at `capacity` and refilled
 * continuously at `refillRate`. Not safe for concurrent use across workers — each
 * process holds its own bucket.
 *
 * @param capacity   Maximum burst size, in tokens. Must be > 0.
 * @param refillRate Tokens added per second. Fractional values are supported.
 */
export class RateLimiter {
  private tokens: number;
  private lastRefill = Date.now();

  constructor(private capacity: number, private refillRate: number) {
    this.tokens = capacity;
  }

  /**
   * Attempts to spend `cost` tokens.
   *
   * @param cost Tokens to spend; values above `capacity` can never succeed.
   * @returns `true` if the tokens were deducted, `false` if the caller should back
   *          off. Rejection consumes nothing, so retrying is safe.
   */
  tryConsume(cost: number): boolean {
    this.refill();
    if (this.tokens < cost) return false;
    this.tokens -= cost;
    return true;
  }

  private refill(): void {
    const now = Date.now();
    // Refill from elapsed wall-clock time rather than on a timer: a timer that misses
    // ticks under load would silently under-refill exactly when traffic is heaviest.
    const elapsedSec = (now - this.lastRefill) / 1000;
    this.tokens = Math.min(this.capacity, this.tokens + elapsedSec * this.refillRate);
    this.lastRefill = now;
  }
}
```

### Python — trimming narration to signal

**Before:**

```python
# function to parse the date
def parse_date(s):
    # strip whitespace
    s = s.strip()
    # split on dash
    parts = s.split("-")
    # return the datetime
    return datetime(int(parts[0]), int(parts[1]), int(parts[2]))
    # end function
```

**After:**

```python
def parse_date(s: str) -> datetime:
    """Parse an ISO-8601 calendar date (``YYYY-MM-DD``) into a naive datetime.

    Args:
        s: Date string. Surrounding whitespace is tolerated; time components and
            timezone offsets are not — pass those to ``parse_timestamp`` instead.

    Returns:
        A ``datetime`` at midnight, with no timezone attached.

    Raises:
        ValueError: If the string is not three dash-separated integers, or if they
            do not form a real calendar date.
    """
    year, month, day = s.strip().split("-")
    return datetime(int(year), int(month), int(day))
```

### Go — doc comments name the identifier

Go's convention is distinctive: a doc comment is a complete sentence starting with the name
of the thing it documents, because `go doc` and pkg.go.dev display it detached from the
declaration.

**Before:**

```go
// this function parses a config
// it takes bytes and returns a Config
func ParseConfig(b []byte) (*Config, error) {
	var c Config
	// unmarshal the yaml
	if err := yaml.Unmarshal(b, &c); err != nil {
		return nil, err // return the error
	}
	return &c, nil
}
```

**After:**

```go
// ParseConfig decodes YAML configuration bytes into a Config, applying defaults for
// any field the document omits. The returned Config is safe for concurrent reads and
// must not be mutated after publication.
//
// It returns a *yaml.TypeError if the document is malformed, and ErrNoRegion if the
// required region field resolves empty after defaults are applied.
func ParseConfig(b []byte) (*Config, error) {
	// Defaults go in before unmarshalling so an explicit empty value in the document
	// wins over the default — the reverse order silently discards `region: ""`.
	c := defaultConfig()
	if err := yaml.Unmarshal(b, &c); err != nil {
		return nil, fmt.Errorf("parse config: %w", err)
	}
	if c.Region == "" {
		return nil, ErrNoRegion
	}
	return &c, nil
}
```

## Language conventions

Delimiters, doc-comment syntax, generators, and line limits vary by ecosystem, and the wrong
form means the doc tooling silently ignores the comment. Read `references/languages.md`
before writing doc comments in **Rust, Java, C#, C/C++, Swift, Ruby, PHP, or shell** — or in
any language with no worked example above. TypeScript, Python, and Go are covered inline;
don't open the reference for those.
