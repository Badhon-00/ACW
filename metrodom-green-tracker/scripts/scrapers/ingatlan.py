"""Scraper for ingatlan.com search results.

ingatlan.com embeds its search results as JSON inside a `<script
id="__NEXT_DATA__">` tag (it's a Next.js app), which is far more stable
to parse than CSS classes that change with every redesign. This module
tries that first and falls back to a best-effort HTML card parse if the
JSON shape has changed — in which case this file will need updating to
match the current markup (check the page source and adjust the
NEXT_DATA path or the CSS selectors in `_parse_html_fallback`).
"""

import json
import re
from typing import List

import requests
from bs4 import BeautifulSoup

from models import Listing

SEARCH_URL = "https://ingatlan.com/lista/kiado+lakas+budapest-ix-ker"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "hu-HU,hu;q=0.9,en;q=0.8",
}


def fetch(session: requests.Session = None) -> List[Listing]:
    session = session or requests.Session()
    try:
        resp = session.get(SEARCH_URL, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"[ingatlan.com] request failed: {exc}")
        return []

    listings = _parse_next_data(resp.text)
    if listings:
        return listings
    return _parse_html_fallback(resp.text)


def _parse_next_data(html: str) -> List[Listing]:
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("script", id="__NEXT_DATA__")
    if not tag or not tag.string:
        return []
    try:
        data = json.loads(tag.string)
    except json.JSONDecodeError:
        return []

    # The exact path to the listing array has moved around over the years;
    # search for the first list of dict-like items that look like listings.
    candidates = _find_listing_arrays(data)
    listings = []
    for item in candidates:
        listing = _listing_from_dict(item)
        if listing:
            listings.append(listing)
    return listings


def _find_listing_arrays(node, depth=0):
    """Depth-first search for arrays of dicts that look like listing records."""
    if depth > 8:
        return []
    if isinstance(node, list):
        if node and all(isinstance(x, dict) for x in node):
            if any(_looks_like_listing(x) for x in node):
                return node
        found = []
        for item in node:
            found.extend(_find_listing_arrays(item, depth + 1))
        return found
    if isinstance(node, dict):
        found = []
        for value in node.values():
            found.extend(_find_listing_arrays(value, depth + 1))
        return found
    return []


def _looks_like_listing(item: dict) -> bool:
    keys = {k.lower() for k in item.keys()}
    return bool({"price", "area", "id"} & keys) or bool({"listingId", "areaSize"} & set(item.keys()))


def _listing_from_dict(item: dict) -> Listing:
    try:
        listing_id = str(item.get("id") or item.get("listingId") or item.get("propertyId") or "")
        if not listing_id:
            return None
        slug = item.get("url") or item.get("slug") or ""
        url = slug if slug.startswith("http") else f"https://ingatlan.com{slug}" if slug else ""
        title = item.get("title") or item.get("address") or ""
        address_text = item.get("address") or item.get("location") or ""
        size_sqm = _to_float(item.get("area") or item.get("areaSize"))
        rooms = _to_float(item.get("roomCount") or item.get("rooms"))
        price_text = str(item.get("price") or item.get("priceLabel") or "")
        description_text = item.get("description") or item.get("shortDescription") or ""

        return Listing(
            source="ingatlan.com",
            listing_id=listing_id,
            url=url,
            title=title,
            price_text=price_text,
            size_sqm=size_sqm,
            rooms=rooms,
            address_text=address_text,
            description_text=description_text,
        )
    except (TypeError, ValueError):
        return None


def _to_float(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"[\d.,]+", str(value))
    if not match:
        return None
    return float(match.group(0).replace(",", "."))


def _parse_html_fallback(html: str) -> List[Listing]:
    """Best-effort card scrape used only if the NEXT_DATA JSON isn't found.

    NOTE: these selectors are a best guess and may need updating to match
    the site's current markup — run with --dry-run and inspect output if
    this returns nothing while _parse_next_data also returns nothing.
    """
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    for card in soup.select("[data-testid='listing-card'], .listing-card, article"):
        link_tag = card.find("a", href=True)
        if not link_tag:
            continue
        href = link_tag["href"]
        url = href if href.startswith("http") else f"https://ingatlan.com{href}"
        listing_id = re.sub(r"\D", "", href) or href
        text = card.get_text(" ", strip=True)
        size_match = re.search(r"(\d+)\s*m2|\d+\s*m²", text)
        rooms_match = re.search(r"(\d+(?:\.\d+)?)\s*szoba", text, re.IGNORECASE)
        listings.append(Listing(
            source="ingatlan.com",
            listing_id=listing_id,
            url=url,
            title=link_tag.get_text(strip=True) or text[:80],
            size_sqm=_to_float(size_match.group(0)) if size_match else None,
            rooms=_to_float(rooms_match.group(1)) if rooms_match else None,
            address_text=text,
            description_text=text,
        ))
    return listings
