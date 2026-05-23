---
name: substack-toolkit
description: Full read-and-write toolkit for Substack from Markdown or Python. Drafts posts (with image upload, native ProseMirror schema). Reads the reader feed, publication archive, individual posts, user profiles, and other users' Notes. Publishes Substack Notes (plain or with link attachments). Engages (like posts, like notes, comment on posts). Exports subscribers. Works around Substack's undocumented private-API gotchas (broken rawHtml node, base64-only image upload, null bylines on draft PUT, user/self 403, get_post wrapper, notes-for-user empty-on-filter). Triggers on any request involving "post to Substack", "draft a Substack article", "create a Substack draft", "upload an image to Substack", "publish a Substack note", "post to Notes", "list my Substack posts", "fetch a Substack post body", "read my Substack feed", "what are my favorite Substack writers saying", "list someone's Substack notes", "like a Substack post", "comment on a Substack post", "look up a Substack profile", "export Substack subscribers", or programmatic Substack publication access generally.
---

# Substack Toolkit

Programmatic Substack publishing for Claude. Converts Markdown (with frontmatter and inline images) into clean Substack drafts via the private writing API, using only the editor-validated ProseMirror schema so drafts open cleanly instead of throwing the "Something has gone wrong" modal.

## When to Use This Skill

Trigger this skill when the user wants to **write** posts:

- Post or draft content to a Substack publication ("post to Substack", "draft a Substack article", "create a Substack draft")
- Turn a Markdown file into a Substack post
- Upload an image to Substack programmatically
- Automate Substack publishing or work around Substack's editor mangling pasted content from Notion, Obsidian, Google Docs, or anywhere else
- Batch-create or schedule Substack drafts from a folder of `.md` files

