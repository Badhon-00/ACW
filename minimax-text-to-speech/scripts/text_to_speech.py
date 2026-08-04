#!/usr/bin/env python3
"""
MiniMax Text to Speech

Convert text into natural speech using the MiniMax text-to-speech API.
Supports synchronous HTTP synthesis, asynchronous long-form synthesis with
status polling, and realtime WebSocket streaming, against both the global and
China endpoints, across the speech-2.8-hd model family and the mp3, wav, flac
and pcm audio formats.

Only the Python standard library is required.

Set your API key in the MINIMAX_API_KEY environment variable (or pass
--api-key). The key is sent as a Bearer token and is never written to disk.
"""

import argparse
import base64
import hashlib
import json
import os
import socket
import ssl
import struct
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# Regional API hosts. "global" serves international traffic, "cn" serves
# mainland China. Both expose the same base path for each API version.
REGIONS = {
    "global": "https://api.minimax.io/v1",
    "cn": "https://api.minimaxi.com/v1",
}

# WebSocket endpoints for realtime synthesis, one per region.
WS_REGIONS = {
    "global": "wss://api.minimax.io/ws/v1/t2a_v2",
    "cn": "wss://api.minimaxi.com/ws/v1/t2a_v2",
}

MODELS = [
    "speech-2.8-hd",
    "speech-2.8-turbo",
    "speech-2.6-hd",
    "speech-2.6-turbo",
    "speech-02-hd",
    "speech-02-turbo",
    "speech-01-hd",
    "speech-01-turbo",
]
DEFAULT_MODEL = "speech-2.8-hd"

AUDIO_FORMATS = ["mp3", "wav", "flac", "pcm"]
OUTPUT_FORMATS = ["hex", *AUDIO_FORMATS]
DEFAULT_VOICE = "English_expressive_narrator"

SUCCESS_STATES = {"success", "succeeded", "complete", "completed"}
FAILURE_STATES = {"fail", "failed", "error", "expired", "cancelled"}

_WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def base_url(region):
    """Return the API base URL for a region."""
    try:
        return REGIONS[region]
    except KeyError:
        raise ValueError(f"Unknown region '{region}'. Choose from: {', '.join(REGIONS)}")


def get_api_key(cli_key):
    """Resolve the API key from the CLI flag or the environment."""
    key = cli_key or os.environ.get("MINIMAX_API_KEY")
    if not key:
        print("Error: no API key. Set MINIMAX_API_KEY or pass --api-key.")
        sys.exit(2)
    return key


def _check_base_resp(parsed):
    """Raise if the API signalled an error via base_resp.status_code."""
    base_resp = parsed.get("base_resp") or {}
    status_code = base_resp.get("status_code")
    if status_code not in (None, 0):
        message = base_resp.get("status_msg", "unknown error")
        raise RuntimeError(f"API error {status_code}: {message}")


