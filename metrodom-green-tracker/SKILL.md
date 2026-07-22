---
name: metrodom-green-tracker
description: Monitor rental listing sites hourly for apartments matching a specific building/area and filter set, and email new matches. Use this when the user wants an automated, recurring watch for new rental ads (e.g. "let me know when a new apartment in my building gets listed") rather than a one-off search.
---

# Rental Listing Tracker (Metrodom Green example)

Watches Hungarian rental listing sites for new apartments matching a
location and a set of hard requirements, and emails you when a new match
appears. Built for tracking the Metrodom Green complex at 12-14 Vágóhíd
utca, Budapest 1097, but the filters in `scripts/config.py` are just data
— point them at any building, street, or district instead.

## What this does

1. **Fetches** current listings from `ingatlan.com` and `alberlet.hu`.
2. **Filters** for:
   - Address/building keyword match (default: Vágóhíd utca / Metrodom Green)
   - Minimum size and room count (default: 40 sqm, 2 rooms)
   - Furnished status, terrace/balcony, and move-in date, read from the
     listing text where stated (see "Soft filters" below)
3. **Deduplicates** against `data/seen_listings.json` so the same listing
   is never emailed twice.
4. **Emails** any new matches to the configured address.
5. Runs **hourly** via a GitHub Actions scheduled workflow
   (`.github/workflows/metrodom-green-tracker.yml`), not via any Claude
   session — see "Why GitHub Actions" below.

## What this deliberately does NOT do: Facebook/Marketplace scraping

Facebook's Terms of Service prohibit automated data collection from its
products, and Marketplace/Group content only renders for a logged-in
session. `scripts/scrapers/facebook.py` makes one unauthenticated,
no-login request and — as expected — will almost always come back empty,
because Facebook serves anonymous requests a login wall. It does not log
in, hold a session, or try to evade Facebook's bot detection.

**For Facebook coverage, use Facebook's own tools instead**: open
Marketplace, search "Vágóhíd utca" or "Metrodom Green", save the search,
and turn on notifications. Do the same for local Budapest rental
Facebook groups you're a member of. That's the reliable way to get
Facebook-sourced alerts, and it costs nothing to set up.

## Soft filters (furnished / terrace / move-in date)

Search-result pages rarely spell out every detail. When a listing's text
doesn't mention furnishing, a terrace, or a move-in date, the listing is
**kept** (not silently dropped) and flagged in the email as "verify
manually" for that field, rather than risking a false negative from an
imperfect text match. A listing IS dropped if the text explicitly says
"no terrace/balcony" equivalent, or states a move-in date earlier than
your configured earliest date.

## Setup

1. **Add repository secrets** (Settings → Secrets and variables → Actions):
   - `GMAIL_ADDRESS` — the Gmail address to send from
   - `GMAIL_APP_PASSWORD` — a Gmail [App Password](https://myaccount.google.com/apppasswords)
     (requires 2FA on that account; this is NOT your normal Gmail password)
2. **Merge this branch to your default branch.** GitHub only fires
   `schedule` (cron) triggers on the repository's default branch, so the
   hourly run won't start until this is merged.
3. Adjust `scripts/config.py` if your filters change (building, sqm,
   rooms, move-in date, recipient address).

## Manual usage

```bash
cd metrodom-green-tracker
pip install -r requirements.txt
python scripts/check_listings.py --dry-run   # preview matches, no email sent
python scripts/check_listings.py             # real run: emails new matches, updates dedup state
```

`GMAIL_ADDRESS` / `GMAIL_APP_PASSWORD` must be set as environment
variables for a real (non-dry-run) run to actually send email; without
them the script prints what it would have sent instead of failing.

## Adapting to a different building or area

Edit `scripts/config.py`:

- `ADDRESS_KEYWORDS` / `LOCATION_HINTS` — what text identifies a match
- `MIN_SIZE_SQM`, `MIN_ROOMS` — hard size/room filters
- `FURNISHED_KEYWORDS`, `OUTDOOR_SPACE_KEYWORDS` — soft-filter keywords
- `EARLIEST_MOVE_IN_YEAR` / `EARLIEST_MOVE_IN_MONTH` — move-in cutoff
- `EMAIL_TO` — recipient address

## Notes on reliability

`ingatlan.com` and `alberlet.hu` change their page markup over time.
`scripts/scrapers/ingatlan.py` parses the site's embedded JSON data first
(more stable across redesigns) and falls back to a CSS-selector scrape;
`scripts/scrapers/alberlet.py` uses CSS selectors directly. If a run
starts returning 0 listings from a source that normally has results, the
site's markup likely changed — run `--dry-run` and inspect the source's
current HTML to update the selectors.
