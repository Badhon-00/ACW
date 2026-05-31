---
name: funasr-transcription
description: Transcribe audio and video files to text using FunASR's MCP server — 50+ languages, speaker diarization, emotion detection.
---

# FunASR Audio Transcription

Transcribe audio and video files to text using [FunASR](https://github.com/modelscope/FunASR), an industrial-grade speech recognition toolkit. Supports 50+ languages with built-in VAD, punctuation restoration, speaker diarization, and emotion detection.

## When to Use This Skill

- Transcribe meeting recordings, interviews, or lectures to text
- Generate subtitles from video/audio files
- Extract spoken content from media for analysis or summarization
- Transcribe multilingual audio (50+ languages including Chinese, English, Japanese, Korean)

## What This Skill Does

1. **Speech-to-Text**: Transcribes audio files with high accuracy using SenseVoice (non-autoregressive, ~10x faster than Whisper) or Paraformer models
2. **Speaker Diarization**: Identifies who spoke when using the cam++ model
3. **Emotion Detection**: Detects speaker emotions (happy, sad, angry, neutral) built into SenseVoice
4. **Audio Event Detection**: Identifies non-speech events like laughter, applause, and music

## Setup

### Option 1: MCP Server (Recommended)

Add FunASR's built-in MCP server to your Claude Code settings:

```json
{
  "mcpServers": {
    "funasr": {
      "command": "funasr-server",
      "args": ["--mcp", "--device", "cuda"]
    }
  }
}
```

### Option 2: OpenAI-Compatible API

```bash
pip install funasr
funasr-server --device cuda
# Server runs at http://localhost:8000
# Endpoint: /v1/audio/transcriptions
```

## How to Use

### Basic Transcription

> "Transcribe this audio file: recording.wav"

### Meeting Notes with Speaker Identification

> "Transcribe meeting.mp3 and identify each speaker"

### Multilingual Transcription

> "Transcribe this Japanese audio file: interview_ja.wav"

## Example Output

```
Speaker 1 (00:00 - 00:15): Welcome everyone to today's meeting.
Speaker 2 (00:16 - 00:32): Thanks. Let me share the quarterly results.
Speaker 1 (00:33 - 00:45): The numbers look great this quarter. [happy]
```

## Links

- [FunASR GitHub](https://github.com/modelscope/FunASR) (16K+ stars)
- [SenseVoice](https://github.com/FunAudioLLM/SenseVoice) (8K+ stars)
- [Documentation](https://www.funasr.com)
