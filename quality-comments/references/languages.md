# Language Conventions

Per-ecosystem delimiters, doc tags, generators, and line limits. Using the wrong delimiter
means the doc generator silently ignores the comment, so check the language before writing
doc comments in it.

**Contents:** [Quick table](#quick-reference) · [Python](#python) · [JavaScript /
TypeScript](#javascript--typescript) · [Go](#go) · [Rust](#rust) · [Java](#java) ·
[C#](#c) · [C / C++](#c--c-1) · [Swift](#swift) · [Ruby](#ruby) · [PHP](#php) ·
[Shell](#shell--bash) · [Functional comments](#functional-comments--leave-these-in-place)

## Quick reference

| Language | Doc delimiter | Inline | Doc tool | Line limit convention |
|---|---|---|---|---|
| Python | `"""..."""` | `#` | Sphinx, pdoc, mkdocstrings | 79 code / 72 comments (PEP 8); 88 with Black |
| JS / TS | `/** ... */` | `//` | JSDoc, TypeDoc, TS compiler | Set by ESLint/Prettier; 80–100 typical |
| Go | `// ` above decl | `//` | `go doc`, pkg.go.dev | No limit; gofmt doesn't wrap |
| Rust | `///`, `//!` | `//` | `cargo doc` (rustdoc) | 80 (rustfmt `comment_width`) |
| Java | `/** ... */` | `//` | Javadoc | 100 (Google), 80–120 house style |
| C# | `/// <summary>` | `//` | DocFX, Sandcastle | 65 recommended by MS docs; 120 common in practice |
| C / C++ | `/** */` or `///` | `//` | Doxygen | 80 (LLVM, GNU); 100 (Google) |
| Swift | `///` or `/** */` | `//` | DocC | 80 default; 100 (Google Swift) |
| Ruby | `#` above decl | `#` | RDoc, YARD | 80–120 (RuboCop default 120) |
| PHP | `/** ... */` | `//`, `#` | phpDocumentor | PSR-12: soft 120, no hard limit |
| Shell | `#` | `#` | none standard | 80 (Google Shell Style) |

---

## Python

- **Docstrings** use triple double quotes, placed *inside* the definition on the first line
  — not above it. A `#` comment above a `def` is invisible to `help()` and every doc tool.
- **PEP 257 shape:** one-line imperative summary ending in a period, blank line, then
  detail. Google style is the most common structured form: `Args:`, `Returns:`, `Raises:`,
  `Yields:`, `Attributes:`. NumPy style (underlined sections) is standard in scientific
  code; Sphinx/reST style (`:param x:`) is older but still widespread — match the file.
- **Type hints replace type documentation.** With `def f(n: int) -> str`, writing
  `Args: n (int)` duplicates something the checker already enforces. Document meaning,
  units, and ranges instead.
- **Inline comments** sit at least two spaces after the statement and start with `# `.
  Block comments align with the code they precede.
- **Module docstring** goes first in the file (after the shebang and any `from __future__`
  import), describing what the module is for.
- PEP 8 caps comments and docstrings at 72 characters even where code is allowed 79; the
  narrower measure is for side-by-side diff reading. Projects using Black commonly relax
  code to 88 while leaving prose narrow.

```python
def retry_with_backoff(fn, attempts: int = 3, base_delay: float = 0.5):
    """Call ``fn`` until it succeeds, backing off exponentially between tries.

    Args:
        fn: Zero-argument callable. Must be idempotent — it may run ``attempts``
            times, and a partial side effect from a failed call is not undone.
        attempts: Total tries including the first. Values < 1 raise ValueError.
        base_delay: Seconds before the first retry; each retry doubles it, so the
            worst-case total wait is ``base_delay * (2**attempts - 1)``.

    Returns:
        Whatever ``fn`` returns on its first success.

    Raises:
        Exception: Re-raises the final failure once attempts are exhausted.
    """
```

## JavaScript / TypeScript

- JSDoc blocks must open with `/**` — two asterisks. `/*` is an ordinary comment and no
  tooling reads it.
- **In TypeScript, omit `@param {type}`.** The signature carries the type and duplicating it
  invites drift. Keep the description: `@param cost Tokens to spend; > capacity never
  succeeds.` In plain JS with `// @ts-check`, types in JSDoc *are* the type system — write
  them.
- Useful tags: `@param`, `@returns`, `@throws`, `@example`, `@deprecated` (with the
  replacement named), `@see`, `@typedef` and `@callback` for shared shapes, `@template` for
  generics, `@remarks` (TSDoc, for detail past the summary).
- The first sentence is the tooltip; make it independently readable.
- `@ts-expect-error` and `eslint-disable` are directives, not comments — see the bottom
  section. Any `@ts-expect-error` should carry a plain-language reason next to it.

## Go

- **The doc comment begins with the identifier's name** and is a complete sentence:
  `// ParseConfig decodes YAML configuration bytes into a Config.` `go doc` and pkg.go.dev
  render it detached from the declaration, so a comment starting "This function decodes…"
  reads as orphaned prose.
- Use `//` line comments, not `/* */` — that is what gofmt and the toolchain expect.
- No blank line between the comment and the declaration, or it stops being a doc comment.
- **Package comment:** `// Package foo ...` immediately above `package foo`, in exactly one
  file per package (conventionally `doc.go` when it's long).
- Document exported identifiers; unexported ones only when non-obvious.
- **Deprecation** has a machine-readable form recognized by tooling — a paragraph starting
  `// Deprecated: ` followed by what to use instead.
- Gofmt reflows nothing, so wrap comments yourself at whatever width the file uses.
- Godoc since Go 1.19 renders links (`[Config]`), lists, and headings; indented lines become
  code blocks, so don't indent ordinary prose.

```go
// Deprecated: use ParseConfigContext instead, which honors cancellation.
// This wrapper will be removed in v3.
func ParseConfig(b []byte) (*Config, error)
```

## Rust

- `///` documents the item *below* it; `//!` documents the *enclosing* item — used at the
  top of a file for module docs or in `lib.rs` for crate docs. Mixing them up is the usual
  rustdoc mistake.
- Doc comments are Markdown. Conventional sections, in this order:
  `# Examples`, `# Panics`, `# Errors`, `# Safety`.
- **`# Safety` is mandatory on `unsafe fn`** — state the invariants a caller must uphold.
  The `clippy::missing_safety_doc` lint enforces it. Inside a function, `// SAFETY:` comments
  on each `unsafe` block state why the invariant holds there.
- **Examples in docs are compiled and run by `cargo test`.** They cannot be pseudocode. That
  makes them the one kind of documentation that can't rot, so prefer an example over prose
  where either would do.
- Document `Err` conditions under `# Errors` — a `Result` signature says a call can fail but
  never says when.
- `#[doc(hidden)]` hides public-but-not-really API from the generated docs.

```rust
/// Decodes a frame header from `buf`.
///
/// # Examples
/// ```
/// let hdr = Header::parse(&[0x01, 0x00, 0x20, 0x00])?;
/// assert_eq!(hdr.len, 32);
/// ```
///
/// # Errors
/// Returns [`FrameError::Short`] if `buf` is under `HEADER_LEN` bytes, and
/// [`FrameError::Version`] if the version nibble is not 1.
pub fn parse(buf: &[u8]) -> Result<Header, FrameError> {
```

## Java

- Javadoc is `/** ... */` immediately above the declaration.
- **The first sentence, up to the first period, is the summary** shown in index tables.
  Write it as a fragment describing the result: "Returns the canonical form of…".
- Tags in conventional order: `@param`, `@return`, `@throws`, `@since`, `@see`,
  `@deprecated`. Document *unchecked* exceptions too when they're part of the contract —
  the signature doesn't declare them.
- `{@code x}` for inline literals, `{@link Type#method}` for cross-references. Raw `<` and
  `&` need escaping since Javadoc is HTML.
- Deprecation needs both halves: the `@Deprecated` annotation (compiler warnings) and the
  `@deprecated` Javadoc tag (explains what to use instead).
- Don't Javadoc trivial getters into existence just to satisfy a checkstyle rule — that is
  the mandated-noise anti-pattern. Configure the rule to skip trivial accessors instead.
- `@inheritDoc` or a bare override with no Javadoc inherits the parent's contract; restating
  it creates two copies that drift.

## C#

- `///` per line, containing XML tags. The compiler parses these into an XML doc file and
  **validates them** — mismatched `<param name="...">` and bad `cref` targets produce
  warnings (CS1573, CS1574), and `<GenerateDocumentationFile>` plus CS1591 flags undocumented
  public members.
- Core tags: `<summary>` (IntelliSense tooltip), `<param>`, `<returns>`, `<exception cref="">`,
  `<remarks>` for longer discussion, `<example>` with `<code>`, `<paramref>`/`<typeparamref>`,
  `<see cref=""/>`, and `<inheritdoc/>` to pull documentation from a base or interface.
- `<inheritdoc/>` on interface implementations avoids maintaining two copies of a contract.
- Microsoft's older guidance recommends ~65-character comment lines for readability in
  rendered docs; most modern C# codebases use 120. Follow the repo's `.editorconfig`.

```csharp
/// <summary>Attempts to reserve <paramref name="cost"/> tokens from the bucket.</summary>
/// <param name="cost">Tokens to reserve. Values above capacity can never succeed.</param>
/// <returns><c>true</c> if reserved; otherwise <c>false</c> and nothing is consumed.</returns>
/// <exception cref="ObjectDisposedException">The limiter has been disposed.</exception>
```

## C / C++

- The physical header/implementation split maps exactly onto the interface/implementation
  split: **the contract goes in the `.h`, the rationale goes in the `.c`/`.cpp`.** Callers
  read the header only. Duplicating the contract in both files guarantees they diverge.
- Doxygen accepts `/** ... */`, `///`, or `//!`; pick whichever the project uses and stay
  consistent. Commands take `@` or `\` — again, match the file.
- Common commands: `@brief`, `@param[in]` / `@param[out]` / `@param[in,out]`, `@return`,
  `@retval`, `@throws`, `@warning`, `@note`, `@pre`, `@post`, `@deprecated`, `@file`.
- **Document ownership and lifetime.** Who frees the returned pointer, whether a pointer
  argument is retained past the call, and required alignment or buffer size — these are the
  facts that cause memory bugs, and nothing else records them.
- Note thread-safety and reentrancy explicitly; assumptions here are invisible and costly.
- `#pragma` and preprocessor conditionals are code, not comments.

```c
/**
 * @brief Decodes one frame from @p src into a newly allocated buffer.
 *
 * @param[in]  src  Encoded bytes; must remain valid for the call only.
 * @param[in]  len  Length of @p src in bytes; 0 returns NULL with errno EINVAL.
 * @param[out] out_len  Receives the decoded length. Must not be NULL.
 * @return Heap buffer owned by the caller — free with frame_free(), not free().
 *         NULL on failure with errno set.
 * @warning Not reentrant: uses a shared scratch table guarded by frame_lock().
 */
uint8_t *frame_decode(const uint8_t *src, size_t len, size_t *out_len);
```

## Swift

- `///` for single lines, `/** */` for blocks; content is Swift-flavored Markdown parsed by
  DocC and shown in Xcode's Quick Help.
- **Begin with a single sentence fragment ending in a period**, in the style of the standard
  library: `/// Returns a view of the collection with elements in reverse order.`
- Callouts use a leading dash: `- Parameter name:`, `- Parameters:` (for a list),
  `- Returns:`, `- Throws:`, `- Note:`, `- Warning:`, `- Important:`, `- Complexity:`,
  `- Precondition:`, `- SeeAlso:`.
- **`- Complexity:` is expected on anything non-O(1) in collection-like APIs** — it's a load-
  bearing part of Apple's API contracts, not decoration.
- Apple's guidelines call for documenting every public symbol; the counterweight is that the
  summary fragment for something obvious should be short, not padded.

```swift
/// Returns the elements that satisfy `isIncluded`, preserving order.
///
/// - Parameter isIncluded: Predicate applied to each element; must be pure, as the
///   evaluation order is unspecified.
/// - Returns: A new array; empty if nothing matches.
/// - Complexity: O(*n*), where *n* is the length of the collection.
```

## Ruby

- Comments are `#`; there is no docstring. Documentation is a `#` block directly above the
  definition, read by RDoc (default) or YARD (tag-based, more common in libraries).
- YARD tags: `@param [Type] name`, `@return [Type]`, `@raise [Class]`, `@example`,
  `@yield` / `@yieldparam`, `@deprecated`, `@api private`.
- **Document what a block is yielded** — a `yield` is invisible in the signature, so the
  block's arity and arguments only exist in the documentation.
- Ruby's bang/predicate conventions (`save!`, `valid?`) already convey mutation and
  boolean-ness; don't spend a comment repeating them.
- Magic comments (`# frozen_string_literal: true`, `# encoding:`) must stay at the top of
  the file, before any code. They are directives.

## PHP

- PHPDoc blocks open with `/**`. Order: summary line, blank line, description, blank line,
  tags.
- Tags: `@param type $name Description` (type first, then the variable), `@return`,
  `@throws`, `@var`, `@deprecated`, `@see`, `@template` and `@psalm-*` / `@phpstan-*` for
  generics and refined types that PHP's own type system can't express.
- **Where a native type declaration exists, don't repeat it in PHPDoc** — keep the docblock
  for what the type can't say, such as `@param string $isoDate` meaning "date only, no time"
  or generic element types like `@return list<User>`.
- Static analyzers (PHPStan, Psalm) read these annotations as real types, so an inaccurate
  `@param` produces false analysis results rather than merely stale prose.

## Shell / Bash

- Only `#`. There is no doc generator, so comments are the entire documentation surface —
  which makes them more important here than anywhere else.
- The shebang must be line 1: `#!/usr/bin/env bash`.
- Google's Shell Style Guide gives the conventional shape: a file header stating what the
  script does, and a header on each non-obvious function listing `Globals:`, `Arguments:`,
  `Outputs:`, and `Returns:`.
- **Document what the script mutates and what it assumes** — required environment variables,
  files written, commands that must be on `PATH`, and whether it is safe to re-run. Shell
  scripts are the most common thing to be run half-understood at 3 a.m.
- Explain non-obvious quoting and expansions (`"${arr[@]}"` vs `$arr`, `set -euo pipefail`
  implications) — this is where shell surprises people.
- `# shellcheck disable=SC2086` is a directive; keep it and add a reason.

```bash
#######################################
# Rotates the application log and reopens the file handle.
# Globals:
#   LOG_DIR  - read; must exist and be writable
# Arguments:
#   $1 - retention count; older archives beyond this are deleted
# Outputs:
#   Writes the archive path to stdout
# Returns:
#   0 on success, 1 if LOG_DIR is unset or unwritable
#######################################
rotate_log() {
```

## Functional comments — leave these in place

These are syntactically comments but semantically code. Removing them changes behavior,
breaks builds, or silences a tool that was doing real work. They are exempt from every
cleanup rule in this skill.

| Form | Language |
|---|---|
| `#!/usr/bin/env ...` | any script (must be line 1) |
| `# -*- coding: utf-8 -*-`, `# type: ignore`, `# noqa: E501`, `# pylint: disable=` | Python |
| `// @ts-check`, `// @ts-expect-error`, `// eslint-disable-next-line`, `/* istanbul ignore next */` | JS/TS |
| `//go:build`, `//go:generate`, `//go:embed`, `//nolint:` | Go |
| `# frozen_string_literal: true`, `# rubocop:disable` | Ruby |
| `#pragma once`, `// NOLINT`, `// clang-format off` | C/C++ |
| `// swiftlint:disable` | Swift |
| `# shellcheck disable=SC####` | Shell |
| `<!-- prettier-ignore -->` | Markdown/HTML |
| `// SPDX-License-Identifier: ...` and license headers | any (legal/compliance) |

When cleanup would touch one of these, leave it in place. If it looks obsolete, raise it as a
question rather than a finding — "this `# noqa: E501` may be dead, the line looks under the
limit, but check before removing" — because the config that decides (a `setup.cfg`
`max-line-length`, a CI flag, a formatter that expands the line later) is usually not in
view. A confident reason to keep it is as wrong as a confident deletion; report the doubt
instead of inventing a justification for either answer.

If a suppression directive lacks a reason, the right move is to *add* one, not remove it.
