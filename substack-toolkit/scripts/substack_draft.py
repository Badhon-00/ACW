#!/usr/bin/env python3
"""
substack_draft.py — Post rich Substack drafts from Python or the command line.

Substack's writing API is undocumented and finicky. This module exposes the
working subset: native ProseMirror nodes, image upload, draft create/update,
and a Markdown converter so you can write in your editor of choice and have
the result open cleanly in the Substack editor.

────────────────────────────────────────────────────────────────────────────
QUICK START (CLI)

    # 1. Grab your session cookie:
    #    Log in at substack.com in your browser, open DevTools → Application
    #    → Cookies → substack.com, copy the value of `substack.sid`.
    export SUBSTACK_SID="s%3A..."
    export SUBSTACK_PUB="yourname.substack.com"   # optional, can also pass --pub

    python substack_draft.py auth                 # verify the cookie works
    python substack_draft.py post --body essay.md --hero hero.png
    python substack_draft.py list
    python substack_draft.py delete 12345678

essay.md can carry YAML-style frontmatter for title/subtitle/hero:

    ---
    title: When the editor stops fighting you
    subtitle: A short note about a small win
    hero: ./hero.png
    hero_caption: Mid-afternoon, the screen finally cooperated.
    ---

    # The actual post starts here.

    Some **bold** text, some *italic*, a [link](https://example.com),
    bullet lists, blockquotes, and ![inline images](./diagram.png).

────────────────────────────────────────────────────────────────────────────
QUICK START (LIBRARY)

    from substack_draft import Client, Doc

    client = Client(pub="yourname.substack.com")
    hero_url = client.upload_image("hero.png")

    doc = Doc()
    doc.h(1, "My Essay")
    doc.p("Plain paragraph.")
    doc.p("With ", Doc.strong("bold"), " and ", Doc.em("italic"),
          " and a ", Doc.link("link", "https://example.com"), ".")
    doc.bullet_list(["First item", "Second item", "Third item"])
    doc.blockquote("A small quote.")
    doc.image(hero_url, caption="The hero again, this time inline.")

    draft_id = client.create_draft(
        title="My Essay", subtitle="A subtitle",
        doc=doc, cover_image=hero_url,
    )
    print(client.edit_url(draft_id))

────────────────────────────────────────────────────────────────────────────
WHAT'S WORKING (verified against the live API, May 2026)

  • Native ProseMirror node types:
      doc, paragraph, heading (level 1-6), text, bullet_list, ordered_list,
      list_item, blockquote, image2, captionedImage, caption.
    Text marks: strong, em, link.
  • Image upload: POST /api/v1/image
      JSON body: {"image": "data:image/png;base64,..."}
      Returns: {"url": "https://substack-post-media.s3.amazonaws.com/..."}
  • Drafts:
      POST   /api/v1/drafts            — create
      PUT    /api/v1/drafts/{id}       — update (requires non-null draft_bylines)
      GET    /api/v1/drafts            — list
      GET    /api/v1/drafts/{id}       — fetch (note: returns draft_bylines:null on
                                                  unpublished drafts)
      DELETE /api/v1/drafts/{id}       — delete
  • Markdown subset: headings, paragraphs, bold (**), italic (*), links
      [text](url), bullet/ordered lists, blockquotes, and image embeds
      (![alt](src)). Local image paths are auto-uploaded.

WHAT'S NOT WORKING (do not use)

  • `rawHtml` node type — API accepts it, editor crashes opening the draft
    with "Something has gone wrong."
  • `body_html` top-level field — creates an empty draft.
  • Multipart file upload to /api/v1/image — rejected 400.
  • Tables, code blocks, footnotes — not in Substack's validated schema.

────────────────────────────────────────────────────────────────────────────
DEPENDENCIES

  requests              (required)
  markdown-it-py        (optional — only needed for Doc.from_markdown / CLI post)

  pip install requests markdown-it-py

License: MIT. Use it, fork it, sell it, whatever.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from pathlib import Path
from typing import Any, Iterable, Optional, Union

import requests

DEFAULT_PUB = os.environ.get("SUBSTACK_PUB", "yourname.substack.com")
DEFAULT_TIMEOUT = 30


# ═══════════════════════════════════════════════════════════════════════════
# ProseMirror document builder
# ═══════════════════════════════════════════════════════════════════════════

class Doc:
    """A Substack-compatible ProseMirror document.

    Use the block methods (`p`, `h`, `blockquote`, `bullet_list`, `ordered_list`,
    `image`, `raw`) to append top-level nodes. Use the static inline helpers
    (`text`, `strong`, `em`, `link`) to compose mixed-content paragraphs.

    Every block method returns `self`, so calls chain.
    """

    def __init__(self):
        self.nodes: list[dict] = []

    # ── Inline (static, return text-with-marks nodes) ──

    @staticmethod
    def text(s: str) -> dict:
        return {"type": "text", "text": str(s)}

    @staticmethod
    def strong(s: str) -> dict:
        return {"type": "text", "text": str(s), "marks": [{"type": "strong"}]}

    @staticmethod
    def em(s: str) -> dict:
        return {"type": "text", "text": str(s), "marks": [{"type": "em"}]}

    @staticmethod
    def link(s: str, href: str) -> dict:
        return {
            "type": "text", "text": str(s),
            "marks": [{"type": "link", "attrs": {
                "href": href, "target": "_blank",
                "rel": "nofollow ugc noopener", "class": None,
            }}],
        }

    # ── Blocks ──

    def _children(self, parts: Iterable[Union[str, dict]]) -> list[dict]:
        return [x if isinstance(x, dict) else self.text(str(x)) for x in parts]

    def p(self, *parts: Union[str, dict]) -> "Doc":
        """Append a paragraph. Mix strings and inline nodes."""
        self.nodes.append({"type": "paragraph", "content": self._children(parts)})
        return self

    def h(self, level: int, text: str) -> "Doc":
        """Append a heading of the given level (1-6)."""
        if not 1 <= level <= 6:
            raise ValueError("heading level must be 1..6")
        self.nodes.append({
            "type": "heading", "attrs": {"level": level},
            "content": [self.text(text)],
        })
        return self

    def blockquote(self, *paragraphs: str) -> "Doc":
        """Append a blockquote containing one paragraph per arg."""
        self.nodes.append({
            "type": "blockquote",
            "content": [
                {"type": "paragraph", "content": [self.text(t)]}
                for t in paragraphs
            ],
        })
        return self

    def bullet_list(self, items: list[Union[str, list, dict]]) -> "Doc":
        """Append a bullet list. Items can be strings, lists of block nodes, or single nodes."""
        self.nodes.append({
            "type": "bullet_list",
            "content": [_list_item(i, self) for i in items],
        })
        return self

    def ordered_list(self, items: list[Union[str, list, dict]], start: int = 1) -> "Doc":
        """Append an ordered list. `start` sets the first number (default 1)."""
        self.nodes.append({
            "type": "ordered_list", "attrs": {"start": start},
            "content": [_list_item(i, self) for i in items],
        })
        return self

    def image(self, src: str, caption: Optional[str] = None,
              width: int = 1200, height: int = 630,
              alt: Optional[str] = None, mime: str = "image/png") -> "Doc":
        """Append a captioned image. `src` must be a Substack-hosted URL — upload local files first."""
        img_node = {
            "type": "image2",
            "attrs": {
                "src": src, "fullscreen": None, "imageSize": "normal",
                "height": height, "width": width, "resizeWidth": width,
                "bytes": None, "alt": alt, "title": None, "type": mime,
                "href": None, "belowTheFold": False, "internalRedirect": None,
            },
        }
        content = [img_node]
        if caption:
            content.append({"type": "caption", "content": [self.text(caption)]})
        self.nodes.append({"type": "captionedImage", "content": content})
        return self

    def raw(self, node: dict) -> "Doc":
        """Append a raw ProseMirror node. Escape hatch for things the helpers don't cover."""
        self.nodes.append(node)
        return self

    def to_dict(self) -> dict:
        """Serialize to the {"type": "doc", ...} dict that the API wants."""
        return {"type": "doc", "content": self.nodes}

    # ── Markdown ingestion ──

    @classmethod
    def from_markdown(cls, md: str, image_uploader=None) -> "Doc":
        """Convert a Markdown string to a Substack-compatible Doc.

        Supported syntax: headings, paragraphs, bold (**), italic (*),
        links [t](u), bullet and ordered lists, blockquotes, images
        ![alt](src). Soft line breaks become spaces.

        If `image_uploader` is provided (e.g. `Client(...).upload_image`),
        any non-http image `src` is treated as a local path and uploaded.
        """
        try:
            from markdown_it import MarkdownIt
        except ImportError as e:
            raise ImportError(
                "Markdown support needs markdown-it-py. Run: "
                "pip install markdown-it-py"
            ) from e
        tokens = MarkdownIt("commonmark").parse(md)
        return _tokens_to_doc(tokens, image_uploader=image_uploader)


