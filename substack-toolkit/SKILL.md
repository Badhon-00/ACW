---
name: substack-toolkit
description: Draft and publish rich Substack posts from Markdown or Python, plus read a publication's archive, fetch individual posts, and download subscribers. Works around Substack's three undocumented private-API gotchas (broken rawHtml node, base64-only image upload, null bylines on draft PUT). Triggers on "post to Substack", "draft a Substack article", "publish a Substack newsletter", "create a Substack draft from markdown", "upload an image to Substack", "list my Substack posts", "fetch a Substack post body", "list Substack archive", "get publication metadata", "export Substack subscribers", or any request to programmatically read or write a Substack publication. Notes publishing and restacking are on the roadmap.
---

# Substack Toolkit

Programmatic Substack publishing for Claude. Converts Markdown (with frontmatter and inline images) into clean Substack drafts via the private writing API, using only the editor-validated ProseMirror schema so drafts open cleanly instead of throwing the "Something has gone wrong" modal.

## When to Use This Skill

Trigger this skill when the user wants to **write** Substack content:

- Post or draft content to a Substack publication ("post to Substack", "draft a Substack article", "create a Substack draft")
- Turn a Markdown file into a Substack post
- Upload an image to Substack programmatically
- Automate Substack publishing or work around Substack's editor mangling pasted content from Notion, Obsidian, Google Docs, or anywhere else
- Batch-create or schedule Substack drafts from a folder of `.md` files

Or to **read** Substack content from a publication they own (or any public publication):

- List the published archive of a publication ("list my Substack posts", "fetch the last 50 posts")
- Fetch a single post's full body, audience, cover image, comment count, etc.
- Get publication metadata (name, hero, custom domain, bylines)
- Download the subscriber list as CSV (owner only)

Do **not** trigger this skill when:

- The user wants to send a Substack Note or restack a post (roadmap)
- The user is asking about general newsletter strategy (this is a read/write tool, not a marketing advisor)

## What This Skill Does

### Write

- **Posts native ProseMirror drafts.** Uses only the editor-validated node types (`paragraph`, `heading`, `blockquote`, `bullet_list`, `ordered_list`, `list_item`, `captionedImage`, `image2`, `caption`). Skips the `rawHtml` node entirely — the API accepts it, but the editor crashes opening any draft that contains it.
- **Uploads images correctly.** The `/api/v1/image` endpoint rejects multipart uploads with a generic 400. This skill uses the working JSON `{"image": "data:image/png;base64,..."}` form and returns the resulting S3 URL.
- **Converts Markdown.** Headings, paragraphs, bold, italic, links, bullet and ordered lists, blockquotes (inline marks preserved), and image embeds (local paths auto-upload to Substack S3).
- **Handles draft lifecycle.** Create, update (with the `draft_bylines: null` workaround for unpublished drafts), list, delete.
- **Sets cover images.** The same uploaded URL is used for both inline display and the post's social card / archive thumbnail.

### Read

- **Lists the archive.** `client.archive(sort, limit, offset)` returns published posts with title, subtitle, slug, audience, date, and bylines. `client.iter_archive()` is a generator that walks the whole archive across pages.
- **Fetches a single post.** `client.get_post(id_or_slug)` returns the full post dict including `body_html`, `cover_image`, `description`, `comment_count`, `canonical_url`, and `truncated_body_text`.
- **Gets publication metadata.** `client.publication()` returns the publication name, hero text, custom domain, and byline list.
- **Exports subscribers.** `client.subscribers_csv(out_path)` downloads the subscriber list as CSV (owner role required; some accounts gate the direct endpoint behind dashboard JS — see Tips).
- **Resolves the current user.** `client.user_id` is the reliable path (uses the drafts/archive fallback chain); `client.user_self()` hits the global endpoint and works for some accounts but 403s on others.

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

Write:

```
python scripts/substack_draft.py auth                       # verify cookie
python scripts/substack_draft.py post --body essay.md       # create draft from markdown
python scripts/substack_draft.py post --body essay.md --hero hero.png
python scripts/substack_draft.py list --limit 10            # list draft posts
python scripts/substack_draft.py delete 12345678            # delete a draft
```

Read:

```
python scripts/substack_draft.py publication                # publication metadata
python scripts/substack_draft.py archive --limit 25         # published posts
python scripts/substack_draft.py archive --sort old --offset 50
python scripts/substack_draft.py get 12345678               # one post (summary)
python scripts/substack_draft.py get 12345678 --out body.html
python scripts/substack_draft.py get 12345678 --body | pandoc -f html -o post.md
python scripts/substack_draft.py whoami                     # may 403 (see Tips)
python scripts/substack_draft.py subscribers --out subs.csv # owner only
```

All commands accept `--pub yourname.substack.com` if `SUBSTACK_PUB` isn't set.

