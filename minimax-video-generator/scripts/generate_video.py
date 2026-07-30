#!/usr/bin/env python3
"""
MiniMax Video Generator

Generate videos with the MiniMax video generation API. Supports both
text-to-video and image-to-video, polls the asynchronous task until it
finishes, retrieves the resulting file, and downloads it locally.

Only the Python standard library is used, so no extra dependencies are
required.

Set your API key in the MINIMAX_API_KEY environment variable (or pass
--api-key). The key is sent as a Bearer token.
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# Regional API hosts. "global" serves international traffic, "cn" serves
# mainland China. Both expose the same paths under /v1.
REGIONS = {
    "global": "https://api.minimax.io/v1",
    "cn": "https://api.minimaxi.com/v1",
}

# Available video models. MiniMax-Hailuo-2.3 is the default.
MODELS = [
    "MiniMax-Hailuo-2.3",
    "MiniMax-Hailuo-2.3-Fast",
    "MiniMax-Hailuo-02",
    "T2V-01-Director",
    "T2V-01",
    "I2V-01-Director",
    "I2V-01-live",
    "I2V-01",
]
DEFAULT_MODEL = "MiniMax-Hailuo-2.3"

# Terminal states reported by the query endpoint.
SUCCESS_STATES = {"Success"}
FAILURE_STATES = {"Fail"}


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


def _request(url, api_key, method="GET", payload=None):
    """Perform an HTTP request and return the decoded JSON response."""
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

    parsed = json.loads(body)
    _check_base_resp(parsed)
    return parsed


def _check_base_resp(parsed):
    """Raise if the API signalled an error via base_resp.status_code."""
    base_resp = parsed.get("base_resp") or {}
    status_code = base_resp.get("status_code")
    if status_code not in (None, 0):
        message = base_resp.get("status_msg", "unknown error")
        raise RuntimeError(f"API error {status_code}: {message}")


def _encode_image(image):
    """Return a data URI for a local file, or pass a URL/data URI through."""
    if image.startswith(("http://", "https://", "data:")):
        return image
    if not os.path.isfile(image):
        raise ValueError(f"first-frame image not found: {image}")
    mime, _ = mimetypes.guess_type(image)
    mime = mime or "image/jpeg"
    with open(image, "rb") as handle:
        encoded = base64.b64encode(handle.read()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _add_optional_fields(payload, args):
    """Attach the optional generation fields shared by both modes."""
    if args.prompt_optimizer is not None:
        payload["prompt_optimizer"] = args.prompt_optimizer
    if args.fast_pretreatment is not None:
        payload["fast_pretreatment"] = args.fast_pretreatment
    if args.duration is not None:
        payload["duration"] = args.duration
    if args.resolution is not None:
        payload["resolution"] = args.resolution
    if args.callback_url is not None:
        payload["callback_url"] = args.callback_url


def create_task(args, api_key):
    """Submit a text-to-video or image-to-video task and return its task_id."""
    url = f"{base_url(args.region)}/video_generation"
    payload = {"model": args.model}

    if args.mode == "image-to-video":
        payload["first_frame_image"] = _encode_image(args.first_frame_image)
        if args.prompt:
            payload["prompt"] = args.prompt
    else:
        payload["prompt"] = args.prompt

    _add_optional_fields(payload, args)

    print(f"Submitting {args.mode} task with model {args.model} ({args.region})...")
    response = _request(url, api_key, method="POST", payload=payload)
    task_id = response.get("task_id")
    if not task_id:
        raise RuntimeError(f"No task_id in response: {response}")
    print(f"Task created: {task_id}")
    return task_id


def query_task(task_id, region, api_key):
    """Query a generation task, returning (status, file_id)."""
    query = urllib.parse.urlencode({"task_id": task_id})
    url = f"{base_url(region)}/query/video_generation?{query}"
    response = _request(url, api_key, method="GET")
    return response.get("status", ""), response.get("file_id", "")


def retrieve_file(file_id, region, api_key):
    """Retrieve a generated file and return its download URL."""
    query = urllib.parse.urlencode({"file_id": file_id})
    url = f"{base_url(region)}/files/retrieve?{query}"
    response = _request(url, api_key, method="GET")
    file_info = response.get("file") or {}
    download_url = file_info.get("download_url")
    if not download_url:
        raise RuntimeError(f"No download_url in response: {response}")
    return download_url


def download(download_url, output_path):
    """Download the generated video to output_path."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with urllib.request.urlopen(download_url) as resp, open(output_path, "wb") as out:
        out.write(resp.read())
    print(f"Saved video to {output_path}")


