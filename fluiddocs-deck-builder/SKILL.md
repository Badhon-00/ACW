---
name: fluiddocs-deck-builder
description: Builds single-file, type-correct HTML decks (pitch, sales, launch, keynote, all-hands) from a one-line brief, with PDF and PPTX import and inline editing. Works with Claude Code, Codex, Gemini CLI, and OpenCode.
---

# FluidDocs Deck Builder

## When to Use
Use this when you need a real, presentation-ready slide deck from a short brief, or when you want to turn an existing PDF or PPTX deck into an editable HTML one. It fits pitch decks, sales decks, launch decks, keynotes, and all-hands.

## What It Does
Builds one self-contained HTML file per deck on a fixed 1440x810 canvas, with a content spine specific to the deck type, so the structure is correct (a pitch is not a sales deck is not an all-hands). It can import a PDF or PPTX and rebuild it as a navigable, inline-editable HTML deck with the original screenshots preserved. A three-reviewer pass (Brand, Copy, Layout) runs before output. No build step, no dependencies.

## How to Use
Install it as a plugin, or drop the skill into your agent. Then give a one-line brief. To import, point it at a PDF or PPTX and ask it to rebuild as HTML. In the output, press E to edit any element inline and Ctrl+S to save a new file.

Source and install: https://github.com/FluidForm-ai/fluiddocs-deck-builder

## Example
Prompt: "Build a 14-slide seed pitch for Switchboard, an observability layer for LLM workloads. Use the Airbnb template."
Output: a single switchboard-pitch.html file you can open offline, arrow-key through, and edit inline.
