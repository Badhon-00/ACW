"""Search configuration for the rental listing tracker.

Edit this file to point the tracker at a different building, area, or
filter set. Defaults below are tuned for the Metrodom Green complex.
"""

# Text that must appear (case-insensitive) in a listing's address/title/
# description for it to be considered a match. A listing matches if ANY
# of these strings is found.
ADDRESS_KEYWORDS = [
    "vágóhíd",
    "vagohid",
    "metrodom green",
    "metrodom",
]

# Budapest postal code / district hints used as a secondary signal when a
# listing doesn't spell out the street name.
LOCATION_HINTS = ["1097", "ix. ker", "ix.ker", "budapest ix"]

MIN_SIZE_SQM = 40
MIN_ROOMS = 2

# Keywords (case-insensitive, Hungarian) used to detect furnishing status.
FURNISHED_KEYWORDS = ["bútorozott", "butorozott", "berendezett", "felszerelt"]
PARTIALLY_FURNISHED_KEYWORDS = ["részben bútorozott", "reszben butorozott"]

# Keywords used to detect a terrace/balcony.
OUTDOOR_SPACE_KEYWORDS = ["erkély", "erkely", "terasz", "loggia"]

# Move-in availability: immediate, or from November 2026 onward.
IMMEDIATE_MOVE_IN_KEYWORDS = ["azonnal", "azonnal költözhető", "azonnal koltozheto"]
EARLIEST_MOVE_IN_YEAR = 2026
EARLIEST_MOVE_IN_MONTH = 11  # November

HUNGARIAN_MONTHS = {
    "január": 1, "januar": 1,
    "február": 2, "februar": 2,
    "március": 3, "marcius": 3,
    "április": 4, "aprilis": 4,
    "május": 5, "majus": 5,
    "június": 6, "junius": 6,
    "július": 7, "julius": 7,
    "augusztus": 8,
    "szeptember": 9,
    "október": 10, "oktober": 10,
    "november": 11,
    "december": 12,
}

# Only surface listings first seen within this many minutes of the current
# run (kept a bit above 60 to tolerate slow/late runs). Combined with the
# on-disk "seen" state file for deduplication.
FRESHNESS_WINDOW_MINUTES = 90

EMAIL_TO = "viktorszspam@gmail.com"
EMAIL_SUBJECT_PREFIX = "[Metrodom Green tracker]"