def _list_item(item, doc: Doc) -> dict:
    if isinstance(item, str):
        return {"type": "list_item",
                "content": [{"type": "paragraph", "content": [doc.text(item)]}]}
    if isinstance(item, list):
        return {"type": "list_item", "content": item}
    if isinstance(item, dict):
        return {"type": "list_item", "content": [item]}
    raise TypeError(f"list item must be str/list/dict, got {type(item).__name__}")


def _inline_to_nodes(children, image_uploader=None) -> list[dict]:
    """Convert markdown-it inline tokens to ProseMirror text+marks nodes."""
    out: list[dict] = []
    marks: list[dict] = []
    for tok in children:
        t = tok.type
        if t == "text":
            if tok.content:
                node = {"type": "text", "text": tok.content}
                if marks:
                    node["marks"] = [dict(m) for m in marks]
                out.append(node)
        elif t == "strong_open":
            marks.append({"type": "strong"})
        elif t == "strong_close":
            marks = [m for m in marks if m["type"] != "strong"]
        elif t == "em_open":
            marks.append({"type": "em"})
        elif t == "em_close":
            marks = [m for m in marks if m["type"] != "em"]
        elif t == "link_open":
            href = tok.attrGet("href") or ""
            marks.append({"type": "link", "attrs": {
                "href": href, "target": "_blank",
                "rel": "nofollow ugc noopener", "class": None,
            }})
        elif t == "link_close":
            marks = [m for m in marks if m["type"] != "link"]
        elif t == "softbreak":
            out.append({"type": "text", "text": " "})
        elif t == "hardbreak":
            out.append({"type": "text", "text": "\n"})
        elif t == "code_inline":
            # No code mark in the validated schema. Render as plain text.
            out.append({"type": "text", "text": tok.content})
        elif t == "image":
            src = tok.attrGet("src") or ""
            alt = tok.content or None
            if image_uploader and not src.startswith(("http://", "https://")):
                try:
                    src = image_uploader(src)
                except Exception as e:
                    print(f"  [warn] image upload failed for {src}: {e}",
                          file=sys.stderr)
            cap = ([{"type": "caption",
                     "content": [{"type": "text", "text": alt}]}]
                   if alt else [])
            # Emit as standalone block; caller decides whether to inline it.
            out.append({
                "type": "captionedImage",
                "content": [{
                    "type": "image2",
                    "attrs": {
                        "src": src, "fullscreen": None, "imageSize": "normal",
                        "height": 630, "width": 1200, "resizeWidth": 1200,
                        "bytes": None, "alt": alt, "title": None,
                        "type": "image/png", "href": None,
                        "belowTheFold": False, "internalRedirect": None,
                    },
                }] + cap,
            })
    return out


