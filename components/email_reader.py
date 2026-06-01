import logging
from imap_tools import MailBox
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)

load_dotenv()

EMAIL    = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")


def fetch_emails(limit=10):
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


def fetch_latest_pdf_email(limit=50):
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
