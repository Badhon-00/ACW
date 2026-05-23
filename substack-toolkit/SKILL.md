---
name: substack-toolkit
description: Draft and publish rich Substack posts from Markdown or Python, with image upload that works around Substack's private-API gotchas (broken rawHtml node, base64-only image upload, null bylines on draft PUT). Triggers on "post to Substack", "draft a Substack article", "publish a Substack newsletter", "create a Substack draft from markdown", "upload an image to Substack", or any request to programmatically push content to a Substack publication. Reading, search, summarization, and Notes publishing are on the roadmap.
---

# Substack Toolkit

Programmatic Substack publishing for Claude. Converts Markdown (with frontmatter and inline images) into clean Substack drafts via the private writing API, using only the editor-validated ProseMirror schema so drafts open cleanly instead of throwing the "Something has gone wrong" modal.

## When to Use This Skill

Trigger this skill when the user:

- Wants to post or draft content to a Substack publication ("post to Substack", "draft a Substack article", "create a Substack draft")
- Has a Markdown file they want turned into a Substack post
- Needs to upload an image to Substack programmatically
- Asks about the Substack writing API or how to automate Substack publishing
- Is hitting issues with Substack's editor mangling pasted content from Notion, Obsidian, Google Docs, or anywhere else
- Wants to batch-create or schedule Substack drafts from a folder of `.md` files

Do **not** trigger this skill when:

- The user wants to read posts from a Substack publication (roadmap)
- The user wants to send a Substack Note or restack a post (roadmap)
- The user is asking about general newsletter strategy (this is a publishing tool, not a marketing advisor)

## What This Skill Does

- **Posts native ProseMirror drafts.** Uses only the editor-validated node types (`paragraph`, `heading`, `blockquote`, `bullet_list`, `ordered_list`, `list_item`, `captionedImage`, `image2`, `caption`). Skips the `rawHtml` node entirely — the API accepts it, but the editor crashes opening any draft that contains it.
- **Uploads images correctly.** The `/api/v1/image` endpoint rejects multipart uploads with a generic 400. This skill uses the working JSON `{"image": "data:image/png;base64,..."}` form and returns the resulting S3 URL.
- **Converts Markdown.** Headings, paragraphs, bold, italic, links, bullet and ordered lists, blockquotes (inline marks preserved), and image embeds (local paths auto-upload to Substack S3).
- **Handles draft lifecycle.** Create, update (with the `draft_bylines: null` workaround for unpublished drafts), list, delete.
- **Sets cover images.** The same uploaded URL is used for both inline display and the post's social card / archive thumbnail.

## How to Use

### Prerequisites

Grab your Substack session cookie:

1. Log in at your publication on `substack.com`.
2. Open DevTools → Application → Cookies → `substack.com`.
3. Copy the value of `substack.sid`.

Export it as an environment variable:

```bash
export SUBSTACK_SID="s%3A..."
export SUBSTACK_PUB="yourname.substack.com"
```

Install dependencies:

```bash
pip install requests markdown-it-py
```

Verify the cookie works:

```bash
python scripts/substack_draft.py auth
```

### Basic Usage (CLI from Markdown)

Write your post as a Markdown file with YAML-style frontmatter:

```markdown
---
title: Your Post Title
subtitle: Your subtitle
hero: ./hero.png
hero_caption: Optional caption under the hero
---

Body content in normal **Markdown**.

- Lists work
- Links work
- Inline ![images](./diagram.png) get auto-uploaded
```

Then post it:

```bash
python scripts/substack_draft.py post --body your-post.md
```

You get back a draft URL. Open it, review, hit Publish in the Substack dashboard.

### Advanced Usage (Python library)

```python
from scripts.substack_draft import Client, Doc

client = Client(pub="yourname.substack.com")
hero_url = client.upload_image("hero.png")

doc = Doc()
doc.h(1, "My Essay")
doc.p("Paragraph with ", Doc.strong("bold"), " and ", Doc.em("italic"), ".")
doc.bullet_list(["First", "Second", "Third"])
doc.blockquote("A quote.")
doc.image(hero_url, caption="Inline hero")

draft_id = client.create_draft(
    title="My Essay", subtitle="A subtitle",
    doc=doc, cover_image=hero_url,
)
print(client.edit_url(draft_id))
```

### CLI Reference