def wait_for_completion(task_id, region, api_key, poll_interval, timeout):
    """Poll the query endpoint until the task succeeds, fails, or times out."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        status, file_id = query_task(task_id, region, api_key)
        print(f"Status: {status or 'unknown'}")
        if status in SUCCESS_STATES and file_id:
            return file_id
        if status in FAILURE_STATES:
            raise RuntimeError(f"Generation failed for task {task_id}")
        time.sleep(poll_interval)
    raise TimeoutError(f"Task {task_id} did not finish within {timeout} seconds")


def run_generation(args):
    """Run the full pipeline: create, poll, retrieve, and download."""
    api_key = get_api_key(args.api_key)
    task_id = create_task(args, api_key)

    if args.no_wait:
        print(f"Task {task_id} submitted. Query it later with the 'query' command.")
        return True

    file_id = wait_for_completion(
        task_id, args.region, api_key, args.poll_interval, args.timeout
    )
    download_url = retrieve_file(file_id, args.region, api_key)
    output_path = args.output
    if os.path.isdir(output_path):
        output_path = os.path.join(output_path, f"{task_id}.mp4")
    download(download_url, output_path)
    return True


def run_query(args):
    """Query the status of an existing task."""
    api_key = get_api_key(args.api_key)
    status, file_id = query_task(args.task_id, args.region, api_key)
    print(json.dumps({"task_id": args.task_id, "status": status, "file_id": file_id}))
    return True


def run_retrieve(args):
    """Retrieve and download a finished file by file_id."""
    api_key = get_api_key(args.api_key)
    download_url = retrieve_file(args.file_id, args.region, api_key)
    output_path = args.output
    if os.path.isdir(output_path):
        output_path = os.path.join(output_path, f"{args.file_id}.mp4")
    download(download_url, output_path)
    return True


def add_common_options(parser):
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


def add_generation_options(parser):
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        choices=MODELS,
        help=f"Video model (default: {DEFAULT_MODEL})",
    )
    parser.add_argument("--duration", type=int, help="Clip duration in seconds")
    parser.add_argument("--resolution", help="Output resolution, e.g. 768P or 1080P")
    parser.add_argument(
        "--prompt-optimizer",
        dest="prompt_optimizer",
        action="store_true",
        default=None,
        help="Let the API refine the prompt before generating",
    )
    parser.add_argument(
        "--fast-pretreatment",
        dest="fast_pretreatment",
        action="store_true",
        default=None,
        help="Enable faster input pre-processing",
    )
    parser.add_argument(
        "--callback-url",
        dest="callback_url",
        default=None,
        help="URL to receive asynchronous status callbacks",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="/mnt/user-data/outputs",
        help="Output file or directory (default: /mnt/user-data/outputs)",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=10,
        help="Seconds between status checks (default: 10)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Maximum seconds to wait for completion (default: 600)",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Submit the task and exit without polling or downloading",
    )


def build_parser():
    parser = argparse.ArgumentParser(
        description="Generate videos with the MiniMax video generation API"
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    t2v = sub.add_parser("text-to-video", help="Generate a video from a text prompt")
    t2v.add_argument("prompt", help="Text description of the video")
    add_generation_options(t2v)
    add_common_options(t2v)
    t2v.set_defaults(func=run_generation)

    i2v = sub.add_parser(
        "image-to-video", help="Generate a video from a first-frame image"
    )
    i2v.add_argument(
        "first_frame_image",
        help="First frame: local image path, URL, or data URI",
    )
    i2v.add_argument("--prompt", default="", help="Optional text guidance")
    add_generation_options(i2v)
    add_common_options(i2v)
    i2v.set_defaults(func=run_generation)

    query = sub.add_parser("query", help="Check the status of a task")
    query.add_argument("task_id", help="Task id returned when the task was created")
    add_common_options(query)
    query.set_defaults(func=run_query)

    retrieve = sub.add_parser("retrieve", help="Download a finished file by file id")
    retrieve.add_argument("file_id", help="File id reported by a successful task")
    retrieve.add_argument(
        "-o",
        "--output",
        default="/mnt/user-data/outputs",
        help="Output file or directory (default: /mnt/user-data/outputs)",
    )
    add_common_options(retrieve)
    retrieve.set_defaults(func=run_retrieve)

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
