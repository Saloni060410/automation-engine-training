from imap_tools import MailBox
from dotenv.main import load_dotenv
import os

load_dotenv()

EMAIL=os.getenv("EMAIL")
PASSWORD=os.getenv("PASSWORD")

def fetch_emails(limit=10):
    emails=[]

    with MailBox("imap.gmail.com").login(EMAIL,PASSWORD) as mailbox:

        messages=mailbox.fetch(limit=limit,reverse=True)
        
        for msg in messages:

            email_data={
                'sender':msg.from_,
                'subject':msg.subject,
                'date':str(msg.date),
                'body': msg.text
            }

            emails.append(email_data)

    return emails

emails = fetch_emails()

print("\nLatest Email Subjects:\n")

for email in emails[:5]:
    print(f"From    : {email['sender']}")
    print(f"Subject : {email['subject']}")
    print(f"Date    : {email['date']}\n\n")
    