```
python scripts/substack_draft.py auth                       # verify cookie
python scripts/substack_draft.py post --body essay.md       # create draft from markdown
python scripts/substack_draft.py post --body essay.md --hero hero.png
python scripts/substack_draft.py list --limit 10            # list recent drafts
python scripts/substack_draft.py delete 12345678            # delete a draft
```

All commands accept `--pub yourname.substack.com` if `SUBSTACK_PUB` isn't set.

## Example

**User prompt:**

> Take the markdown file at `~/Documents/launch-post.md` and create a Substack draft. The hero image is alongside it at `~/Documents/launch-hero.png`.

**What Claude does:**

1. Reads the markdown briefly to confirm structure and the frontmatter.
2. Confirms `SUBSTACK_SID` is exported (or asks the user to set it).
3. Runs:
   ```bash
   python scripts/substack_draft.py post \
     --body ~/Documents/launch-post.md \
     --hero ~/Documents/launch-hero.png
   ```
4. Returns the draft edit URL to the user:
   ```
   Uploading hero ~/Documents/launch-hero.png...
     https://substack-post-media.s3.amazonaws.com/public/images/<uuid>_1200x630.png
   Converting markdown...
   Creating draft on yourname.substack.com...
   Draft created: https://yourname.substack.com/publish/post/12345678
   ```

## Tips

- **Frontmatter beats CLI flags.** Put `title`, `subtitle`, `hero`, and `hero_caption` in the markdown frontmatter so the same file is replayable without juggling args.
- **Inline images in Markdown auto-upload.** `![alt](./diagram.png)` paths relative to the markdown file are uploaded to Substack's S3 and inlined. Remote `https://` URLs pass through untouched.
- **Tables and code blocks don't render.** Substack's validated schema doesn't include them. Render them to an image and embed, or accept that inline code becomes plain text.
- **The "Something has gone wrong" trap.** If the editor shows that modal opening your draft, you've sent an unsupported node type. Compare your `draft_body` against `GET /api/v1/drafts/<known-good-id>` to find which.
- **The SID expires.** Logging out of `substack.com` in your browser invalidates the cookie. Refresh from DevTools when auth starts failing.
- **Update, don't recreate.** For iterating on a draft, use `Client.update_draft(draft_id, ...)` — the Substack API treats every `POST /drafts` as a brand-new draft, so re-pushing fills the dashboard with duplicates.

## Common Use Cases

- **Drafting from a journaling app.** Write in Obsidian, Bear, iA Writer, or any Markdown editor and push to Substack as drafts without losing formatting.
- **Batch-posting a backlog.** Convert a folder of `.md` archive files into drafts in one loop.
- **AI-assisted drafting.** Claude writes the post, this skill ships it cleanly without the user touching the web editor.
- **Anonymized personal essays.** Author privately, generate a programmatic hero image, draft it and review on Substack without ever pasting through the browser.
- **Cross-posting from a static site.** Keep one canonical Markdown source for your blog, publish to Substack with one command.

## Known Gotchas (Hall of Shame)

Documented here so the next person doesn't lose a weekend.

| Trap | Symptom | Fix |
|---|---|---|
| `rawHtml` node | API returns 200, editor shows "Something has gone wrong" opening the draft | Use only validated node types (built into this skill) |
| `body_html` top-level field | Draft is created but body is empty | Send `draft_body` with a ProseMirror JSON doc instead |
| Multipart image upload | 400 with "Invalid value" on `param: image` | Use JSON `{"image": "data:image/png;base64,..."}` (built in) |
| `draft_bylines: null` on PUT | 400 on update of an unpublished draft | Inject `[{"id": user_id, "is_guest": False}]` before PUT (built in) |
| Tables in markdown | Render as collapsed text or nothing | Not in the validated schema — render to image and embed |

## Roadmap

- [ ] Read posts and archive from a publication
- [ ] Search a publication's archive
- [ ] Summarize an existing post
- [ ] Post Substack Notes (with link attachments)
- [ ] Restack a post programmatically
- [ ] Scheduled-publish helper

## Dependencies

- `requests` — required
- `markdown-it-py` — required for the Markdown converter and the `post` CLI subcommand

## License

MIT.

---

**Inspired by:** Michael Hanko ([mphinance.substack.com](https://mphinance.substack.com)) — built because Substack's editor kept mangling pasted Markdown and there was no documented escape hatch.
