"""Shared data model for listings across all sources."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Listing:
    source: str            # "ingatlan.com" | "alberlet.hu" | "facebook"
    listing_id: str         # stable id/url used for dedup
    url: str
    title: str
    price_text: str = ""
    size_sqm: Optional[float] = None
    rooms: Optional[float] = None
    address_text: str = ""
    description_text: str = ""
    posted_at: Optional[str] = None  # ISO string if known

    # Filled in by filters.py — None means "could not be determined from
    # the listing text", not "fails the filter".
    furnished_status: Optional[str] = None   # "full" | "partial" | None
    has_outdoor_space: Optional[bool] = None
    move_in_ok: Optional[bool] = None

    notes: list = field(default_factory=list)

    def dedup_key(self) -> str:
        return f"{self.source}:{self.listing_id}"
