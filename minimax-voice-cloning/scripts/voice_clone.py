#!/usr/bin/env python3
"""Upload consented reference audio and create a MiniMax cloned voice."""

import argparse
import json
import mimetypes
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request
import uuid


REGIONS = {
    "global": {
        "upload": "https://api.minimax.io/v1/files/upload",
        "clone": "https://api.minimax.io/v1/voice_clone",
    },
    "cn": {
        "upload": "https://api.minimaxi.com/v1/files/upload",
        "clone": "https://api.minimaxi.com/v1/voice_clone",
    },
}
MODELS = ["speech-2.8-hd", "speech-2.6-hd", "speech-02-hd", "speech-01-hd"]
AUDIO_FORMATS = {".mp3", ".m4a", ".wav"}
MAX_AUDIO_BYTES = 20 * 1024 * 1024


def get_api_key():
    """Return the API key from the environment without logging it."""
    api_key = os.environ.get("MINIMAX_API_KEY")
    if not api_key:
        raise ValueError("Set MINIMAX_API_KEY before running this command")
    return api_key


def validate_audio(audio_path):
    """Validate the local requirements that do not need an audio decoder."""
    path = Path(audio_path)
    if not path.is_file():
        raise ValueError(f"Audio file does not exist: {path}")
    if path.suffix.lower() not in AUDIO_FORMATS:
        raise ValueError("Reference audio must be mp3, m4a, or wav")
    if path.stat().st_size > MAX_AUDIO_BYTES:
        raise ValueError("Reference audio must not exceed 20 MB")
    return path


def build_multipart(audio_path, boundary):
    """Build the multipart body for a voice-clone audio upload."""
    path = validate_audio(audio_path)
    filename = path.name.replace('"', "")
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    lines = [
        f"--{boundary}\r\n".encode(),
        b'Content-Disposition: form-data; name="purpose"\r\n\r\n',
        b"voice_clone\r\n",
        f"--{boundary}\r\n".encode(),
        (
            'Content-Disposition: form-data; name="file"; '
            f'filename="{filename}"\r\n'
        ).encode(),
        f"Content-Type: {content_type}\r\n\r\n".encode(),
        path.read_bytes(),
        b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    return b"".join(lines)


def check_response(response):
    """Raise when the API reports a nonzero status code."""
    base_resp = response.get("base_resp") or {}
    status_code = base_resp.get("status_code")
    if status_code is None:
        raise RuntimeError("API response did not include base_resp.status_code")
    if status_code != 0:
        status_msg = base_resp.get("status_msg", "unknown error")
        raise RuntimeError(f"API error {status_code}: {status_msg}")
    return response


def request_json(url, api_key, data, content_type):
    """Send an authenticated POST request and decode its JSON response."""
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": content_type,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            parsed = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")
        raise RuntimeError(
            f"API request failed with HTTP {error.code}: {detail}"
        ) from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"API request failed: {error.reason}") from error
    except json.JSONDecodeError as error:
        raise RuntimeError("API returned invalid JSON") from error
    return check_response(parsed)


def upload_audio(audio_path, region, api_key):
    """Upload reference audio and return its file ID."""
    boundary = f"----minimax-{uuid.uuid4().hex}"
    body = build_multipart(audio_path, boundary)
    response = request_json(
        REGIONS[region]["upload"],
        api_key,
        body,
        f"multipart/form-data; boundary={boundary}",
    )
    file_id = (response.get("file") or {}).get("file_id")
    if file_id is None:
        raise RuntimeError("Upload response did not include file.file_id")
    return file_id


def build_clone_payload(file_id, voice_id, model):
    """Build the required voice cloning request body."""
    return {"file_id": file_id, "voice_id": voice_id, "model": model}


def clone_voice(file_id, voice_id, model, region, api_key):
    """Create a cloned voice from an uploaded reference file."""
    payload = build_clone_payload(file_id, voice_id, model)
    return request_json(
        REGIONS[region]["clone"],
        api_key,
        json.dumps(payload).encode("utf-8"),
        "application/json",
    )


def add_common_options(parser, include_model=False):
    """Add the region and optional model arguments to a subcommand."""
    parser.add_argument("--region", choices=REGIONS, default="global")
    if include_model:
        parser.add_argument("--model", choices=MODELS, default=MODELS[0])


def build_parser():
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        description="Upload consented reference audio and create a MiniMax cloned voice."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    upload_parser = subparsers.add_parser("upload", help="upload reference audio")
    upload_parser.add_argument("audio", help="path to an mp3, m4a, or wav file")
    add_common_options(upload_parser)

    clone_parser = subparsers.add_parser("clone", help="create a cloned voice")
    clone_parser.add_argument("file_id", type=int, help="uploaded reference file ID")
    clone_parser.add_argument("voice_id", help="new reusable voice ID")
    add_common_options(clone_parser, include_model=True)

    workflow_parser = subparsers.add_parser(
        "workflow", help="upload reference audio and create a cloned voice"
    )
    workflow_parser.add_argument("audio", help="path to an mp3, m4a, or wav file")
    workflow_parser.add_argument("voice_id", help="new reusable voice ID")
    add_common_options(workflow_parser, include_model=True)
    return parser


def main(argv=None):
    """Run the selected upload, clone, or combined workflow."""
    args = build_parser().parse_args(argv)
    api_key = get_api_key()

    if args.command == "upload":
        file_id = upload_audio(args.audio, args.region, api_key)
        result = {"file_id": file_id, "purpose": "voice_clone"}
    elif args.command == "clone":
        response = clone_voice(
            args.file_id, args.voice_id, args.model, args.region, api_key
        )
        result = {"voice_id": args.voice_id, "response": response}
    else:
        file_id = upload_audio(args.audio, args.region, api_key)
        response = clone_voice(file_id, args.voice_id, args.model, args.region, api_key)
        result = {
            "file_id": file_id,
            "voice_id": args.voice_id,
            "response": response,
        }

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
