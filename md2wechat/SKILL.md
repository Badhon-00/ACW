---
name: md2wechat
description: Agent-native CLI workflow for formatting Markdown articles, previewing WeChat Official Account HTML, handling article assets, and creating WeChat draft posts.
---

# md2wechat

Use this skill when a user wants an AI agent to turn Markdown into a WeChat Official Account-ready article. The workflow is CLI-first and agent friendly, so Claude Code, Codex, OpenCode, or OpenClaw can inspect an article, preview the output, choose themes and layout modules, upload images, generate covers, and create a WeChat draft when credentials are configured.

## When to Use This Skill

- Format a Markdown article for WeChat Official Account publishing.
- Preview WeChat HTML locally before creating a draft.
- Add professional themes, mobile-friendly layout modules, covers, or generated images to an article workflow.
- Let an agent run the repetitive publishing steps while keeping draft creation explicit and confirm-first.

## What This Skill Does

1. **Inspects article readiness**: Checks article metadata, image requirements, and target readiness before publishing.
2. **Previews locally**: Generates local preview output so the user can review layout before any remote side effects.
3. **Formats for WeChat**: Converts Markdown into WeChat Official Account-compatible HTML with themes and layout modules.
4. **Handles publishing assets**: Supports image upload, cover selection, and draft creation when the user explicitly asks for it.

## How to Use

### Basic Usage

```bash
md2wechat preview article.md
```

### Agent Workflow

```bash
md2wechat inspect article.md --json
md2wechat preview article.md
md2wechat convert article.md --draft --cover cover.jpg
```

### Install As An Agent Skill

```bash
npx skills add https://github.com/geekjourneyx/md2wechat-skill --skill md2wechat
```

## Example

**User**: "Use md2wechat to prepare this Markdown article for WeChat. Preview it first, then only create a draft if the article is ready."

**Output**:

```text
The agent inspects the Markdown, reports readiness blockers, generates a local preview, and waits for confirmation before running draft creation.
```

## Tips

- Run `md2wechat capabilities --json` when the installed CLI version or supported features are uncertain.
- Use `md2wechat themes list --json` and `md2wechat layout list --json` before selecting visual formatting options.
- Treat preview, image upload, and draft creation as separate steps. Draft creation requires configured WeChat credentials.

## Common Use Cases

- Technical writers publishing Markdown posts to WeChat Official Accounts.
- Content teams standardizing WeChat article formatting through Claude Code or Codex.
- Indie developers turning documentation, changelogs, or product essays into WeChat-ready drafts.

**Credit:** Created by [@geekjourneyx](https://github.com/geekjourneyx) and maintained at [geekjourneyx/md2wechat-skill](https://github.com/geekjourneyx/md2wechat-skill).
