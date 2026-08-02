"""Filtering logic shared by all scrapers.

Hard filters (size, rooms, location keyword) drop a listing outright when
the data says it fails. Soft filters (furnished, outdoor space, move-in
date) only drop a listing when the listing text *confirms* it fails; when
the relevant detail simply isn't stated in the search-result text, the
listing is kept and flagged "unconfirmed" so a human can check it rather
than being silently dropped by an imperfect parse.
"""

import re
from datetime import datetime
from typing import Optional

import config
from models import Listing


def text_matches_any(text: str, keywords) -> bool:
    text = (text or "").lower()
    return any(kw in text for kw in keywords)


def location_matches(listing: Listing) -> bool:
    haystack = f"{listing.title} {listing.address_text} {listing.description_text}"
    return text_matches_any(haystack, config.ADDRESS_KEYWORDS) or (
        text_matches_any(haystack, config.LOCATION_HINTS)
        and text_matches_any(haystack, ["vágóhíd", "vagohid", "metrodom"])
    )


def size_ok(listing: Listing) -> bool:
    return listing.size_sqm is not None and listing.size_sqm >= config.MIN_SIZE_SQM


def rooms_ok(listing: Listing) -> bool:
    return listing.rooms is not None and listing.rooms >= config.MIN_ROOMS


def detect_furnished(text: str) -> Optional[str]:
    text = (text or "").lower()
    if text_matches_any(text, config.PARTIALLY_FURNISHED_KEYWORDS):
        return "partial"
    if text_matches_any(text, config.FURNISHED_KEYWORDS):
        return "full"
    return None


def detect_outdoor_space(text: str) -> Optional[bool]:
    text = (text or "").lower()
    if text_matches_any(text, config.OUTDOOR_SPACE_KEYWORDS):
        return True
    return None  # not mentioned != confirmed absent


_MOVE_IN_DATE_RE = re.compile(
    r"(\d{4})\.?\s*(" + "|".join(config.HUNGARIAN_MONTHS.keys()) + r")",
    re.IGNORECASE,
)


def detect_move_in_ok(text: str) -> Optional[bool]:
    text = (text or "").lower()
    if text_matches_any(text, config.IMMEDIATE_MOVE_IN_KEYWORDS) or "költözhető" in text or "koltozheto" in text:
        return True
    match = _MOVE_IN_DATE_RE.search(text)
    if match:
        year = int(match.group(1))
        month = config.HUNGARIAN_MONTHS[match.group(2).lower()]
        target = (config.EARLIEST_MOVE_IN_YEAR, config.EARLIEST_MOVE_IN_MONTH)
        return (year, month) >= target
    return None  # not stated, needs a manual check


def annotate(listing: Listing) -> Listing:
    combined_text = f"{listing.description_text} {listing.title}"
    listing.furnished_status = detect_furnished(combined_text)
    listing.has_outdoor_space = detect_outdoor_space(combined_text)
    listing.move_in_ok = detect_move_in_ok(combined_text)
    return listing


def passes_hard_filters(listing: Listing) -> bool:
    return location_matches(listing) and size_ok(listing) and rooms_ok(listing)


def passes_soft_filters(listing: Listing) -> bool:
    """Only excludes when a soft criterion is explicitly contradicted."""
    if listing.furnished_status is None:
        listing.notes.append("furnished status not stated — verify manually")
    if listing.has_outdoor_space is None:
        listing.notes.append("terrace/balcony not stated — verify manually")
    elif listing.has_outdoor_space is False:
        return False
    if listing.move_in_ok is None:
        listing.notes.append("move-in date not stated — verify manually")
    elif listing.move_in_ok is False:
        return False
    return True


def is_fresh(listing: Listing, now: Optional[datetime] = None) -> bool:
    if not listing.posted_at:
        return True  # can't tell, let the dedup state file be the gate
    now = now or datetime.utcnow()
    try:
        posted = datetime.fromisoformat(listing.posted_at)
    except ValueError:
        return True
    age_minutes = (now - posted).total_seconds() / 60
    return age_minutes <= config.FRESHNESS_WINDOW_MINUTES


def apply_all(listings):
    matches = []
    for listing in listings:
        annotate(listing)
        if passes_hard_filters(listing) and passes_soft_filters(listing):
            matches.append(listing)
    return matches
