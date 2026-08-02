"""Best-effort, unauthenticated check of Facebook Marketplace/Groups.

Facebook's Terms of Service prohibit automated data collection from its
products without permission, and Marketplace/Group content is only
rendered to a logged-in session. This module deliberately does NOT log
in, hold a session/cookie jar, spoof a browser fingerprint, or otherwise
try to get around Facebook's bot detection — it only issues a single
plain, unauthenticated GET to a public search URL.

In practice this will almost always return zero results, because
Facebook serves a login wall to anonymous requests. That's expected and
by design, not a bug. The reliable way to monitor Facebook for this
building is the native "save search" alert feature in Marketplace and in
the relevant local rental groups — turn on notifications for a saved
search there; this script won't do it for you.
"""

from typing import List

import requests

from models import Listing

SEARCH_URL = "https://www.facebook.com/marketplace/108314429191488/search/?query=V%C3%A1g%C3%B3h%C3%ADd%20utca"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
}


def fetch(session: requests.Session = None) -> List[Listing]:
    session = session or requests.Session()
    try:
        resp = session.get(SEARCH_URL, headers=HEADERS, timeout=15, allow_redirects=True)
    except requests.RequestException as exc:
        print(f"[facebook] request failed (expected without login): {exc}")
        return []

    if "login" in resp.url or resp.status_code in (302, 400, 403, 429):
        print(
            "[facebook] no data available without an authenticated session "
            "(this is expected — see module docstring). Use Marketplace's "
            "native saved-search alerts instead."
        )
        return []

    # We deliberately don't attempt to parse Facebook's markup even if a
    # response came back, since any real result here is unauthenticated
    # public content only (e.g. a fully public group post rendered
    # server-side), which is rare enough not to be worth building a parser
    # around.
    return []