def _inline_to_text(children) -> str:
    """Flatten inline tokens to plain text (used inside headings)."""
    out = []
    for tok in children:
        if tok.type == "text":
            out.append(tok.content)
        elif tok.type in ("softbreak", "hardbreak"):
            out.append(" ")
    return "".join(out)


def _tokens_to_doc(tokens, image_uploader=None) -> Doc:
    doc = Doc()
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.type == "heading_open":
            level = int(tok.tag[1])
            text = _inline_to_text(tokens[i + 1].children)
            doc.h(level, text)
            i += 3
            continue
        if tok.type == "paragraph_open":
            inline_children = tokens[i + 1].children
            kids = _inline_to_nodes(inline_children, image_uploader)
            # Hoist a lone image out of the paragraph wrapper.
            if (len(kids) == 1 and isinstance(kids[0], dict)
                    and kids[0].get("type") == "captionedImage"):
                doc.raw(kids[0])
            else:
                doc.nodes.append({"type": "paragraph", "content": kids})
            i += 3
            continue
        if tok.type in ("bullet_list_open", "ordered_list_open"):
            items, consumed = _collect_list_items(tokens, i, image_uploader)
            if tok.type == "bullet_list_open":
                doc.bullet_list(items)
            else:
                start = int(tok.attrGet("start") or 1)
                doc.ordered_list(items, start=start)
            i += consumed
            continue
        if tok.type == "blockquote_open":
            paragraph_nodes, consumed = _collect_blockquote(tokens, i, image_uploader)
            doc.raw({"type": "blockquote", "content": paragraph_nodes})
            i += consumed
            continue
        if tok.type == "hr":
            # No horizontal_rule in the validated schema. Soft divider.
            doc.p(Doc.em("* * *"))
            i += 1
            continue
        i += 1
    return doc


