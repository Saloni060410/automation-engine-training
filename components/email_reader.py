"""Email reader component for the automation engine.

This module handles Gmail mailbox access using IMAP to fetch
emails and extract PDF invoice attachments for downstream
processing. It provides two main functions: one for listing
recent email subjects and another for locating the most
recent email that contains a PDF attachment. Credentials are
loaded from environment variables (EMAIL and PASSWORD). The
module uses imap-tools for clean IMAP abstraction. All
operations are wrapped in structured error handling with
Python's logging module to ensure failures are captured
without crashing the pipeline.
"""

import os
import logging
from imap_tools import MailBox
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

EMAIL    = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")


def fetch_emails(limit: int = 10) -> list:
    try:
        emails = []
        with MailBox("imap.gmail.com").login(EMAIL, PASSWORD) as mailbox:
            for msg in mailbox.fetch(limit=limit, reverse=True):
                emails.append({
                    'sender':  msg.from_,
                    'subject': msg.subject,
                    'date':    str(msg.date),
                    'body':    msg.text,
                })

        print("\nLatest Email Subjects:\n")
        for email in emails[:5]:
            print(f"From    : {email['sender']}")
            print(f"Subject : {email['subject']}")
            print(f"Date    : {email['date']}\n")

        logger.info('email_reader: fetched %d emails', len(emails))
        return emails
    except Exception as e:
        logger.error('Component failed: %s', e)
        raise


def fetch_latest_pdf_email(limit: int = 50) -> tuple:
    """Return (subject, sender, pdf_bytes, filename) for the most recent email with a PDF attachment."""
    try:
        with MailBox("imap.gmail.com").login(EMAIL, PASSWORD) as mailbox:
            for msg in mailbox.fetch(reverse=True, limit=limit):
                for att in msg.attachments:
                    if att.content_type == "application/pdf" or att.filename.lower().endswith(".pdf"):
                        logger.info('email_reader: found PDF "%s" in "%s"', att.filename, msg.subject)
                        return msg.subject, msg.from_, att.payload, att.filename
        logger.warning('email_reader: no PDF attachment found in last %d emails', limit)
        return None, None, None, None
    except Exception as e:
        logger.error('Component failed: %s', e)
        raise
