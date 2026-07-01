---
name: x-twitter-scraper
description: Use Xquik for X (Twitter) data workflows, REST API setup, MCP setup, monitoring, webhooks, and approval-gated actions.
---

# x-twitter-scraper

Use this skill when working with Xquik's X (Twitter) data and automation workflows through the public REST API, MCP server, and webhooks.

## When to Use This Skill

- Set up Xquik API keys, REST calls, or MCP clients.
- Search, look up, or export X data through Xquik.
- Configure account or keyword monitors and webhook delivery.
- Draft approval-gated X actions with clear user confirmation.

## What This Skill Does

1. Choose the interface: REST API for direct integrations, MCP for AI agents, or webhooks for event delivery.
2. Map the workflow: Identify the Xquik endpoint or MCP task that matches the request.
3. Keep actions explicit: Treat posting, deleting, following, and other account-changing actions as approval-gated.
4. Validate outputs: Check response shapes, pagination, and webhook signatures before using results downstream.

## How to Use

### REST API

Read the API docs before building the request:

```
Open https://docs.xquik.com/api-reference and choose the endpoint that matches the workflow.
```

### MCP

Use the MCP guide when connecting an AI client:

```
Open https://docs.xquik.com/mcp/overview and configure the Xquik MCP server.
```

### Source Skill

Inspect the maintained source skill and repository:

```
Open https://github.com/Xquik-dev/x-twitter-scraper/tree/master/skills/x-twitter-scraper
```

## Example

**User**: "Set up an agent workflow that tracks brand mentions on X and sends webhook events."

**Output**:

```
Use Xquik monitors for the keyword stream, configure a signed webhook endpoint, test delivery, and document the retry and verification flow.
```

## Tips

- Keep API keys in the user's approved secret store.
- Use pagination when collecting large result sets.
- Verify webhook signatures before processing events.
- Confirm user intent before any account-changing action.

## Common Use Cases

- X search and lookup workflows
- Account and keyword monitoring
- Giveaway and draw support workflows
- Webhook-driven event pipelines
- AI agent access through MCP

**Source:** [Xquik x-twitter-scraper](https://github.com/Xquik-dev/x-twitter-scraper)
