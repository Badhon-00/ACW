---
name: qa-agent-skill
description: Turns Claude into an autonomous QA tester for a running web app. Use whenever someone says "test my app", "find bugs", "QA this", or "break this app" against a live URL or dev server.
---

# QA Agent Skill

Turn Claude into an autonomous QA tester for your web app. Say "test my app" and Claude opens it in a browser, explores it like a confused/adversarial user (clicks everything, submits garbage into forms, resizes the viewport, mashes back/forward, tries invalid routes) and files real bugs it finds as GitHub issues or Jira tickets, each with a repro (numbered screenshots, assembled into a GIF) and a clear write-up.

## When to Use This Skill

- You want a live web app (local dev server or deployed staging/production URL) explored and stress-tested without writing test scripts by hand.
- You want bugs deduplicated against previously found issues instead of re-filed every run.
- You want evidence (screenshots/GIFs) attached automatically to every bug report.
- You want an agent that asks before filing anything publicly visible (a ticket, an issue, a comment).

## What This Skill Does

**Setup interview** — asks for the target URL, the environment (staging/test vs. production, production is read-only), and which tracker to use (Jira and/or GitHub).

**Reads the QA wiki, then Jira** — checks a persistent `.qa-wiki/` knowledge base committed in the target repo for what's already known (open bugs, tested flows, last-seen dates) before doing anything else. If a Jira MCP is connected, fetches open QA tickets and asks which one to start with.

**Exploration** — a subagent drives the app with Claude's browser tools, clicking every interactive element, submitting edge-case input (empty, oversized, wrong type, special characters, unicode), resizing across breakpoints, and mashing browser history, while watching the console and network tab for real failures. Anything that looks broken is a candidate, not a confirmed bug yet.

**Independent verification** — a maker/checker split. The exploring subagent is mid-exploration and prone to false positives, so the main conversation re-attempts each candidate's minimal repro from a fresh page load before it counts as real.

**Evidence** — for each confirmed bug, captures a numbered screenshot at each repro step and assembles them into a GIF (via ffmpeg) so every bug report comes with a visual repro, not just prose.

**Reports** — every filed bug follows a fixed standard: specific title, minimal numbered repro, expected vs. actual, environment, justified severity, and evidence. Deduped against the wiki and existing tickets first.

**Confirms before filing** — shows the draft (destination, title, body) and waits for a yes before creating anything.

## How to Use

### Basic Usage

test my app at https://staging.example.com

### Advanced Usage

test my app at http://localhost:3000, use the Jira MCP for tracking, and only explore the checkout flow

## Example

**User**: "test my app at https://staging.example.com"

**Output**: Claude asks for environment type and tracker, reads `.qa-wiki/index.md` for prior findings, explores the app via browser tools, verifies each candidate bug from a fresh page load, then shows a draft GitHub issue with a repro GIF and waits for confirmation before filing.

## Tips

- Point it at staging or a local dev server first. Production runs are read-only by design (no destructive actions, no persisted form submissions).
- Install ffmpeg if you want repro GIFs instead of individual screenshots.
- Connect a Jira MCP if you want it to check existing tickets before filing new ones.

## Common Use Cases

- Regression-testing a staging deploy before a release.
- Exploratory testing of a new feature branch's preview deployment.
- Building up a persistent, git-committed record (`.qa-wiki/`) of what's been tested and what's broken, so repeat runs don't rediscover or re-file the same bugs.

**Repository:** [amalshehu/qa-agent-skill](https://github.com/amalshehu/qa-agent-skill)
