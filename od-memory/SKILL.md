---
name: od-memory
description: >-
  Operate Open Design daemon memory — the durable markdown fact store
  under the daemon data root that is injected into future agent prompts.
  Use when the user mentions od memory, daemon memory, memory tree,
  MEMORY.md, user profile, memory rules, memory extraction, or wants to
  list/edit/move memory entries, set profile, add rules, or toggle memory
  config via CLI or /api/memory.
---

# Open Design daemon memory

Durable product memory owned by the OD daemon — **not** Cursor chat context.

## What it is

- Filesystem store under `<OD_DATA_DIR>/memory/`:
  - `MEMORY.md` — index (one bullet per fact)
  - `<type>_<slug>.md` — entry body + frontmatter
  - `.config.json` — feature switches
- Accepted entries are injected into **future** daemon / BYOK agent prompts.
- Surfaces: Settings UI, `/api/memory/*`, `od memory …`

## Types (buckets)

| Type | Role |
|------|------|
| `profile` | Singleton `user_profile` — who / how; PRE-loop brief expansion |
| `user` | Stable user prefs / identity facts |
| `feedback` | Corrections and taste notes |
| `project` | Project-specific facts |
| `reference` | External refs / docs pointers |
| `rule` | Assertion + check — POST-loop self-verify rubric |

Sources (frontmatter `source:`): `manual` · `heuristic` · `llm` · `connector` · `brand` · `annotation`

## Prefer CLI over scraping UI

Daemon must be running. Use `--json` when scripting. Optional `--daemon-url <url>`.

```bash
od memory tree list --json
od memory tree view <id> --json
od memory tree edit <id> --name "…" --description "…" --type user|feedback|project|reference --body "…"
od memory tree move <id> --type user|feedback|project|reference

od memory profile show --json
od memory profile set --field "Label=Value" [--prompt-file path|-]

od memory rule list --json
od memory rule add --name "…" --assertion "…" --check "…"
od memory rule suggest --note "…"   # proposals only; keep with rule add

od memory verify list --json
od memory verify clear --json

od memory config --json
od memory config --enabled true|false --extraction true|false --profile true|false --rewrite true|false --verify true|false
```

`--extraction` maps to chat auto-extraction. Master `--enabled false` turns the whole feature off.

## HTTP (same contract)

- `GET/PATCH /api/memory/tree` (+ `…/tree/:id`)
- Entry CRUD under `/api/memory/…`
- Config under `/api/memory/config`
- SSE: `/api/memory/events`

Do not invent a second store. Do not write under cwd-relative legacy paths — memory lives under the resolved daemon data root (`OD_DATA_DIR` → `RUNTIME_DATA_DIR`).

## Agent behavior

1. **Inspect before edit** — `tree list` / `view` so you don't duplicate facts.
2. **Prefer one clear entry** over many overlapping bullets.
3. **Profile** for stable identity/workflow; **feedback** for corrections; **rule** only when there is a checkable assertion.
4. **Confirm** before destructive config toggles or `verify clear`.
5. Do not confuse this with Cursor Memories / chat history — those are IDE-side and do not feed OD prompts.

## When coding memory itself

Source of truth: `apps/daemon/src/memory.ts`, routes in `apps/daemon/src/routes/memory.ts`, contracts in `packages/contracts/src/api/memory.ts`. CLI help in `apps/daemon/src/cli.ts` (`od memory`). Keep UI + CLI + HTTP parity.