def _collect_list_items(tokens, start, image_uploader):
    items: list[Any] = []
    i = start + 1
    depth = 1
    current: list[dict] = []
    while i < len(tokens) and depth > 0:
        t = tokens[i].type
        if t in ("bullet_list_open", "ordered_list_open"):
            depth += 1
            i += 1
            continue
        if t in ("bullet_list_close", "ordered_list_close"):
            depth -= 1
            if depth == 0:
                return items, i - start + 1
            i += 1
            continue
        if t == "list_item_open":
            current = []
        elif t == "list_item_close":
            items.append(current if current else "")
        elif t == "paragraph_open":
            kids = _inline_to_nodes(tokens[i + 1].children, image_uploader)
            current.append({"type": "paragraph", "content": kids})
            i += 3
            continue
        i += 1
    return items, i - start + 1


def _collect_blockquote(tokens, start, image_uploader=None):
    """Walk a blockquote and return ([paragraph_node, ...], tokens_consumed).

    Paragraphs preserve inline marks (bold, italic, link) — flattening to
    plain text would drop the href on Markdown links inside blockquotes.
    """
    paragraphs: list[dict] = []
    i = start + 1
    depth = 1
    while i < len(tokens) and depth > 0:
        t = tokens[i].type
        if t == "blockquote_open":
            depth += 1
            i += 1
            continue
        if t == "blockquote_close":
            depth -= 1
            if depth == 0:
                return paragraphs, i - start + 1
            i += 1
            continue
        if t == "paragraph_open":
            kids = _inline_to_nodes(tokens[i + 1].children, image_uploader)
            paragraphs.append({"type": "paragraph", "content": kids})
            i += 3
            continue
        i += 1
    return paragraphs, i - start + 1


# ═══════════════════════════════════════════════════════════════════════════
# Substack API client
# ═══════════════════════════════════════════════════════════════════════════

