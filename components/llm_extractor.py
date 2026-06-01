# components/llm_extractor.py

import os
import json
import time
import logging

logger = logging.getLogger(__name__)

import google.genai as genai
from google.genai.errors import ClientError, ServerError

from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional


# Load environment variables
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODELS = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash"]


# Pydantic schemas for structured invoice data
class LineItem(BaseModel):

    description: Optional[str] = None
    qty: Optional[float] = None
    unit_price: Optional[float] = None


class InvoiceData(BaseModel):

    vendor: Optional[str] = None
    invoice_no: Optional[str] = None
    amount: Optional[str] = None
    currency: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None

    line_items: List[LineItem] = []


# Load the extraction prompt from file
def load_prompt():

    with open(
        "prompts/invoice_extract.txt",
        "r"
    ) as file:

        return file.read()


# Strip markdown code fences from the model response
def clean_json_response(text):

    text = text.strip()

    text = text.replace(
        "```json",
        ""
    )

    text = text.replace(
        "```",
        ""
    )

    return text.strip()


# Main function to extract structured data from raw invoice text
def extract_invoice(raw_text: str):

    prompt = load_prompt()

    final_prompt = f"""
{prompt}

INVOICE TEXT:
{raw_text}
"""

    for model in MODELS:

        print(f"Trying model: {model}")

        retry_count = 0
        max_retries = 4

        while retry_count < max_retries:

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=final_prompt
                )

                response_text = clean_json_response(response.text)

                parsed_json = json.loads(response_text)

                logger.info('llm_extractor: extracted invoice using %s', model)
                return InvoiceData(**parsed_json)

            except json.JSONDecodeError:

                print(
                    f"JSON Parse Error. Retrying... "
                    f"Attempt {retry_count + 1}"
                )
                logger.error('Component failed: JSON parse error on attempt %d', retry_count + 1)

                retry_count += 1

            except ClientError as e:

                if e.code != 429:
                    print(f"API Error ({e.code}): {e.message}")
                    break

                details = (e.details or {}).get("error", {}).get("details", [])

                violations = []
                retry_delay = 30

                for detail in details:
                    if "violations" in detail:
                        violations = detail["violations"]
                    if detail.get("@type", "").endswith("RetryInfo"):
                        delay_str = detail.get("retryDelay", "30s")
                        retry_delay = int(float(delay_str.rstrip("s"))) + 1

                if any("PerDay" in v.get("quotaId", "") for v in violations):
                    print(
                        f"Daily quota exhausted for {model}. "
                        f"Trying next model..."
                    )
                    break

                print(
                    f"Rate limit hit. Waiting {retry_delay}s before retry... "
                    f"Attempt {retry_count + 1}"
                )

                time.sleep(retry_delay)
                retry_count += 1

            except ServerError as e:

                print(
                    f"Server error ({e.code}). Waiting 10s before retry... "
                    f"Attempt {retry_count + 1}"
                )

                time.sleep(10)
                retry_count += 1

            except Exception as e:

                print(f"Unexpected Error: {e}")
                logger.error('Component failed: %s', e)
                break

    raise Exception(
        "All models exhausted. Check your API key or wait until quota resets."
    )