Or **read** content (own publication, any public publication, or the authenticated user's feed):

- List the published archive of a publication ("list my Substack posts", "fetch the last 50 posts")
- Fetch a single post's full body, audience, cover image, comment count, etc.
- Get publication metadata (name, hero, custom domain, bylines)
- Read the authenticated user's reader feed ("what's new in my Substack feed", "summarize my reads")
- Look up a Substack profile by handle ("who is @someuser on Substack")
- List Notes posted by a specific user ("show me dickcapital's recent notes")
- Download the subscriber list as CSV (owner only)

Or **publish Notes**:

- Post a Substack Note from text or a Doc ("post a note saying X", "publish a note about Y")
- Post a Note with a link attachment ("share this URL as a note")

Or **engage** with content (use sparingly; Substack rate-limits aggressively):

- Like a post ("like that post", "react to post 12345")
- Like a Note ("like that note")
- Comment on a post ("leave a comment on this post saying X")

Do **not** trigger this skill for:

- General newsletter strategy advice (this is a read/write API tool, not a marketing advisor)
- Bulk auto-engagement or follower-farming loops (the methods are explicit-call only on purpose; do not wrap them in a "like everything" loop)

## What This Skill Does

### Write

- **Posts native ProseMirror drafts.** Uses only the editor-validated node types (`paragraph`, `heading`, `blockquote`, `bullet_list`, `ordered_list`, `list_item`, `captionedImage`, `image2`, `caption`). Skips the `rawHtml` node entirely — the API accepts it, but the editor crashes opening any draft that contains it.
- **Uploads images correctly.** The `/api/v1/image` endpoint rejects multipart uploads with a generic 400. This skill uses the working JSON `{"image": "data:image/png;base64,..."}` form and returns the resulting S3 URL.
- **Converts Markdown.** Headings, paragraphs, bold, italic, links, bullet and ordered lists, blockquotes (inline marks preserved), and image embeds (local paths auto-upload to Substack S3).
- **Handles draft lifecycle.** Create, update (with the `draft_bylines: null` workaround for unpublished drafts), list, delete.
- **Sets cover images.** The same uploaded URL is used for both inline display and the post's social card / archive thumbnail.

### Read

- **Reader feed.** `client.feed(cursor)` and `client.iter_feed(max_items, max_pages)` walk the authenticated user's mixed feed (posts + notes from followed publications). Built-in 429 retry and inter-page sleep.
- **Lists the archive.** `client.archive(sort, limit, offset)` returns published posts with title, subtitle, slug, audience, date, and bylines. `client.iter_archive()` is a generator that walks the whole archive across pages.
- **Fetches a single post.** `client.get_post(id_or_slug)` returns the full post dict including `body_html`, `cover_image`, `description`, `comment_count`, `canonical_url`, and `truncated_body_text`.
- **Profile lookup.** `client.user_public_profile(handle)` returns id, name, handle, bio, subscriberCount, primaryPublication for any user.
- **Notes for a user.** `client.notes_for_user(user_id, cursor)` and `client.iter_notes_for_user(user_id, max_items)` paginate any user's published Notes with `reaction_count`, `children_count`, `restacks`.
- **Publication metadata.** `client.publication()` returns the publication name, hero text, custom domain, and byline list.
- **Exports subscribers.** `client.subscribers_csv(out_path)` downloads the subscriber list as CSV (owner role required; some accounts gate the direct endpoint behind dashboard JS — see Tips).
- **Resolves the current user.** `client.user_id` is the reliable path (uses the drafts/archive fallback chain); `client.user_self()` hits the global endpoint and works for some accounts but 403s on others.

### Publish Notes

- **Plain Note.** `client.publish_note("Just bought NVDA dip.")` publishes a one-paragraph Note.
- **Rich Note.** `client.publish_note(doc)` where `doc` is a `Doc` instance with paragraphs, marks, etc.
- **Note with link.** `client.publish_note("Read this:", attachment_url="https://...")` runs the two-step attachment-then-publish flow that produces a Note with a rich link card.

### Engage

These methods write to your account; there are no CLI wrappers for them on purpose. Call explicitly from your own code.

- **Like a post.** `client.like_post(post_id)` (`POST /post/{id}/reaction` with `{"reaction": "❤"}`)
- **Like a Note.** `client.like_note(note_id)` (`POST /comment/{id}/reaction`)
- **Comment on a post.** `client.comment_on_post(post_id, "Great take.")` (`POST /posts/{id}/comments`)

### Helpers

- **`safe_text(s)`** — defensive ASCII transliteration for accounts that still see the editor break on em-dashes, smart quotes, or emoji. Most modern publications render Unicode fine; reach for this only if you see "Something has gone wrong" opening a draft.

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
python scripts/substack_draft.py feed --limit 20            # reader feed
python scripts/substack_draft.py whois @someone             # profile lookup
python scripts/substack_draft.py notes --user @someone --limit 10
python scripts/substack_draft.py notes --user 98404674 --limit 10
```

No CLI for `publish_note`, `like_post`, `like_note`, or `comment_on_post` — those have side effects on your account, so they're library-only. Use Python.

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

# Reader feed (your own followed publications)
for item in client.iter_feed(max_items=50):
    if item["type"] == "post":
        print(item["post"]["title"])
    elif item["type"] == "comment":
        author = (item.get("context") or {}).get("users", [{}])[0].get("name")
        print(f"Note from {author}: {item['comment']['body'][:80]}")

# Profile lookup + notes by handle
prof = client.user_public_profile("dickcapital")
for note_item in client.iter_notes_for_user(prof["id"], max_items=20):
    c = note_item["comment"]
    print(f"{c['date'][:10]} ♥{c['reaction_count']} {c['body'][:80]}")

# Download subscribers (requires owner role)
client.subscribers_csv(out_path="subs.csv")
```

### Publish Notes + Engage (Python library)

```python
from scripts.substack_draft import Client, Doc

client = Client(pub="yourname.substack.com")

# Plain Note
client.publish_note("Working on a draft about why everyone gets the VIX wrong.")

# Note with link attachment (renders as a rich link card)
client.publish_note(
    "Just shipped this. MIT, single file, works around the editor crashes.",
    attachment_url="https://github.com/mphinance/substack-toolkit",
)

# Rich Note built with the Doc API
note = Doc()
note.p("Three things I learned this week:")
note.p("1. ", Doc.strong("VIX <17"), " is not always a buy signal.")
note.p("2. ", Doc.em("Patience"), " is a position size.")
note.p("3. The most expensive trade is the one you take to feel something.")
client.publish_note(note)

# Engagement — library-only, no CLI
client.like_post(198832063)
client.like_note(2814629384)
client.comment_on_post(198832063, "This is the post I needed today. Thanks.")
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
- **Reader feed is rate-limited at 429.** `iter_feed()` handles a single retry per page with a 10-second sleep. If you're doing a long backfill, slow down with `inter_page_sleep=2.0` or higher and consider running in batches across hours.
- **Reader feed order isn't strictly chronological.** Some items show up out of order. If you're filtering by date, use a stop-counter (e.g. "stop after 10 consecutive items older than 24h") instead of stopping on the first old item.
- **`notes_for_user` uses cursor pagination, not offset.** The endpoint also ignores the `?types[]=comment` filter that you might assume from the URL pattern — passing it returns zero items. This skill drops the filter automatically.
- **Engagement methods are explicit on purpose.** There is no `client.like_everything_in_feed()`. Build that yourself, with your own sleeps and limits, if you want it — Substack will rate-limit or shadow-ban accounts that auto-engage at scale.

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
- **Daily reads digest.** Iterate `iter_feed(max_items=200)` over the last 24 hours, call `get_post()` on the post items, summarize each with Claude, write to a daily markdown digest.
- **Track what a writer is saying.** `iter_notes_for_user(client.user_public_profile("@someone")["id"])` gets every Note a writer has posted, with engagement metrics.
- **Newsletter analytics on your own posts.** Pull the archive, group by `audience` (`everyone` vs `only_paid`), count `comment_count`, eyeball cadence by `post_date`.
- **AI-assisted summarization.** Fetch a post's body, pass it to Claude with a "summarize for the daily digest" prompt, save the summary anywhere.
- **Migration off Substack.** Combine `iter_archive()` + `get_post()` + `subscribers_csv()` to produce a clean export folder you can import into Ghost, Beehiiv, or anywhere else.

### Publish Notes + Engage

- **Announce a post as a Note.** After publishing a long-form post, `publish_note("New piece: <hook>", attachment_url=<post_url>)` gives you the rich-card preview in the Notes feed.
- **Cross-post a tweet-length thought.** Write once in your editor, call `publish_note(text)` — no need to open the dashboard.
- **Thoughtful engagement loop.** Pull `iter_feed(max_items=20)`, let Claude decide which 2-3 items merit a comment, call `comment_on_post(post_id, body)` for each. Keep it manual-feeling; do not loop over everything.
- **Show appreciation programmatically.** When a follower comments on one of your posts, `like_note(comment_id)` or reply with `comment_on_post()` — small touches that scale without becoming spam.

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
| `notes_for_user` with `?types[]=comment` | Returns zero items, looks like the user has no notes | Drop the filter — every item on this endpoint already is a note. This skill omits the filter automatically |
| Reader feed returns 429 | API throttled mid-pagination | `iter_feed()` retries once after a 10s sleep; tune with `rate_limit_sleep` and `inter_page_sleep` |
| Note publish silently no-ops | `bodyJson` missing `attrs.schemaVersion` | `publish_note()` injects `{"schemaVersion": "v1"}` automatically when you pass a string or `Doc`

## Roadmap

- [x] Read posts and archive from a publication (v0.2)
- [x] Fetch publication metadata (v0.2)
- [x] Export subscribers as CSV (v0.2)
- [x] Reader feed for the authenticated user (v0.3)
- [x] Lookup any Substack profile by handle (v0.3)
- [x] List any user's published Notes with engagement metrics (v0.3)
- [x] Publish Substack Notes (plain, with link attachment, or rich Doc) (v0.3)
- [x] Like a post, like a Note, comment on a post (v0.3)
- [x] `safe_text()` helper for accounts where the editor still chokes on Unicode (v0.3)
- [ ] Restack a post programmatically
- [ ] Search a publication's archive (titles, full-text)
- [ ] Scheduled-publish helper
- [ ] Read comments on a post
- [ ] Following / followers iteration

## Dependencies

- `requests` — required
- `markdown-it-py` — required for the Markdown converter and the `post` CLI subcommand

## License

MIT.

---

**Inspired by:** Michael Hanko ([mphinance.substack.com](https://mphinance.substack.com)) — built because Substack's editor kept mangling pasted Markdown and there was no documented escape hatch.
