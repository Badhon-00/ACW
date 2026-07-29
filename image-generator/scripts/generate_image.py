#!/usr/bin/env python3
"""
Build a Pollinations AI image URL from an (already enhanced) prompt, and try to
download the resulting image to disk so it can be saved/presented as a file —
not just embedded as a remote link.

Usage:
    python3 generate_image.py "enhanced prompt text" \
        [--width 1024] [--height 1024] [--seed 42] [--out /path/to/file.png]

Behavior:
    - width/height default to 1024x1024 if not given (caller should pass sizes
      that match the requested aspect ratio/use-case instead of always relying
      on the default — see SKILL.md's sizing guide).
    - seed defaults to a random value each run, so repeat prompts don't return
      an identical image unless the caller explicitly passes --seed to make a
      result reproducible.
    - Tries to download the image bytes to --out (default: a slugified name in
      the current directory). If the download fails (e.g. no network access to
      image.pollinations.ai in this environment), prints the URL anyway so the
      caller can fall back to a Markdown image embed.

Prints one line starting with "URL:" and, if the download succeeded, a second
line starting with "FILE:" with the saved path. Always check for the FILE line
before assuming a local file exists.
"""
import argparse
import random
import re
import sys
import urllib.parse
import urllib.request


def slugify(prompt: str, max_len: int = 50) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", prompt.strip().lower()).strip("-")
    return (slug[:max_len] or "image")


def build_url(prompt: str, width: int, height: int, seed: int) -> str:
    encoded = urllib.parse.quote(prompt)
    return (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={width}&height={height}&nologo=true&seed={seed}"
    )


def main():
    parser = argparse.ArgumentParser(description="Build and optionally download a Pollinations AI image.")
    parser.add_argument("prompt", help="The enhanced image-generation prompt text.")
    parser.add_argument("--width", type=int, default=1024, help="Image width in pixels (default 1024).")
    parser.add_argument("--height", type=int, default=1024, help="Image height in pixels (default 1024).")
    parser.add_argument("--seed", type=int, default=None, help="Seed for reproducibility. Omit for a random result.")
    parser.add_argument("--out", default=None, help="Path to save the downloaded image (default: ./<slug>.png).")
    parser.add_argument("--no-download", action="store_true", help="Only print the URL, don't attempt a download.")
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else random.randint(0, 2**31 - 1)
    url = build_url(args.prompt, args.width, args.height, seed)
    print(f"URL: {url}")

    if args.no_download:
        return

    out_path = args.out or f"{slugify(args.prompt)}.png"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp, open(out_path, "wb") as f:
            f.write(resp.read())
        print(f"FILE: {out_path}")
    except Exception as e:
        print(f"DOWNLOAD_FAILED: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
