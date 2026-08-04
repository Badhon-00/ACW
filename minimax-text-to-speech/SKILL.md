---
name: minimax-text-to-speech
description: Convert text into natural speech with the MiniMax text-to-speech API. Use this skill when the user asks to synthesize, generate, or read text aloud into an audio file, choosing between synchronous HTTP, asynchronous long-form, or realtime WebSocket synthesis, across the speech-2.8-hd model family, global and China regions, and mp3/wav/flac/pcm output.
---

# MiniMax Text to Speech

Convert text into natural-sounding speech with the MiniMax text-to-speech
API. The skill covers synchronous HTTP synthesis, asynchronous long-form
synthesis with status polling, and realtime WebSocket streaming, works
against the global and China regions, defaults to the `speech-2.8-hd` model,
and supports mp3, wav, flac, and pcm output.

## When to Use This Skill

- The user wants to turn a paragraph or script into a spoken audio file.
- The user needs long-form narration generated asynchronously, or wants to
  submit a task and check its status later.
- The user wants low-latency, streamed speech for interactive or realtime use.

## What This Skill Does

1. **Synchronous HTTP synthesis**: Sends the text to `POST /v1/t2a_v2` and
   saves the returned audio locally.
2. **Asynchronous synthesis**: Creates a task with `POST /v1/t2a_async_v2`,
   polls its status, and downloads the finished file by its file id.
3. **Realtime WebSocket synthesis**: Streams audio over `WSS /ws/v1/t2a_v2`
   and reassembles the received chunks into a single audio file.

## Setup

Set your API key before running the script. The key is sent as a Bearer token.

```bash
export MINIMAX_API_KEY="your-api-key"
```

Only the Python standard library is required.

## How to Use

### Synchronous HTTP

```bash
python scripts/text_to_speech.py http "Hello from MiniMax text to speech"
```

### Asynchronous

```bash
python scripts/text_to_speech.py async "A long narration generated in the background" --no-wait
python scripts/text_to_speech.py query TASK_ID
python scripts/text_to_speech.py async "A long narration generated in the background"
```

The `async` command without `--no-wait` creates the task, polls it until the
status is `Success`, then downloads the finished audio file.

### Realtime WebSocket

```bash
python scripts/text_to_speech.py ws "Stream this sentence in realtime"
```

## Options

### Model

Use `--model` to choose a speech model (default: `speech-2.8-hd`):

- `speech-2.8-hd`, `speech-2.8-turbo`
- `speech-2.6-hd`, `speech-2.6-turbo`
- `speech-02-hd`, `speech-02-turbo`
- `speech-01-hd`, `speech-01-turbo`

```bash
python scripts/text_to_speech.py http "Faster speech" --model speech-2.8-turbo
```

### Region

Use `--region` to target the global (default) or China endpoint:

- `global`: `https://api.minimax.io/v1` (WebSocket `wss://api.minimax.io/ws/v1/t2a_v2`)
- `cn`: `https://api.minimaxi.com/v1` (WebSocket `wss://api.minimaxi.com/ws/v1/t2a_v2`)

```bash
python scripts/text_to_speech.py http "中文语音合成" --region cn
```

### Voice and Audio Settings

- `--voice-id`: Voice to synthesize with (default: `English_expressive_narrator`).
- `--speed`, `--vol`, `--pitch`: Voice speed, volume, and pitch adjustments.
- `--language-boost`: Language guidance, e.g. `auto`, `Chinese`, `English`.
- `--audio-format`: Output codec, one of `mp3`, `wav`, `flac`, `pcm` (default: `mp3`).
- `--sample-rate`, `--bitrate`, `--channel`: Audio encoding details.
- `--pronunciation-dict`: Pronunciation overrides as JSON, e.g.
  `'{"tone": ["Omg/Oh my god"]}'`.
- `--voice-modify`: Voice modification as JSON, e.g.
  `'{"pitch": 0, "intensity": 0, "timbre": 0}'`.
- `-o`, `--output`: Output file or directory (default: `/mnt/user-data/outputs`).

### HTTP-only Options

- `--output-format`: `hex`, `mp3`, `wav`, `flac`, or `pcm` (default: `hex`).
- `--stream`: Stream the audio response.
- `--subtitle-enable`: Request subtitle data in the response.

### Async Options

- `--poll-interval`: Seconds between status checks (default: 5).
- `--timeout`: Maximum seconds to wait for completion (default: 600).
- `--no-wait`: Create the task and exit without polling or downloading.

## Example

**User**: "Turn this announcement into an mp3."

**Output**:
```
Submitting text "System maintenance starts at midnight" to speech-2.8-hd (global)...
Saved audio to /mnt/user-data/outputs/speech.mp3
```

## How It Works

The skill calls four endpoints under the selected region base URL:

- `POST /v1/t2a_v2` performs synchronous synthesis and returns the audio as
  `data.audio` (hex encoded by default) with `data.status` and
  `base_resp.status_code`.
- `POST /v1/t2a_async_v2` creates an asynchronous task and returns a
  `task_id`.
- `/v1/query/t2a_async_query_v2` reports the task `status` (`Processing`,
  `Success`, `Failed`, or `Expired`) and the `file_id` once complete; the
  script sends the task id either as a GET query parameter or as a POST JSON
  body.
- `GET /v1/files/retrieve?file_id=...` returns a download URL for the finished
  audio file.

The WebSocket flow connects to `WSS /ws/v1/t2a_v2`, sends a `task_start`
event followed by one or more `task_continue` events with the text and a
`task_finish` event, then collects the hex audio from each `task_continued`
event until the task finishes. API errors are surfaced through the
`base_resp.status_code` field in each response.

## Important Notes

- Audio is saved to `/mnt/user-data/outputs/` by default; when the output is
  a directory the file is named after the task id or `speech`.
- The API key is read from the `MINIMAX_API_KEY` environment variable and
  never written to disk.
- Synchronous and WebSocket synthesis return the audio directly; asynchronous
  tasks must be polled until the status is `Success` before the file can be
  downloaded.
- Long texts are split into chunks for WebSocket synthesis.

## Common Use Cases

- Producing narration or voice-overs from a written script.
- Generating multilingual announcements or educational audio.
- Batching asynchronous synthesis tasks with `--no-wait` and collecting the
  results later.
