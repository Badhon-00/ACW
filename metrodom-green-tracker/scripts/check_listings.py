#!/usr/bin/env python3
"""Main entry point: fetch, filter, dedup, and email new rental matches.

Usage:
    python check_listings.py            # normal run: emails new matches
    python check_listings.py --dry-run  # print what would be sent, no email, no state write
"""

import argparse
import sys

import filters
from emailer import send_email
from scrapers import ingatlan, alberlet, facebook
from state import load_seen, save_seen


def gather_all_listings():
    listings = []
    for scraper in (ingatlan, alberlet, facebook):
        try:
            found = scraper.fetch()
            print(f"[{scraper.__name__}] fetched {len(found)} listing(s)")
            listings.extend(found)
        except Exception as exc:  # keep one source's failure from killing the run
            print(f"[{scraper.__name__}] unexpected error: {exc}")
    return listings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Don't send email or update dedup state")
    args = parser.parse_args()

    all_listings = gather_all_listings()
    matches = filters.apply_all(all_listings)
    print(f"{len(matches)} listing(s) pass the Metrodom Green filters")

    seen = load_seen()
    new_matches = [m for m in matches if m.dedup_key() not in seen]
    print(f"{len(new_matches)} of those are new since the last run")

    if not new_matches:
        print("Nothing new — no email sent.")
        return 0

    for m in new_matches:
        print(f"NEW MATCH: [{m.source}] {m.title} -> {m.url}")

    if args.dry_run:
        print("--dry-run set: not sending email or updating state.")
        return 0

    send_email(new_matches)

    seen.update(m.dedup_key() for m in new_matches)
    save_seen(seen)
    return 0


if __name__ == "__main__":
    sys.exit(main())
