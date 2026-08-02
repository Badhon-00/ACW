"""On-disk dedup state so the same listing isn't emailed twice.

Stored as a flat JSON file of previously-seen dedup keys, committed back
to the repo by the GitHub Actions workflow after each run. Kept as a
capped list (oldest entries dropped) so the file doesn't grow forever.
"""

import json
import os

STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "seen_listings.json")
MAX_ENTRIES = 2000


def load_seen() -> set:
    if not os.path.exists(STATE_PATH):
        return set()
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        try:
            return set(json.load(f))
        except json.JSONDecodeError:
            return set()


def save_seen(seen: set) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    trimmed = list(seen)[-MAX_ENTRIES:]
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, indent=2)