class Client:
    """Thin Substack API client.

    Auth uses the `substack.sid` cookie, passed as `SUBSTACK_SID` env var or
    `sid=` kwarg. To grab one: log in at substack.com, open DevTools →
    Application → Cookies, copy `substack.sid`.
    """

    def __init__(self, pub: Optional[str] = None,
                 sid: Optional[str] = None,
                 timeout: int = DEFAULT_TIMEOUT):
        self.pub = pub or os.environ.get("SUBSTACK_PUB") or DEFAULT_PUB
        self.timeout = timeout
        self.sid = sid or os.environ.get("SUBSTACK_SID", "")
        if not self.sid:
            raise ValueError(
                "SUBSTACK_SID not set. Export it or pass sid=...\n"
                "  Grab it from your browser: DevTools > Application > Cookies > substack.sid"
            )
        self.session = requests.Session()
        self.session.cookies.set("substack.sid", self.sid, domain=".substack.com")
        self._user_id: Optional[int] = None

    @property
    def _json_headers(self) -> dict:
        return {"Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json"}

    @property
    def user_id(self) -> int:
        if self._user_id is None:
            self._user_id = self._resolve_user_id()
        return self._user_id

    def _resolve_user_id(self) -> int:
        r = self.session.get(f"https://{self.pub}/api/v1/drafts?limit=1",
                             headers=self._json_headers, timeout=self.timeout)
        if r.status_code == 200:
            data = r.json()
            posts = data.get("posts", data) if isinstance(data, dict) else data
            if isinstance(posts, list) and posts:
                b = (posts[0].get("publishedBylines")
                     or posts[0].get("draft_bylines") or [])
                if b and b[0].get("id") is not None:
                    return b[0]["id"]
        r2 = self.session.get(f"https://{self.pub}/api/v1/archive?sort=new&limit=1",
                              headers=self._json_headers, timeout=self.timeout)
        if r2.status_code == 200:
            arr = r2.json()
            if arr and arr[0].get("publishedBylines"):
                return arr[0]["publishedBylines"][0]["id"]
        raise RuntimeError("Could not resolve user_id. SID may be expired.")

    def check_auth(self) -> bool:
        try:
            _ = self.user_id
            return True
        except Exception:
            return False

    # ── Images ──

    _MIME_MAP = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png",
                 "gif": "gif", "webp": "webp"}

    def upload_image(self, path: Union[str, Path]) -> str:
        """Upload a local image. Returns the public S3 URL Substack hosts it at.

        Uses POST /api/v1/image with a JSON `{"image": "data:...;base64,..."}`
        body. The multipart form upload approach is rejected.
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(p)
        suffix = p.suffix.lower().lstrip(".") or "png"
        mime = self._MIME_MAP.get(suffix, "png")
        with open(p, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        r = self.session.post(
            f"https://{self.pub}/api/v1/image",
            json={"image": f"data:image/{mime};base64,{b64}"},
            headers=self._json_headers,
            timeout=60,
        )
        if r.status_code not in (200, 201):
            raise RuntimeError(
                f"Image upload failed: {r.status_code} {r.text[:300]}"
            )
        d = r.json()
        url = (d.get("url") or d.get("imageUrl")
               or (d.get("attachment") or {}).get("imageUrl")
               or (d.get("attachment") or {}).get("url"))
        if not url:
            raise RuntimeError(f"Upload returned 200 but no URL: {d}")
        return url

    # ── Reads ──

    def user_self(self) -> dict:
        """Current authenticated user's profile.

        Hits the global substack.com endpoint, not your publication subdomain.
        Returns at minimum: id, name, handle, photo_url, email.

        Note: this endpoint returns 403 for some accounts (Substack appears
        to gate it behind an anti-bot or session-scope check that is not
        well-documented). If you only need the user ID, use the `user_id`
        property on this Client instead — it resolves from drafts/archive
        bylines and is more reliable.
        """
        r = self.session.get(
            "https://substack.com/api/v1/user/self",
            headers=self._json_headers, timeout=self.timeout,
        )
        if r.status_code != 200:
            raise RuntimeError(
                f"user_self failed: {r.status_code} {r.text[:200]} "
                "(some accounts always 403 here; use the client.user_id property instead)"
            )
        return r.json()

    def publication(self) -> dict:
        """Publication metadata: name, hero, bylines, custom domain, theme."""
        r = self.session.get(
            f"https://{self.pub}/api/v1/publication",
            headers=self._json_headers, timeout=self.timeout,
        )
        if r.status_code != 200:
            raise RuntimeError(f"publication failed: {r.status_code} {r.text[:200]}")
        return r.json()

    def archive(self, sort: str = "new", limit: int = 10,
                offset: int = 0) -> list[dict]:
        """List published posts in this publication's archive.

        Returns a list of post dicts with keys including: id, title,
        subtitle, slug, canonical_url, audience, post_date,
        publishedBylines, type, description, cover_image.

        Args:
          sort: 'new', 'old', or 'community' (engagement-sorted).
          limit: posts per page. Substack caps around 50.
          offset: pagination offset.
        """
        r = self.session.get(
            f"https://{self.pub}/api/v1/archive"
            f"?sort={sort}&limit={limit}&offset={offset}",
            headers=self._json_headers, timeout=self.timeout,
        )
        if r.status_code != 200:
            raise RuntimeError(f"archive failed: {r.status_code} {r.text[:200]}")
        data = r.json()
        return data if isinstance(data, list) else data.get("posts", [])

    def iter_archive(self, sort: str = "new", page_size: int = 25):
        """Generator over the full archive. Stops when a short page returns."""
        offset = 0
        while True:
            page = self.archive(sort=sort, limit=page_size, offset=offset)
            if not page:
                return
            for post in page:
                yield post
            offset += len(page)
            if len(page) < page_size:
                return

    def get_post(self, slug_or_id: Union[str, int]) -> dict:
        """Fetch a single published post by slug or numeric ID.

        Returns the post dict (unwrapped from the API's `{post, publication,
        subscription, ...}` envelope) with all fields including
        `body_html`, `cover_image`, `description`, `audience`, `post_date`,
        `canonical_url`, `comment_count`, `truncated_body_text`.

        If the response shape ever changes, this method raises a RuntimeError
        with the available top-level keys for debugging.
        """
        candidates = [
            f"https://{self.pub}/api/v1/posts/{slug_or_id}",
            f"https://{self.pub}/api/v1/posts/by-id/{slug_or_id}",
        ]
        last_err = None
        for url in candidates:
            r = self.session.get(url, headers=self._json_headers,
                                 timeout=self.timeout)
            if r.status_code == 200:
                data = r.json()
                # Unwrap the envelope; fall through to raw if shape is unexpected.
                if isinstance(data, dict) and "post" in data and isinstance(data["post"], dict):
                    return data["post"]
                if isinstance(data, dict) and "body_html" in data:
                    return data
                raise RuntimeError(
                    f"get_post returned an unexpected shape: "
                    f"top-level keys={sorted(data.keys()) if isinstance(data, dict) else type(data).__name__}"
                )
            last_err = f"{r.status_code} {r.text[:120]}"
        raise RuntimeError(f"get_post failed for {slug_or_id}: {last_err}")

    def subscribers_csv(self, out_path: Union[str, Path, None] = None
                        ) -> Optional[bytes]:
        """Download the subscriber list as CSV. Requires owner role.

        Some publications serve subscriber data only through dashboard JS;
        if the direct API returns a non-CSV payload, fall back to the
        Playwright recipe in README.md.

        Returns the CSV bytes. If `out_path` is given, also writes to disk.
        """
        r = self.session.get(
            f"https://{self.pub}/api/v1/subscribers/export",
            headers={"User-Agent": "Mozilla/5.0",
                     "Accept": "text/csv,application/octet-stream,*/*"},
            timeout=120,
        )
        if r.status_code != 200:
            raise RuntimeError(
                f"subscribers_csv failed: {r.status_code} {r.text[:200]}"
            )
        ct = r.headers.get("content-type", "")
        if not any(t in ct for t in ("csv", "octet", "text/plain")):
            raise RuntimeError(
                f"Subscriber export returned non-CSV content-type: {ct!r}. "
                "Owner role required; some accounts need the Playwright "
                "dashboard-scraping fallback documented in README."
            )
        csv_bytes = r.content
        if out_path:
            Path(out_path).write_bytes(csv_bytes)
        return csv_bytes

    # ── Drafts ──

    def create_draft(self, title: str, subtitle: str,
                     doc: Union[Doc, dict],
                     audience: str = "everyone",
                     cover_image: Optional[str] = None) -> int:
        """Create a draft. Returns its numeric ID."""
        body = doc.to_dict() if isinstance(doc, Doc) else doc
        payload = {
            "draft_title": title,
            "draft_subtitle": subtitle,
            "draft_body": json.dumps(body),
            "draft_bylines": [{"id": self.user_id, "is_guest": False}],
            "type": "newsletter",
            "audience": audience,
        }
        if cover_image:
            payload["cover_image"] = cover_image
        r = self.session.post(f"https://{self.pub}/api/v1/drafts",
                              json=payload, headers=self._json_headers,
                              timeout=self.timeout)
        if r.status_code not in (200, 201):
            raise RuntimeError(
                f"Draft create failed: {r.status_code} {r.text[:400]}"
            )
        return r.json()["id"]

    def update_draft(self, draft_id: int, *,
                     title: Optional[str] = None,
                     subtitle: Optional[str] = None,
                     doc: Union[Doc, dict, None] = None,
                     cover_image: Optional[str] = None,
                     audience: Optional[str] = None) -> None:
        """Patch an existing draft. Only provided fields are changed.

        Workaround note: a GET on an unpublished draft returns
        `draft_bylines: null`, but the PUT requires non-null bylines.
        We resolve and inject them.
        """
        r = self.session.get(f"https://{self.pub}/api/v1/drafts/{draft_id}",
                             headers=self._json_headers, timeout=self.timeout)
        if r.status_code != 200:
            raise RuntimeError(
                f"Draft fetch failed: {r.status_code} {r.text[:300]}"
            )
        d = r.json()
        bylines = d.get("draft_bylines") or d.get("publishedBylines") or [
            {"id": self.user_id, "is_guest": False}
        ]
        body_raw = d.get("draft_body") or "{}"
        body_obj = json.loads(body_raw) if isinstance(body_raw, str) else body_raw
        if doc is not None:
            body_obj = doc.to_dict() if isinstance(doc, Doc) else doc

        payload = {
            "draft_title": title if title is not None else d.get("draft_title"),
            "draft_subtitle": subtitle if subtitle is not None else d.get("draft_subtitle"),
            "draft_body": json.dumps(body_obj),
            "draft_bylines": bylines,
            "type": d.get("type") or "newsletter",
            "audience": audience or d.get("audience") or "everyone",
        }
        if cover_image is not None:
            payload["cover_image"] = cover_image
        elif d.get("cover_image"):
            payload["cover_image"] = d["cover_image"]

        r = self.session.put(f"https://{self.pub}/api/v1/drafts/{draft_id}",
                             json=payload, headers=self._json_headers,
                             timeout=self.timeout)
        if r.status_code not in (200, 201):
            raise RuntimeError(
                f"Draft update failed: {r.status_code} {r.text[:400]}"
            )

    def list_drafts(self, limit: int = 10) -> list[dict]:
        r = self.session.get(f"https://{self.pub}/api/v1/drafts?limit={limit}",
                             headers=self._json_headers, timeout=self.timeout)
        if r.status_code != 200:
            raise RuntimeError(f"List failed: {r.status_code} {r.text[:200]}")
        data = r.json()
        return data.get("posts", data) if isinstance(data, dict) else data

    def delete_draft(self, draft_id: int) -> None:
        r = self.session.delete(f"https://{self.pub}/api/v1/drafts/{draft_id}",
                                headers=self._json_headers,
                                timeout=self.timeout)
        if r.status_code not in (200, 201, 204):
            raise RuntimeError(
                f"Delete failed: {r.status_code} {r.text[:200]}"
            )

    def edit_url(self, draft_id: int) -> str:
        return f"https://{self.pub}/publish/post/{draft_id}"


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def _parse_frontmatter(md_text: str) -> tuple[dict, str]:
    """Strip YAML-ish frontmatter (`--- ... ---`) and return (meta, body)."""
    if not md_text.lstrip().startswith("---"):
        return {}, md_text
    md_text = md_text.lstrip()
    end = md_text.find("\n---", 3)
    if end < 0:
        return {}, md_text
    front = md_text[3:end].strip()
    body = md_text[end + 4:].lstrip("\n")
    meta: dict[str, str] = {}
    for line in front.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body


def _cli_auth(args):
    client = Client(pub=args.pub)
    if client.check_auth():
        print(f"OK — authenticated as user {client.user_id} on {client.pub}")
    else:
        sys.exit("SID expired or invalid")


def _cli_post(args):
    client = Client(pub=args.pub)
    md_text = Path(args.body).read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(md_text)

    title = args.title or meta.get("title")
    subtitle = args.subtitle or meta.get("subtitle", "")
    hero = args.hero or meta.get("hero")
    hero_caption = meta.get("hero_caption")
    if not title:
        sys.exit("--title is required (or set 'title:' in markdown frontmatter)")

    hero_url = None
    if hero:
        hero_path = Path(hero)
        if not hero_path.is_absolute():
            hero_path = Path(args.body).resolve().parent / hero_path
        print(f"Uploading hero {hero_path}...")
        hero_url = client.upload_image(hero_path)
        print(f"  {hero_url}")

    print("Converting markdown...")
    # Resolve relative image paths inside the markdown against the markdown's dir.
    md_dir = Path(args.body).resolve().parent

    def upload_relative(src):
        p = Path(src)
        if not p.is_absolute():
            p = md_dir / p
        return client.upload_image(p)

    doc = Doc.from_markdown(body, image_uploader=upload_relative)

    if hero_url:
        # Prepend hero as the first block.
        prepend = Doc()
        prepend.image(hero_url, caption=hero_caption)
        prepend.nodes.extend(doc.nodes)
        doc = prepend

    print(f"Creating draft on {client.pub}...")
    draft_id = client.create_draft(title, subtitle, doc,
                                   cover_image=hero_url)
    print(f"Draft created: {client.edit_url(draft_id)}")


def _cli_list(args):
    client = Client(pub=args.pub)
    drafts = client.list_drafts(limit=args.limit)
    if not drafts:
        print("No drafts.")
        return
    for d in drafts:
        did = d.get("id")
        title = d.get("draft_title") or d.get("title") or "(untitled)"
        print(f"  [{did}] {title[:80]}")


def _cli_delete(args):
    client = Client(pub=args.pub)
    client.delete_draft(args.draft_id)
    print(f"Deleted draft {args.draft_id}")


def _cli_whoami(args):
    client = Client(pub=args.pub)
    u = client.user_self()
    print(f"id:     {u.get('id')}")
    print(f"name:   {u.get('name')}")
    print(f"handle: {u.get('handle')}")
    print(f"email:  {u.get('email')}")


def _cli_publication(args):
    client = Client(pub=args.pub)
    p = client.publication()
    print(f"name:           {p.get('name')}")
    print(f"hero:           {p.get('hero_text')}")
    print(f"custom_domain:  {p.get('custom_domain')}")
    bylines = p.get("bylines") or []
    if bylines:
        print(f"bylines:        {', '.join(b.get('name', '?') for b in bylines)}")


def _cli_archive(args):
    client = Client(pub=args.pub)
    posts = client.archive(sort=args.sort, limit=args.limit, offset=args.offset)
    if not posts:
        print("No posts in this page.")
        return
    for p in posts:
        pid = p.get("id")
        title = (p.get("title") or "(untitled)")[:70]
        date = (p.get("post_date") or p.get("publishedAt") or "")[:10]
        audience = p.get("audience", "?")
        print(f"  [{pid}] {date}  {audience:10s}  {title}")


def _cli_subscribers(args):
    client = Client(pub=args.pub)
    out = Path(args.out) if args.out else Path(
        f"subscribers_{__import__('datetime').date.today().isoformat()}.csv"
    )
    csv_bytes = client.subscribers_csv(out_path=out)
    print(f"Wrote {len(csv_bytes)} bytes to {out}")


def _cli_get_post(args):
    client = Client(pub=args.pub)
    post = client.get_post(args.id_or_slug)
    if args.body:
        # Just the body HTML, for piping into pandoc or similar.
        print(post.get("body_html") or "")
        return
    print(f"id:           {post.get('id')}")
    print(f"title:        {post.get('title')}")
    print(f"subtitle:     {post.get('subtitle')}")
    print(f"audience:     {post.get('audience')}")
    print(f"post_date:    {post.get('post_date')}")
    print(f"canonical:    {post.get('canonical_url')}")
    print(f"comments:     {post.get('comment_count')}")
    print(f"body_html:    {len(post.get('body_html') or '')} bytes")
    if args.out:
        Path(args.out).write_text(post.get("body_html") or "", encoding="utf-8")
        print(f"Wrote body HTML to {args.out}")


def _build_parser():
    p = argparse.ArgumentParser(
        prog="substack_draft",
        description="Post rich drafts to Substack from Python or the command line.",
    )
    p.add_argument("--pub", default=None,
                   help="Publication domain (e.g. yourname.substack.com). "
                        "Defaults to $SUBSTACK_PUB.")
    sub = p.add_subparsers(dest="cmd", required=True)

    ap = sub.add_parser("auth", help="Verify SUBSTACK_SID works.")
    ap.set_defaults(func=_cli_auth)

    pp = sub.add_parser("post", help="Create a draft from a Markdown file.")
    pp.add_argument("--title", help="Title (overrides frontmatter).")
    pp.add_argument("--subtitle", help="Subtitle (overrides frontmatter).")
    pp.add_argument("--body", required=True, help="Path to markdown file.")
    pp.add_argument("--hero",
                    help="Path to hero image. Used as cover_image and "
                         "prepended to the body.")
    pp.set_defaults(func=_cli_post)

    lp = sub.add_parser("list", help="List recent drafts.")
    lp.add_argument("--limit", type=int, default=10)
    lp.set_defaults(func=_cli_list)

    dp = sub.add_parser("delete", help="Delete a draft by ID.")
    dp.add_argument("draft_id", type=int)
    dp.set_defaults(func=_cli_delete)

    wp = sub.add_parser("whoami", help="Show the authenticated user.")
    wp.set_defaults(func=_cli_whoami)

    pup = sub.add_parser("publication", help="Show publication metadata.")
    pup.set_defaults(func=_cli_publication)

    arp = sub.add_parser("archive", help="List published posts.")
    arp.add_argument("--sort", default="new", choices=["new", "old", "community"])
    arp.add_argument("--limit", type=int, default=10)
    arp.add_argument("--offset", type=int, default=0)
    arp.set_defaults(func=_cli_archive)

    sp = sub.add_parser("subscribers", help="Download subscriber CSV (owner only).")
    sp.add_argument("--out", help="Output path (default: subscribers_YYYY-MM-DD.csv)")
    sp.set_defaults(func=_cli_subscribers)

    gp = sub.add_parser("get", help="Fetch a single post by ID or slug.")
    gp.add_argument("id_or_slug",
                    help="Numeric post ID or string slug.")
    gp.add_argument("--body", action="store_true",
                    help="Print only the body HTML, suitable for piping.")
    gp.add_argument("--out", help="Write body HTML to a file.")
    gp.set_defaults(func=_cli_get_post)

    return p


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
