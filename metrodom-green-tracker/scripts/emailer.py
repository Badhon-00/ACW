"""Sends the match notification email over SMTP.

Reads credentials from environment variables so no secret ever needs to
be written to disk or committed:

  GMAIL_ADDRESS       - the Gmail account to send from
  GMAIL_APP_PASSWORD  - a Gmail App Password (not the account password;
                        requires 2FA enabled on the account, generated at
                        https://myaccount.google.com/apppasswords)

In GitHub Actions these are read from repository secrets of the same
name (see .github/workflows/metrodom-green-tracker.yml).
"""

import os
import smtplib
from email.mime.text import MIMEText

import config


def format_email_body(listings) -> str:
    lines = [f"{len(listings)} new match(es) for the Metrodom Green search:\n"]
    for listing in listings:
        lines.append("-" * 60)
        lines.append(listing.title)
        lines.append(f"Source: {listing.source}")
        if listing.price_text:
            lines.append(f"Price: {listing.price_text}")
        if listing.size_sqm:
            lines.append(f"Size: {listing.size_sqm} sqm")
        if listing.rooms:
            lines.append(f"Rooms: {listing.rooms}")
        if listing.address_text:
            lines.append(f"Address: {listing.address_text}")
        if listing.furnished_status:
            lines.append(f"Furnished: {listing.furnished_status}")
        if listing.notes:
            lines.append("Notes: " + "; ".join(listing.notes))
        lines.append(f"Link: {listing.url}")
        lines.append("")
    return "\n".join(lines)


def send_email(listings, to_address: str = None) -> bool:
    to_address = to_address or config.EMAIL_TO
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    app_password = os.environ.get("GMAIL_APP_PASSWORD")

    if not gmail_address or not app_password:
        print(
            "GMAIL_ADDRESS / GMAIL_APP_PASSWORD not set — skipping send. "
            "Set these as GitHub Actions secrets to enable real email delivery."
        )
        print(format_email_body(listings))
        return False

    subject = f"{config.EMAIL_SUBJECT_PREFIX} {len(listings)} new match(es)"
    body = format_email_body(listings)

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = gmail_address
    msg["To"] = to_address

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, app_password)
        server.sendmail(gmail_address, [to_address], msg.as_string())

    print(f"Sent email with {len(listings)} match(es) to {to_address}")
    return True
