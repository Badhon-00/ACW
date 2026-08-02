---
name: filaxy-watch
description: Watch a video (YouTube, TikTok, Vimeo, X, Loom, or a local file) and answer questions about it, grounded in real extracted frames and a timestamped transcript rather than a guess from the title. Use this skill when the user shares a video URL or local video file and asks what happens in it, wants a summary, wants a bug diagnosed from a screen recording, or asks about a specific moment.
---

# Filaxy Watch

Gives Claude an actual video input. A bundled Python script downloads the video (or just its captions when that's enough), extracts frames at an auto-scaled rate, gets a timestamped transcript, and hands both to Claude — which then reads every frame as an image and answers grounded in what it actually saw and heard.

## When to Use This Skill

- The user pastes a video URL (YouTube, TikTok, Vimeo, X, Loom, and hundreds of other sites via yt-dlp) or a local file path (`.mp4`, `.mov`, `.mkv`, `.webm`) and asks a question about it.
- Diagnosing a bug from a screen recording — "what's going wrong here?"
- Summarizing a long video instead of watching it manually.
- Breaking down someone else's content — "what hook did they open with?"
- Zooming into a specific moment — "what happens around 2:30?"

## What This Skill Does

1. **Downloads only what's needed.** Checks for free native captions first; skips the full video download entirely when a caption-only answer is enough.
2. **Extracts frames with an auto-scaled budget.** Duration-aware sampling (denser for short clips, capped for long ones) so a 45-minute video doesn't blow the context window. A dedup pass drops near-identical frames (held slides, static screen recordings) before the budget is spent.
3. **Gets a transcript.** Native captions when available; Whisper (Groq or OpenAI) as a fallback when they're not.
4. **Hands frames + transcript to Claude.** Claude `Read`s every frame path as an image and answers using both the visual and spoken content.

## How to Use

### Basic Usage

```
Watch this and tell me what happens at the 30 second mark: https://youtu.be/dQw4w9WgXcQ
```

### Advanced Usage

```bash
# Zoom into a specific section instead of sampling the whole video:
python3 scripts/watch.py "https://youtu.be/abc" --start 2:15 --end 2:45

# Multiple videos in one call, each gets its own report section:
python3 scripts/watch.py video1.mp4 video2.mp4 "compare how each one opens"

# Fast pass, keyframes only, no transcription:
python3 scripts/watch.py bug-repro.mov --detail efficient --no-whisper
```

## Example

**User**: "Someone sent me this screen recording — what's breaking? ~/Movies/bug.mov"

**Output**: Claude runs the script, which extracts frames across the clip and a transcript (if there's narration), then Claude reads the frames and answers something like: "At 0:14 the 'Save' button starts overflowing its container — the frame right before that shows the layout still intact, so it's the click handler at that point resizing something incorrectly, not a CSS load-order issue."

## Setup

First run installs `ffmpeg` and `yt-dlp` automatically on macOS (via Homebrew) and prints exact install commands on Linux/Windows. A Whisper API key (Groq or OpenAI, either free-tier friendly) is optional — only needed for videos with no native captions at all.

## Tips

- Pass `--start`/`--end` whenever the user names a specific moment — it densifies frame sampling around that window instead of spreading frames thin across the whole video.
- Re-asking about the same URL reuses the cached download automatically — no need to re-fetch.
- Bump `--resolution 1024` when the user needs to read on-screen text (slides, terminal output, code).

## Common Use Cases

- Bug repro diagnosis from a shared screen recording
- Competitor/content breakdown ("what hook did they use?")
- Long-video summarization
- Turning a video into searchable notes

**Inspired by:** [Brad Bonanno](https://www.youtube.com/@bradbonanno)'s [`claude-video`](https://github.com/bradautomates/claude-video) project (MIT License). This is a rebrand/fork under the Filaxy brand with three added improvements — a download cache, live extraction progress, and multi-video support in one call. Full docs: [github.com/othmarodev/Filaxy-whatch_skill_for_claude](https://github.com/othmarodev/Filaxy-whatch_skill_for_claude).
