---
title: Hello from substack-toolkit
subtitle: A demonstration of every feature this library currently supports
---

This post was created end-to-end by running:

`python scripts/substack_draft.py post --body resources/example.md`

If it shows up in your Substack drafts looking like the source Markdown, the library is working.

## Headings render at six levels

### This is an h3

#### This is an h4

(h5 and h6 work the same way.)

## Inline marks

A paragraph with **bold text**, *italic text*, and an inline [link to example.com](https://example.com).

Combinations work too: **bold and *italic*** together, and a [**bold link**](https://example.com).

## Bullet lists

- First item
- Second item with a [link](https://example.com)
- Third item with **bold**

## Ordered lists

1. First step
2. Second step
3. Third step

## Blockquotes

> Blockquotes preserve their inline marks. **Bold**, *italic*, and [links](https://example.com) all survive the round-trip into the editor.

> Multi-paragraph quotes work too.
>
> Second paragraph of the same blockquote.

## Inline images

You can embed a local image with the normal Markdown image syntax, and the library will upload it to Substack's S3 automatically:

`![Caption](./your-diagram.png)`

Remote URLs pass through untouched:

`![Remote image](https://example.com/image.png)`

## What's not supported

Substack's validated ProseMirror schema does not include tables, code blocks, or footnotes. The library skips them rather than producing drafts the editor would reject. If you need any of those, render them to an image and embed.

## Frontmatter reference

| Key | Purpose |
|---|---|
| `title` | Draft title (required) |
| `subtitle` | Draft subtitle |
| `hero` | Path to a hero image — uploaded, prepended to the body, used as the social card |
| `hero_caption` | Caption rendered under the hero |

(That table is itself unsupported; it renders as plain text in the actual Substack draft. Embedded here so you can see what happens.)

## Closing note

This file is intentionally generic and reproducible. Run the command above, open the draft, and you will see exactly what every feature renders as in the live editor. From there you know what's safe to depend on.
