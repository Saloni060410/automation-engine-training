import os
import logging
import tempfile
import requests
from dotenv import load_dotenv

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

from components.email_reader import fetch_latest_pdf_email
from components.pdf_parser import parse_invoice
from components.llm_extractor import extract_invoice
from components.validator import validate_invoice
from components.api_caller import post_to_api

load_dotenv()

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")
SAP_ENDPOINT  = os.getenv("SAP_ENDPOINT", "https://httpbin.org/post")


def send_slack(message: str):
    requests.post(SLACK_WEBHOOK, json={"text": message}, timeout=10)


def run_pipeline():
    logger.info('pipeline: starting run')
    print("\n--- Step 1: Fetch latest email with PDF attachment ---")
    subject, sender, pdf_bytes, filename = fetch_latest_pdf_email()

    if not pdf_bytes:
        msg = "No email with PDF attachment found in the last 50 emails."
        print(msg)
        send_slack(f":warning: Pipeline skipped: {msg}")
        return

    print(f"Found: '{filename}' | From: {sender} | Subject: {subject}")

    print("\n Step 2: Parse PDF ")
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name

    try:
        invoice_data = parse_invoice(tmp_path)
    finally:
        os.unlink(tmp_path)

    print(f"Parsed: {invoice_data}")

    print("\n Step 3: LLM extraction ")
    raw_text = "\n".join(f"{k}: {v}" for k, v in invoice_data.items() if v)
    invoice_obj = extract_invoice(raw_text)
    invoice_dict = invoice_obj.model_dump()
    print(f"Extracted: {invoice_dict}")

    print("\n Step 4: Validate ")
    amount_raw = invoice_dict.get("amount") or 0
    try:
        amount = float(str(amount_raw).replace(",", ""))
    except (ValueError, TypeError):
        amount = 0

    validation_input = {
        "vendor":   invoice_dict.get("vendor") or "",
        "amount":   amount,
        "due_date": invoice_dict.get("due_date") or "",
        "currency": invoice_dict.get("currency") or "",
    }
    result = validate_invoice(validation_input)
    print(f"Validation: {result}")

    print("\n Step 5: Send to SAP + Slack ")
    if result["valid"]:
        try:
            api_response = post_to_api(SAP_ENDPOINT, invoice_dict)
            print(f"SAP response: {api_response}")
        except Exception as e:
            print(f"SAP call failed (non-fatal): {e}")

        slack_msg = (
            f":white_check_mark: *Invoice processed successfully*\n"
            f">*From:* {sender}\n"
            f">*Subject:* {subject}\n"
            f">*Vendor:* {invoice_dict.get('vendor')}\n"
            f">*Amount:* {invoice_dict.get('amount')} {invoice_dict.get('currency')}\n"
            f">*Due Date:* {invoice_dict.get('due_date')}\n"
            f">*Invoice #:* {invoice_dict.get('invoice_no')}"
        )
    else:
        slack_msg = (
            f":x: *Invoice validation failed*\n"
            f">*From:* {sender}\n"
            f">*Subject:* {subject}\n"
            f">*Errors:* {', '.join(result['errors'])}"
        )

    send_slack(slack_msg)
    print(f"Slack notification sent.")
    print(f"\nPipeline complete. Valid: {result['valid']}")


if __name__ == "__main__":
    run_pipeline()
