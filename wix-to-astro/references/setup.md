# Setup — tools this skill assumes, with install + verify commands

The skill presumes two accounts: **Cloudflare** (Workers, free tier is enough for staging) and
nothing else. No Wix account or API access is needed — everything is extracted from the public
live site.

Run the verify column before starting a migration. A missing tool discovered mid-migration costs
a context switch at the worst time; a missing tool discovered here costs one install command.

| Tool | Why the migration needs it | Install (macOS / general) | Verify |
|---|---|---|---|
| Node.js ≥ 20 | Astro 5+ requires it | `brew install node` or nvm | `node -v` |
| A package manager | Project deps (examples below use pnpm; npm works) | `corepack enable` | `pnpm -v` |
| Astro 5+ | The target framework | created per-project: `pnpm create astro@latest` | `pnpm astro --version` (in project) |
| Wrangler 4+ | Build + deploy to Cloudflare Workers | comes as a project dev-dep; login once | `npx wrangler whoami` |
| ffmpeg | Re-encode builder videos under the 25 MiB Workers asset limit; extract poster frames | `brew install ffmpeg` | `ffmpeg -version` |
| Python 3 + `fonttools`, `brotli`, `Pillow` | Identify obfuscated font files by their name table (the ONLY reliable way — see playbook Step 2); resize/flatten images | `pip3 install fonttools brotli Pillow` | `python3 -c "import fontTools, PIL; print('ok')"` |
| Real-browser automation | Extract computed CSS, run `document.getAnimations()`, measure rendered boxes. Any tool that executes JS in a live page works: Claude in Chrome MCP, Playwright MCP, or a Playwright script | e.g. `npm i -g playwright && playwright install chromium` | open any page, run `1+1` in its context |
| curl | URL matrices, crawler-delivery checks, media downloads | preinstalled on macOS/Linux | `curl --version` |
| Headless screenshot capability *(optional but recommended)* | Full-page side-by-side comparisons at exact viewport widths | a screenshot API (e.g. Firecrawl) or Playwright's `page.screenshot` | one full-page capture at width 402 |
| Headless Chrome *(optional)* | Rendering OG cards from real brand fonts (better than drawing them) | ships with Chrome/Chromium | `chrome --headless --screenshot=... <file://…>` |

## Notes that save real time

- **Browser automation is the load-bearing tool.** Screenshots alone cannot run this skill —
  the method is computed-style extraction, and that requires executing JS in a real rendered
  page. If you have to choose one optional install, choose Playwright.
- **DOM reads survive an occluded window; paints don't.** If using an extension that drives the
  user's own browser (e.g. Claude in Chrome): `getComputedStyle` and `getBoundingClientRect`
  keep working when the window is covered or the display sleeps, but screenshots come back blank
  and CSS transitions freeze at t=0. Use the user's browser for measurement, a headless tool for
  screenshots.
- **JS-bridge output limits.** Browser-automation bridges truncate long results (~1.5 KB is
  common) and may block strings containing URL query params. Strip query strings
  (`new URL(u).origin + new URL(u).pathname`) and page through large results via a `window.__X`
  variable rather than returning everything at once.
- **Secrets.** The only secrets a plain migration needs are Cloudflare credentials (via
  `wrangler login` or an API token in the environment). Forms/integrations (Turnstile, a CRM,
  transactional email) each bring their own keys — set them with `npx wrangler secret put`, never
  commit them, and keep local ones in a gitignored `.dev.vars`.
