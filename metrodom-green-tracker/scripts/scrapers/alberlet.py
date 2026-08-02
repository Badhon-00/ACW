"""Scraper for alberlet.hu search results.

alberlet.hu renders results as plain server-side HTML (no client-side
JSON blob to lean on), so this is a straightforward card scrape. If the
site redesigns its markup, update the CSS selectors below — run with
--dry-run to see what got parsed.
"""

import re
from typing import List

import requests
from bs4 import BeautifulSoup

from models import Listing

SEARCH_URL = "https://www.alberlet.hu/kiado-lakas/budapest-ix-kerulet"
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
        print(f"[alberlet.hu] request failed: {exc}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    listings = []

    cards = soup.select(".list-item, .listing, .search-result-item, .property-item")
    if not cards:
        # Fallback: any anchor whose href looks like a listing detail page.
        cards = [a.parent for a in soup.find_all("a", href=re.compile(r"/(hirdetes|kiado-lakas)/"))]

    for card in cards:
        link_tag = card.find("a", href=True) if hasattr(card, "find") else None
        if not link_tag:
            continue
        href = link_tag["href"]
        url = href if href.startswith("http") else f"https://www.alberlet.hu{href}"
        listing_id = re.sub(r"\D", "", href) or href
        text = card.get_text(" ", strip=True)

        size_match = re.search(r"(\d+)\s*(?:m2|m²|nm)", text, re.IGNORECASE)
        rooms_match = re.search(r"(\d+(?:[.,]\d)?)\s*szoba", text, re.IGNORECASE)

        listings.append(Listing(
            source="alberlet.hu",
            listing_id=listing_id,
            url=url,
            title=link_tag.get_text(strip=True) or text[:80],
            size_sqm=_to_float(size_match.group(1)) if size_match else None,
            rooms=_to_float(rooms_match.group(1)) if rooms_match else None,
            address_text=text,
            description_text=text,
        ))
    return listings


def _to_float(value):
    if value is None:
        return None
    try:
        return float(str(value).replace(",", "."))
    except ValueError:
        return None
