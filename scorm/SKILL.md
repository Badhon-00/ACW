---
name: scorm
description: Use when integrating SCORM 1.2/2004 in a web app with @studiolxd/scorm — initializing a session, reading/writing CMI data (score, completion, suspend data, interactions, objectives), handling Result errors, or wiring lifecycle/auto-commit across React, Vue, Angular, Svelte, Web Components, or vanilla JS.
---

# Using @studiolxd/scorm

`@studiolxd/scorm` is a headless SCORM 1.2/2004 runtime. A framework-agnostic core
(`createScormSession`) plus thin adapters. Built-in **mock mode** runs without an LMS.

## Pick the entry point

- Vanilla / any framework: `import { createScormSession } from '@studiolxd/scorm'`
- React: `import { ScormProvider, useScorm, useScormSession } from '@studiolxd/scorm/react'`
- Vue: `import { useScorm } from '@studiolxd/scorm/vue'`
- Angular (>=17): `import { provideScorm, SCORM } from '@studiolxd/scorm/angular'`
- Svelte: `import { createScormStore } from '@studiolxd/scorm/svelte'`
- Web Component: `import '@studiolxd/scorm/wc'` then `<scorm-session>`
- CDN `<script>`: global `window.Scorm`

## The golden rules

1. **Always check `.ok` before `.value`.** Every API method returns
   `Result<T, ScormError>`. Session lifecycle methods return `undefined` when no SCORM
   API was found (`noLmsBehavior: 'error'`).
2. **Lifecycle order:** `initialize()` → interact → `commit()` → `terminate()`. Never
   call data methods before `initialize()`.
3. **Use mock mode for dev/tests:** `createScormSession('2004', { noLmsBehavior: 'mock' })`.
4. **A terminated session cannot be re-initialized** (SCORM rule). Create a new session
   (or remount the React provider with a changed `key`) to start over.
5. **`version: 'auto'`** detects the host LMS (SCORM 2004 first, then 1.2).

## Canonical vanilla example

```ts
import { createScormSession } from '@studiolxd/scorm';

const session = createScormSession('auto', { noLmsBehavior: 'mock' });
session.initialize();

const name = session.api?.getLearnerName();
if (name?.ok) console.log(name.value);

session.api?.setScore({ raw: 80, min: 0, max: 100 }); // 1.2: raw/min/max must be 0–100
session.api?.setComplete();
session.commit();
session.terminate();
```

## Lifecycle helpers (don't hand-roll unload handling)

```ts
import { autoTerminate, autoCommit } from '@studiolxd/scorm';
const stopTerm = autoTerminate(session);   // init now; commit+terminate on unload/dispose
const stopCommit = autoCommit(session, 30_000); // flush every 30s
// later: stopTerm(); stopCommit();
```

React: `useScormAutoTerminate()` and `useScormAutoCommit(ms)` do this for you.

## Common gotchas (these cause real bugs)

- SCORM 1.2 interactions are **write-only**: `getInteraction()` errors (code 404) in 1.2;
  only SCORM 2004 can read them back.
- SCORM 1.2 score `raw/min/max` must be **0–100** (error 405 otherwise). 2004 `scaled`
  must be **-1..1** (error 407).
- `setProgressMeasure` is a no-op in SCORM 1.2.
- `setSessionTime(ms)` takes **milliseconds**; it formats per version internally.
- `recordInteraction(index, record)` — index is the FIRST argument.
- `addLearnerComment(comment, location?, timestamp?)` — location before timestamp.
- SSR (Next.js/Remix): the core is SSR-safe; import `/wc` on the client only.

## ScormError fields

`code`, `errorString`, `operation`, `path`, `diagnostic`, `version`, `apiFound`, `initialized`.