def _request(url, api_key, method="GET", payload=None, raw=False):
    """Perform an HTTP request and return the decoded JSON (or raw body)."""
    data = None
    headers = {"Authorization": f"Bearer {api_key}"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {exc.code} calling {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error calling {url}: {exc.reason}") from exc

    if raw:
        return body
    parsed = json.loads(body)
    _check_base_resp(parsed)
    return parsed


def _build_voice_setting(args):
    """Build the voice_setting object from CLI options."""
    return {
        "voice_id": args.voice_id,
        "speed": args.speed,
        "vol": args.vol,
        "pitch": args.pitch,
    }


def _build_audio_setting(args):
    """Build the audio_setting object from CLI options."""
    setting = {"format": args.audio_format}
    if args.sample_rate is not None:
        setting["sample_rate"] = args.sample_rate
    if args.bitrate is not None:
        setting["bitrate"] = args.bitrate
    if args.channel is not None:
        setting["channel"] = args.channel
    return setting


def _build_pronunciation_dict(args):
    """Parse the optional pronunciation_dict JSON option."""
    if args.pronunciation_dict is None:
        return None
    try:
        return json.loads(args.pronunciation_dict)
    except json.JSONDecodeError as exc:
        raise ValueError(f"--pronunciation-dict must be valid JSON: {exc}") from exc


def _build_voice_modify(args):
    """Parse the optional voice_modify JSON option."""
    if args.voice_modify is None:
        return None
    try:
        return json.loads(args.voice_modify)
    except json.JSONDecodeError as exc:
        raise ValueError(f"--voice-modify must be valid JSON: {exc}") from exc


def build_payload(args, async_=False):
    """Build the synthesis request body for the HTTP or async endpoint."""
    payload = {
        "model": args.model,
        "text": args.text,
        "voice_setting": _build_voice_setting(args),
        "audio_setting": _build_audio_setting(args),
        "language_boost": args.language_boost,
    }
    pronunciation = _build_pronunciation_dict(args)
    if pronunciation is not None:
        payload["pronunciation_dict"] = pronunciation
    voice_modify = _build_voice_modify(args)
    if voice_modify is not None:
        payload["voice_modify"] = voice_modify

    if async_:
        return payload

    if args.output_format is not None:
        payload["output_format"] = args.output_format
    if args.stream:
        payload["stream"] = True
    if args.subtitle_enable:
        payload["subtitle_enable"] = True
    return payload


def _decode_audio(encoded):
    """Decode hex (or base64) encoded audio data into raw bytes."""
    value = encoded.strip() if isinstance(encoded, str) else encoded
    if not value:
        return b""
    if isinstance(value, str):
        try:
            if len(value) % 2 == 0 and all(c in "0123456789abcdefABCDEF" for c in value):
                return bytes.fromhex(value)
        except ValueError:
            pass
        try:
            return base64.b64decode(value, validate=True)
        except Exception:
            pass
        return value.encode("utf-8")
    return value


def _parse_tts_body(body):
    """Extract audio chunks from a T2A HTTP response body.

    Handles both a single JSON document and a streamed, newline-delimited
    JSON body (optionally wrapped as SSE "data:" lines).
    """
    chunks = []
    try:
        parsed = json.loads(body)
        _check_base_resp(parsed)
        audio = (parsed.get("data") or {}).get("audio")
        if audio:
            chunks.append(audio)
    except json.JSONDecodeError:
        pass
    if chunks:
        return chunks
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("data:"):
            line = line[len("data:"):].strip()
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        _check_base_resp(parsed)
        audio = (parsed.get("data") or {}).get("audio")
        if audio:
            chunks.append(audio)
    return chunks


def _output_extension(args):
    """Pick the local file extension from the audio codec or output format."""
    if args.audio_format in AUDIO_FORMATS:
        return args.audio_format
    if args.output_format in AUDIO_FORMATS:
        return args.output_format
    return "mp3"


def _output_path(args, extension, name):
    """Resolve the output path for a synthesized audio file."""
    out = args.output
    if os.path.isdir(out):
        return os.path.join(out, f"{name}.{extension}")
    if os.path.splitext(out)[1]:
        return out
    return f"{out}.{extension}"


def _write_audio(audio_bytes, output_path):
    """Write audio bytes to disk, creating parent directories as needed."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "wb") as out:
        out.write(audio_bytes)
    print(f"Saved audio to {output_path}")


def run_http(args):
    """Synchronous text-to-speech over HTTP (POST /v1/t2a_v2)."""
    api_key = get_api_key(args.api_key)
    payload = build_payload(args)
    url = f"{base_url(args.region)}/t2a_v2"
    body = _request(url, api_key, method="POST", payload=payload, raw=True)
    chunks = _parse_tts_body(body)
    if not chunks:
        raise RuntimeError("No audio data in response")
    audio_bytes = b"".join(_decode_audio(chunk) for chunk in chunks)
    output_path = _output_path(args, _output_extension(args), "speech")
    _write_audio(audio_bytes, output_path)
    return True


def create_async_task(args, api_key):
    """Create an asynchronous synthesis task (POST /v1/t2a_async_v2)."""
    payload = build_payload(args, async_=True)
    url = f"{base_url(args.region)}/t2a_async_v2"
    response = _request(url, api_key, method="POST", payload=payload)
    task_id = response.get("task_id")
    if not task_id:
        raise RuntimeError(f"No task_id in response: {response}")
    return task_id


def query_task(task_id, region, api_key):
    """Query an async synthesis task.

    The query endpoint accepts task_id either as a GET query parameter or as a
    POST JSON body; try both and keep whichever the endpoint accepts.
    """
    base = base_url(region)
    path = "/query/t2a_async_query_v2"
    query_url = f"{base}{path}?{urllib.parse.urlencode({'task_id': task_id})}"
    try:
        return _request(query_url, api_key, method="GET")
    except RuntimeError as first_error:
        try:
            return _request(f"{base}{path}", api_key, method="POST", payload={"task_id": task_id})
        except RuntimeError:
            raise first_error


def retrieve_file(file_id, region, api_key):
    """Resolve a finished file id to its download URL."""
    url = f"{base_url(region)}/files/retrieve?{urllib.parse.urlencode({'file_id': file_id})}"
    response = _request(url, api_key, method="GET")
    file_info = response.get("file") or {}
    download_url = file_info.get("download_url")
    if not download_url:
        raise RuntimeError(f"No download_url in response: {response}")
    return download_url


def download(download_url, output_path):
    """Download the generated audio file to output_path."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with urllib.request.urlopen(download_url) as resp, open(output_path, "wb") as out:
        out.write(resp.read())
    print(f"Saved audio to {output_path}")


def wait_for_completion(task_id, region, api_key, poll_interval, timeout):
    """Poll an async task until it succeeds, fails, or times out."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        response = query_task(task_id, region, api_key)
        status = (response.get("status") or "").lower()
        print(f"Status: {status or 'unknown'}")
        if status in SUCCESS_STATES:
            return response
        if status in FAILURE_STATES:
            raise RuntimeError(f"Synthesis failed for task {task_id}: {status}")
        time.sleep(poll_interval)
    raise TimeoutError(f"Task {task_id} did not finish within {timeout} seconds")


def run_async(args):
    """Asynchronous text-to-speech: create, poll, then download the result."""
    api_key = get_api_key(args.api_key)
    task_id = create_async_task(args, api_key)
    print(f"Task created: {task_id}")
    if args.no_wait:
        print(f"Task {task_id} submitted. Query it later with the 'query' command.")
        return True
    task = wait_for_completion(task_id, args.region, api_key, args.poll_interval, args.timeout)
    file_id = task.get("file_id")
    if not file_id:
        raise RuntimeError(f"No file_id for completed task {task_id}")
    download_url = retrieve_file(file_id, args.region, api_key)
    output_path = _output_path(args, _output_extension(args), str(task_id))
    download(download_url, output_path)
    return True


def run_query(args):
    """Query the status of an existing async task."""
    api_key = get_api_key(args.api_key)
    print(json.dumps(query_task(args.task_id, args.region, api_key)))
    return True


def _ws_connect(ws_url, api_key):
    """Open a WebSocket connection with a Bearer authorization header."""
    parsed = urllib.parse.urlparse(ws_url)
    if parsed.scheme not in ("ws", "wss"):
        raise ValueError(f"Unsupported WebSocket scheme: {parsed.scheme}")
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "wss" else 80)
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"

    sock = socket.create_connection((host, port), timeout=30)
    if parsed.scheme == "wss":
        context = ssl.create_default_context()
        sock = context.wrap_socket(sock, server_hostname=host)

    key = base64.b64encode(os.urandom(16)).decode("ascii")
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        f"Authorization: Bearer {api_key}\r\n"
        "\r\n"
    )
    sock.sendall(request.encode("utf-8"))

    response = b""
    while b"\r\n\r\n" not in response:
        chunk = sock.recv(4096)
        if not chunk:
            raise RuntimeError("WebSocket handshake failed: connection closed")
        response += chunk
    header_bytes, _, _ = response.partition(b"\r\n\r\n")
    headers = header_bytes.decode("iso-8859-1").split("\r\n")
    status_line = headers[0]
    if "101" not in status_line:
        raise RuntimeError(f"WebSocket handshake failed: {status_line}")

    accept = None
    for line in headers[1:]:
        if line.lower().startswith("sec-websocket-accept:"):
            accept = line.split(":", 1)[1].strip()
    expected = base64.b64encode(
        hashlib.sha1((key + _WS_GUID).encode("ascii")).digest()
    ).decode("ascii")
    if accept != expected:
        raise RuntimeError("WebSocket handshake failed: invalid Sec-WebSocket-Accept")
    return sock


def _recv_exact(sock, size):
    """Read exactly size bytes from the socket."""
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise RuntimeError("WebSocket connection closed")
        data += chunk
    return data


def _ws_send_frame(sock, opcode, payload, fin=True):
    """Send one WebSocket frame. Client frames are masked per RFC 6455."""
    mask = os.urandom(4)
    header = bytearray([(0x80 if fin else 0x00) | opcode])
    length = len(payload)
    if length < 126:
        header.append(0x80 | length)
    elif length < 65536:
        header.append(0x80 | 126)
        header += struct.pack(">H", length)
    else:
        header.append(0x80 | 127)
        header += struct.pack(">Q", length)
    header += mask
    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    sock.sendall(bytes(header) + masked)


def _ws_send_text(sock, message):
    """Send a text frame containing the given message."""
    _ws_send_frame(sock, 0x1, message.encode("utf-8"))


def _ws_recv_frame(sock):
    """Read and unmask one WebSocket frame from the server."""
    b0, b1 = _recv_exact(sock, 2)
    fin = b0 & 0x80
    opcode = b0 & 0x0F
    masked = b1 & 0x80
    length = b1 & 0x7F
    if length == 126:
        length = struct.unpack(">H", _recv_exact(sock, 2))[0]
    elif length == 127:
        length = struct.unpack(">Q", _recv_exact(sock, 8))[0]
    mask_key = None
    if masked:
        mask_key = _recv_exact(sock, 4)
    payload = _recv_exact(sock, length)
    if mask_key:
        payload = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))
    return fin, opcode, payload


def _ws_recv_message(sock):
    """Read one complete WebSocket message, handling fragmentation."""
    fragments = []
    while True:
        fin, opcode, payload = _ws_recv_frame(sock)
        if opcode == 0x9:  # ping
            _ws_send_frame(sock, 0xA, payload)
            continue
        if opcode == 0x8:  # close
            return None
        if opcode in (0x0, 0x1, 0x2):
            fragments.append(payload)
            if fin:
                return b"".join(fragments).decode("utf-8", "replace")
        # Ignore other control frames.


def _ws_recv_event(sock):
    """Receive one WebSocket message and parse it as JSON."""
    message = _ws_recv_message(sock)
    if message is None:
        raise RuntimeError("WebSocket closed before synthesis finished")
    try:
        return json.loads(message)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON from WebSocket: {message[:200]}") from exc


def _ws_wait_for_event(sock, expected_event):
    """Read events until the expected event arrives."""
    while True:
        event = _ws_recv_event(sock)
        if event.get("event") == expected_event:
            return event
        if event.get("event") == "task_failed":
            raise RuntimeError(f"WebSocket synthesis failed: {event.get('base_resp')}")


def _ws_build_start(args):
    """Build the task_start event for the WebSocket session."""
    start = {
        "event": "task_start",
        "model": args.model,
        "language_boost": args.language_boost,
        "voice_setting": _build_voice_setting(args),
        "audio_setting": _build_audio_setting(args),
    }
    pronunciation = _build_pronunciation_dict(args)
    if pronunciation is not None:
        start["pronunciation_dict"] = pronunciation
    return start


def _ws_split_text(text, max_chars=500):
    """Split long text into task_continue chunks."""
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)] or [""]


def run_ws(args):
    """Realtime text-to-speech over WebSocket (WSS /ws/v1/t2a_v2)."""
    api_key = get_api_key(args.api_key)
    sock = _ws_connect(WS_REGIONS[args.region], api_key)
    try:
        _ws_wait_for_event(sock, "connected_success")
        _ws_send_text(sock, json.dumps(_ws_build_start(args)))
        _ws_wait_for_event(sock, "task_started")
        for chunk in _ws_split_text(args.text):
            _ws_send_text(sock, json.dumps({"event": "task_continue", "text": chunk}))
        _ws_send_text(sock, json.dumps({"event": "task_finish"}))

        chunks = []
        while True:
            event = _ws_recv_event(sock)
            event_name = event.get("event")
            if event_name == "task_continued":
                audio = (event.get("data") or {}).get("audio")
                if audio:
                    chunks.append(audio)
                if event.get("is_final"):
                    break
            elif event_name == "task_finished":
                break
            elif event_name == "task_failed":
                raise RuntimeError(f"WebSocket synthesis failed: {event.get('base_resp')}")

        audio_bytes = b"".join(_decode_audio(chunk) for chunk in chunks)
        output_path = _output_path(args, _output_extension(args), "speech")
        _write_audio(audio_bytes, output_path)
        return True
    finally:
        try:
            sock.close()
        except OSError:
            pass


def add_common_options(parser):
    """Options shared by every subcommand."""
    parser.add_argument(
        "--region",
        default="global",
        choices=sorted(REGIONS),
        help="API region (default: global)",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key (defaults to the MINIMAX_API_KEY environment variable)",
    )


def add_tts_options(parser):
    """Options shared by the synthesis subcommands."""
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        choices=MODELS,
        help=f"Speech model (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--voice-id",
        default=DEFAULT_VOICE,
        help="Voice id to synthesize with (default: {})".format(DEFAULT_VOICE),
    )
    parser.add_argument("--speed", type=float, default=1.0, help="Speech speed (default: 1.0)")
    parser.add_argument("--vol", type=float, default=1.0, help="Volume (default: 1.0)")
    parser.add_argument("--pitch", type=float, default=0.0, help="Pitch shift (default: 0)")
    parser.add_argument(
        "--language-boost",
        default="auto",
        help="Language boost, e.g. auto, Chinese or English (default: auto)",
    )
    parser.add_argument(
        "--audio-format",
        choices=AUDIO_FORMATS,
        default="mp3",
        help="Audio codec (default: mp3)",
    )
    parser.add_argument("--sample-rate", type=int, help="Audio sample rate, e.g. 32000")
    parser.add_argument("--bitrate", type=int, help="Audio bitrate, e.g. 128000")
    parser.add_argument("--channel", type=int, help="Audio channels: 1 or 2")
    parser.add_argument(
        "--pronunciation-dict",
        default=None,
        help="Pronunciation dictionary as JSON, e.g. '{\"tone\": [\"Omg/Oh my god\"]}'",
    )
    parser.add_argument(
        "--voice-modify",
        default=None,
        help="Voice modification as JSON, e.g. '{\"pitch\": 0, \"intensity\": 0, \"timbre\": 0}'",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="/mnt/user-data/outputs",
        help="Output file or directory (default: /mnt/user-data/outputs)",
    )


def build_parser():
    parser = argparse.ArgumentParser(
        description="Synthesize speech with the MiniMax text-to-speech API"
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    http = sub.add_parser("http", help="Synchronous text-to-speech over HTTP")
    http.add_argument("text", help="Text to synthesize")
    http.add_argument(
        "--output-format",
        choices=OUTPUT_FORMATS,
        default="hex",
        help="Audio output format (default: hex)",
    )
    http.add_argument("--stream", action="store_true", help="Stream the audio response")
    http.add_argument(
        "--subtitle-enable",
        action="store_true",
        help="Request subtitle data in the response",
    )
    add_tts_options(http)
    add_common_options(http)
    http.set_defaults(func=run_http)

    async_cmd = sub.add_parser("async", help="Asynchronous text-to-speech task")
    async_cmd.add_argument("text", help="Text to synthesize")
    async_cmd.add_argument(
        "--poll-interval",
        type=int,
        default=5,
        help="Seconds between status checks (default: 5)",
    )
    async_cmd.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Maximum seconds to wait for completion (default: 600)",
    )
    async_cmd.add_argument(
        "--no-wait",
        action="store_true",
        help="Create the task and exit without polling or downloading",
    )
    add_tts_options(async_cmd)
    add_common_options(async_cmd)
    async_cmd.set_defaults(func=run_async)

    query = sub.add_parser("query", help="Query the status of an async task")
    query.add_argument("task_id", help="Task id returned when the task was created")
    add_common_options(query)
    query.set_defaults(func=run_query)

    ws = sub.add_parser("ws", help="Realtime text-to-speech over WebSocket")
    ws.add_argument("text", help="Text to synthesize")
    add_tts_options(ws)
    add_common_options(ws)
    ws.set_defaults(func=run_ws)

    return parser


def main():
    args = build_parser().parse_args()
    try:
        ok = args.func(args)
    except (RuntimeError, ValueError, TimeoutError) as exc:
        print(f"Error: {exc}")
        sys.exit(1)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
