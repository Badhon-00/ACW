---
name: minimax-voice-cloning
description: Create a reusable MiniMax voice from consented reference audio. Use this skill when the user asks to upload an mp3, m4a, or wav sample and clone its voice through the global or China MiniMax API.
---

# MiniMax Voice Cloning

Upload a reference recording and create a reusable voice ID with the MiniMax
voice cloning API. The included command-line tool supports the complete upload
and clone workflow, either as separate steps or as one command.

Only clone a voice when the speaker has explicitly consented to that use. Do
not use recordings obtained deceptively, or impersonate someone without their
permission.

## Setup

Set the API key as an environment variable. It is sent as a Bearer token and
is never written to disk.

```bash
export MINIMAX_API_KEY="your-api-key"
```

The tool uses only the Python standard library.

## Clone a Voice in One Step

Run `workflow` with the consented sample and the new voice ID:

```bash
python scripts/voice_clone.py workflow ./sample.wav my-consented-voice
```

This uploads the file with the `voice_clone` purpose, obtains its file ID,
and submits that ID with the requested voice ID and model to the clone API.
The result is printed as JSON containing `file_id`, `voice_id`, and the API
response.

## Run the Steps Separately

Upload the sample:

```bash
python scripts/voice_clone.py upload ./sample.mp3
```

Copy the returned `file_id`, then create the voice:

```bash
python scripts/voice_clone.py clone 123456789 my-consented-voice
```

## Options

### Region

Use `--region global` (the default) for `api.minimax.io`, or `--region cn`
for `api.minimaxi.com`:

```bash
python scripts/voice_clone.py workflow ./sample.m4a my-consented-voice --region cn
```

The upload and clone calls always use the same selected region.

### Model

The default model is `speech-2.8-hd`. The supported voice-cloning models are:

- `speech-2.8-hd`
- `speech-2.6-hd`
- `speech-02-hd`
- `speech-01-hd`

Choose one with `--model` on `clone` or `workflow`:

```bash
python scripts/voice_clone.py clone 123456789 my-consented-voice --model speech-2.6-hd
```

## Reference Audio Requirements

- Format: mp3, m4a, or wav
- Duration: 10 seconds to 5 minutes
- Size: no more than 20 MB

The tool validates the format and size before upload. Use a clear recording
with little background noise, and verify the speaker's consent before sending
it.

## How It Works

1. `POST /v1/files/upload` sends the recording as multipart form data with
   `purpose=voice_clone` and reads `file.file_id` from the response.
2. `POST /v1/voice_clone` sends the required `file_id`, `voice_id`, and
   `model` fields as JSON.
3. Both responses are checked for a successful `base_resp.status_code` before
   any identifier is reported.

## Common Use Cases

- Creating an approved brand voice from a professional voice actor's sample.
- Preserving a speaker's delivery across authorized narration projects.
- Preparing a reusable voice ID for a consented localization workflow.
