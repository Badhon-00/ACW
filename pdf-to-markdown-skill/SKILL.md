---
name: pdf-to-markdown-skill
description: Convert a text-based PDF into a clean Markdown (or HTML) document that is easy for AI to read, with images extracted into an assets/ folder and scan-like pages detected and flagged. Use this skill whenever the user mentions converting a PDF to Markdown, extracting PDF text for AI reading, "把 PDF 转成 Markdown", "把 PDF 变成 AI 能读的文档", turning lecture notes / textbook chapters / papers into .md, or any request where a document-type PDF should become an AI-friendly text file. This works for text-based PDFs (course slides, textbooks, papers, reports) that may contain a few images. It does NOT do OCR: pure-image pages are detected and flagged so the reader knows text is missing. Make sure to use this skill even if the user doesn't explicitly say "convert" — if they want to read or analyze a document PDF as text, this skill produces the fastest path.
license: MIT
---

# PDF → Markdown

Turn a text-based PDF into a single self-contained folder containing a clean Markdown document, extracted images, and a scan report. The goal: after conversion, reading the .md is as good as reading the original PDF — without re-opening the PDF.

## When to use / when not to use

- **Use for**: document-type PDFs — course slides, textbook chapters, papers, reports — where the text layer exists (you can select text in a PDF viewer).
- **Not for**: pure scan/image PDFs (no selectable text). The script detects and flags those pages, but text extraction will be missing on them — tell the user, and suggest OCR as a separate step. Do not attempt OCR inside this skill.
- **Not for**: creating or editing PDFs, filling forms, page manipulation. Use the `pdf` skill for those.

## Quick start

```bash
python scripts/pdf2md.py <input.pdf> [-o <outdir>] [-f md|html|both]
```

Default output: `<input's folder>/<pdf basename>/` containing:

```
<basename>/
├── <basename>.md        ← Markdown with a conversion report header
├── assets/              ← extracted images (png/jpg), referenced via relative paths
└── scan_report.json     ← machine-readable scan detection results
```

The Markdown starts with an HTML-comment report block. Read it first — it tells you which pages lost content (scan-like, blank, dense math, broken fonts).

## Interpreter check (Windows pitfall)

The system `python` on Windows may be a stub without packages. Dependencies: `pymupdf4llm`, plus `markdown` for the HTML format. Before running, verify:

```bash
python -c "import pymupdf4llm"
py -3 -c "import pymupdf4llm"
```
(Either command succeeding means the dependency is available; the second is for machines where the first `python` is a stub.)

If both fail, locate a real Python (e.g. `C:\Users\Lenovo\AppData\Local\Programs\Python\Python313\python.exe`) and use its absolute path for the script too. Output filenames may contain non-ASCII characters — always pass paths as arguments, never rely on a shell working directory that might mangle them.

## Options

| Flag | Default | Meaning |
|------|---------|---------|
| `-o, --outdir` | `<pdf basename>/` next to input | Output directory (created if missing) |
| `-f, --format` | `md` | `md`, `html`, or `both` |
| `--image-format` | `png` | `png` or `jpg` for extracted assets |
| `--scan-threshold` | `30` | Max chars per page before flagging as scan/blank |
| `--no-scan-check` | off | Skip scan-page detection (faster) |

## Conversion report

The report block at the top of the .md explains what may be missing, so the reader can trust what follows:

- `⚠️ Page N: looks like a pure-image page (X chars, Y images) — no text layer extracted. Check assets/ or OCR it separately.` — scan-like page: little text but contains images. Expect its content to be absent.
- `ℹ️ Page N: blank page (X chars).` — nothing there at all.
- `⚠️ Pages A-B, D: dense math — formulas extract poorly (one symbol per line).` — formulas in the original will look broken; verify manually if formulas matter.
- `⚠️ Font mapping missing (X% glyphs are (cid:…)) — some text may be garbled.` — the PDF embeds fonts without proper mapping; extraction quality is the source file's fault, not fixable here.

If the user only wants the text (not images), it's fine to run with the default options and just read the .md — images stay in assets/ and don't clutter the text.

## How it works

1. **Detect** — per-page text density: pages with few chars and images → scan-like; few chars and no images → blank. `page.get_text()` and `page.get_images()` are read per page (no OCR).
2. **Convert** — `pymupdf4llm.to_markdown(write_images=True, image_path="assets/")` handles headings, lists, and tables. The HTML format is rendered from the same Markdown (markdown lib with tables/fenced_code extensions), so both formats stay identical.
3. **Annotate** — prepend the conversion report; rewrite absolute image paths to relative `assets/` so the output folder is portable (e.g. zipped, committed, uploaded).

## Known limitations

- Formulas extract one symbol per line — inherently broken; the report flags dense-math pages.
- Table fidelity depends on the source PDF's borders; complex tables may lose alignment.
- Scanned pages have no text — detected and flagged, not extracted. No OCR.
- Source PDFs with text-order issues (e.g. PPT exports, translated two-column layouts) will show garbled ordering in the .md — same as any text extraction, not fixable by this skill.
