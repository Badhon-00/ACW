---
name: unbrowser
description: Use unbrowser as a lightweight MCP browser for LLM agents when WebFetch is insufficient but full Chrome or Playwright would be overkill. Supports JavaScript execution, DOM queries, links, forms, cookies, and low-token page maps through a local native binary.
---

# unbrowser MCP Browser

unbrowser is a local MCP browser server for agentic web access. It runs as one native binary, executes bounded JavaScript, keeps session state, and returns compact BlockMaps instead of raw HTML or screenshots.

Use it as the first browser tier between static fetch tools and full Chrome automation.

## When to Use This Skill

- The user needs current web content and static fetch/markdown extraction is incomplete.
- A page requires JavaScript execution, link following, forms, or cookies.
- The task needs structured web extraction without screenshots or visual reasoning.
- You need a cheap reconnaissance pass before deciding whether to escalate to Playwright, Browserbase, or real Chrome.
- You are working in CI, a local terminal, or another environment where launching Chrome is expensive or unavailable.

## When Not to Use This Skill

- The task depends on screenshots, layout pixels, canvas output, video, or visual QA.
- The page requires CAPTCHA solving, Turnstile interaction, browser extensions, SSO, or human takeover.
- The target is a heavy SPA whose content only appears after complex browser APIs or viewport-driven rendering.
- The user explicitly asks for Playwright, Selenium, Chrome DevTools, or a real browser session.

## Setup

Install unbrowser:

```bash
pipx install pyunbrowser
# or
cargo install unbrowser
```

Add it to the MCP client config. The server can be named `unbrowser`; `unchained` is also a useful alias when using it as part of the Unchained browser-agent stack.

```json
{
  "mcpServers": {
    "unchained": {
      "command": "unbrowser",
      "args": ["--mcp"]
    }
  }
}
```

Restart the MCP client after changing the config.

## Core Workflow

1. Start with `navigate` for the target URL.
2. Read the returned BlockMap before querying or clicking.
3. Use `query` for selectors when the BlockMap shows useful structure.
4. Use `text` for simple extraction from `body` or a specific selector.
5. Use `click`, `type`, and `submit` for forms and simple multi-step flows.
6. Use `cookies_set` when the user provides clearance or auth cookies from a real browser.
7. If `challenge` reports a bot wall, CAPTCHA, or high-confidence block, stop and explain that real Chrome or Unchained escalation is needed.

## Practical Prompts

```text
Use unbrowser to open this docs page, find the install command, and summarize the setup steps.
```

```text
Use unbrowser first. If the page looks like a JavaScript shell or bot challenge, tell me what escalation is needed instead of scraping blindly.
```

```text
Navigate to this search page, enter "wreq", submit the form, and extract the first five result titles and URLs.
```

## Best Practices

- Prefer BlockMap, headings, links, and selectors over raw HTML dumps.
- Keep extraction narrow: query the smallest selector that contains the desired data.
- Treat empty tables, empty lists, and sparse server-rendered shells as signs that the page may need stronger browser execution.
- Do not retry bot challenges repeatedly; surface the provider and recommended escalation path.
- Do not ask the user for passwords. If authentication is needed, ask for already-exported cookies or use a real browser workflow outside unbrowser.

## Common Escalations

- Use Playwright when visual state, screenshots, browser APIs, or test assertions matter.
- Use real Chrome when the task requires SSO, extensions, existing browser cookies, CAPTCHA handling, or human takeover.
- Use Unchained when the workflow needs managed Chrome escalation after unbrowser detects that the lightweight tier is insufficient.

## Resources

- Repository: https://github.com/protostatis/unbrowser
- Website: https://unchainedsky.com

**Credit:** Based on the unbrowser project by Unchained.