### Read API (Python library)

```python
from scripts.substack_draft import Client

client = Client(pub="yourname.substack.com")

# Publication metadata
pub = client.publication()
print(pub["name"], pub.get("custom_domain"))

# Archive listing
for post in client.archive(sort="new", limit=10):
    print(post["id"], post["title"], post["audience"])

# Walk the whole archive
for post in client.iter_archive(page_size=25):
    ...

# Fetch a single post's full body
post = client.get_post(12345678)
html = post["body_html"]

# Download subscribers (requires owner role)
client.subscribers_csv(out_path="subs.csv")
```

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
- **`user_self` 403 is normal.** Some accounts always get 403 from `https://substack.com/api/v1/user/self`. Use `client.user_id` instead — it falls back through `/api/v1/drafts` and `/api/v1/archive` to resolve the byline ID, and works on every account that can write at all.
- **Subscriber export is finicky.** `subscribers_csv()` works for most owner accounts. If you get a non-CSV content-type back, the publication is gated behind dashboard JS — fall back to a short Playwright recipe that injects the cookie into a headless browser and downloads from `/publish/users`. See the standalone repo's README for a working snippet.
- **`get_post` returns the inner post dict.** The raw API wraps it as `{post, publication, publicationSettings, subscription, publicationUser}`; this skill unwraps to the post for you. If you need the surrounding context (subscription state, etc.), use `client.session.get(...)` directly and parse the envelope yourself.

## Common Use Cases

### Write

- **Drafting from a journaling app.** Write in Obsidian, Bear, iA Writer, or any Markdown editor and push to Substack as drafts without losing formatting.
- **Batch-posting a backlog.** Convert a folder of `.md` archive files into drafts in one loop.
- **AI-assisted drafting.** Claude writes the post, this skill ships it cleanly without the user touching the web editor.
- **Anonymized personal essays.** Author privately, generate a programmatic hero image, draft it and review on Substack without ever pasting through the browser.
- **Cross-posting from a static site.** Keep one canonical Markdown source for your blog, publish to Substack with one command.

### Read

- **Mirror an archive locally.** Walk `iter_archive()`, call `get_post(id)` on each, write `body_html` to disk — full publication backup in one script.
- **Convert posts back to Markdown.** `get_post --body | pandoc -f html -o post.md` round-trips a published post into editable Markdown.
- **Newsletter analytics on your own posts.** Pull the archive, group by `audience` (`everyone` vs `only_paid`), count `comment_count`, eyeball cadence by `post_date`.
- **AI-assisted summarization.** Fetch a post's body, pass it to Claude with a "summarize for the daily digest" prompt, save the summary anywhere.
- **Migration off Substack.** Combine `iter_archive()` + `get_post()` + `subscribers_csv()` to produce a clean export folder you can import into Ghost, Beehiiv, or anywhere else.

## Known Gotchas (Hall of Shame)

Documented here so the next person doesn't lose a weekend.

| Trap | Symptom | Fix |
|---|---|---|
| `rawHtml` node | API returns 200, editor shows "Something has gone wrong" opening the draft | Use only validated node types (built into this skill) |
| `body_html` top-level field | Draft is created but body is empty | Send `draft_body` with a ProseMirror JSON doc instead |
| Multipart image upload | 400 with "Invalid value" on `param: image` | Use JSON `{"image": "data:image/png;base64,..."}` (built in) |
| `draft_bylines: null` on PUT | 400 on update of an unpublished draft | Inject `[{"id": user_id, "is_guest": False}]` before PUT (built in) |
| Tables in markdown | Render as collapsed text or nothing | Not in the validated schema — render to image and embed |
| `user/self` returns 403 | Some accounts always 403 on this endpoint | Use `client.user_id` (resolves via drafts/archive bylines) |
| `get_post` returns wrapper | Top-level keys are `post`, `publication`, `subscription`, ... | This skill unwraps to the post dict automatically |
| `subscribers_csv` returns HTML | Account is gated behind dashboard JS | Fall back to Playwright with the SID cookie injected (see standalone repo README) |

## Roadmap

- [x] Read posts and archive from a publication (v0.2)
- [x] Fetch publication metadata (v0.2)
- [x] Export subscribers as CSV (v0.2)
- [ ] Search a publication's archive by title / date / audience
- [ ] Post Substack Notes (with link attachments)
- [ ] Restack a post programmatically
- [ ] Scheduled-publish helper
- [ ] Comments read/write

## Dependencies

- `requests` — required
- `markdown-it-py` — required for the Markdown converter and the `post` CLI subcommand

## License

MIT.

---

**Inspired by:** Michael Hanko ([mphinance.substack.com](https://mphinance.substack.com)) — built because Substack's editor kept mangling pasted Markdown and there was no documented escape hatch.
