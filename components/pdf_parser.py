import re
import os
import logging

logger = logging.getLogger(__name__)

#have added pytesseract for scanned image pdfs

import fitz
import pytesseract
from PIL import Image

# all possible labels 
LABELS = {
    "INVOICE",
    "INVOICE #",
    "INVOICE NUMBER",
    "INVOICE DATE",
    "DATE OF ISSUE",
    "DUE DATE",
    "BILLED TO",
    "BILL TO",
    "SHIP TO",
    "FROM",
    "VENDOR",
    "PURCHASE ORDER",
    "P.0.#",
    "P.O.#",
    "DESCRIPTION",
    "UNIT PRICE",
    "UNIT COST",
    "QTY",
    "AMOUNT",
    "SUBTOTAL",
    "DISCOUNT",
    "TAX",
    "SHIPPING",
    "INVOICE TOTAL",
    "TOTAL",
    "TERMS & CONDITIONS",
    "TERMS AND CONDITIONS",
}

#regex for date
DATE_RE = re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b")

#regex for money
MONEY_RE = re.compile(
    r"(?:[$₹€£]\s*)?[\d,]+(?:\.\d{2})?(?:\s*(?:AED|USD|INR|EUR|GBP))?",
    re.I,
)

#regex for currency
CURRENCY_RE = re.compile(r"\b(AED|USD|INR|EUR|GBP)\b|([$₹€£])", re.I)

#extract the contents of pdf
def read_pdf_text(pdf_path):
    text = ""

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: '{pdf_path}'")

    try:
        doc = fitz.open(pdf_path)

        for page in doc:
            page_text = page.get_text()

            if not page_text.strip():
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                page_text = pytesseract.image_to_string(img)

            text += page_text + "\n"

        doc.close()
    except FileNotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"Error reading PDF '{pdf_path}': {e}") from e

    return text

#clean the data into lines
def clean_lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]

# does it exist in our label set?
def is_label(line):
    normalized = re.sub(r"\s+", " ", line.strip().upper())
    return normalized in LABELS

# first date match becomes invoice date
def first_match(pattern, lines):
    for line in lines:
        match = re.search(pattern, line, re.I)
        if match:
            return match.group(1).strip()

    return None

# second date match becomes due date
def dates_after(lines, start_index):
    dates = []

    for line in lines[start_index + 1:]:
        dates.extend(DATE_RE.findall(line))

    return dates

# Remove currency symbols/codes so only the amount remains
def normalize_money(value):
    if not value:
        return None

    value = re.sub(r"^[^\d-]+", "", value.strip())
    value = re.sub(r"\s+(AED|USD|INR|EUR|GBP)$", "", value, flags=re.I)
    return value.strip()

# Detect currency code or symbol from text
def currency_from_text(value):
    if not value:
        return None

    match = CURRENCY_RE.search(value)
    if not match:
        return None

    symbol_map = {"$": "USD", "₹": "INR", "€": "EUR", "£": "GBP"}
    return (match.group(1) or symbol_map.get(match.group(2))).upper()

# Guess whether a line is a company/vendor name
def looks_like_company(line):
    return bool(
        re.search(
            r"\b(inc\.?|llc|ltd\.?|limited|company|corp\.?|corporation|events?)\b",
            line,
            re.I,
        )
    )

#extracting features
def extract_vendor(lines):
    if any(line.upper() == "FROM" for line in lines):
        country_indexes = [
            index
            for index, line in enumerate(lines)
            if re.fullmatch(r"United Arab Emirates", line, re.I)
        ]

        if len(country_indexes) >= 2:
            vendor_parts = []

            for line in lines[country_indexes[0] + 1:country_indexes[1]]:
                if re.search(r"business bay|dubai|phone|email", line, re.I):
                    break

                vendor_parts.append(line)

            if vendor_parts:
                return " ".join(vendor_parts)

        from_index = next(index for index, line in enumerate(lines) if line.upper() == "FROM")

        for line in lines[from_index + 1:]:
            if not is_label(line):
                return line

    for index, line in enumerate(lines[:12]):
        if looks_like_company(line) and line.upper() != "VENDOR":
            return line

        if index > 0 and lines[index - 1].upper() == "INVOICE" and not is_label(line):
            return line

    return None


def extract_invoice_number(lines):
    value = first_match(r"\bInvoice\s*#\s*([A-Z]{0,5}-?\d+[A-Z0-9-]*)\b", lines)
    if value:
        return value

    label_indexes = [
        index
        for index, line in enumerate(lines)
        if re.fullmatch(r"INVOICE\s*(?:#|NUMBER)", line, re.I)
    ]

    for index in label_indexes:
        for line in lines[index + 1:]:
            if is_label(line):
                continue

            if re.fullmatch(r"[A-Z]{1,5}-\d+[A-Z0-9-]*", line, re.I):
                return line

            if re.fullmatch(r"\d{1,8}", line):
                return line

    return None


def extract_invoice_date(lines):
    value = first_match(r"\bInvoice date\s*[:\-]?\s*(" + DATE_RE.pattern + r")", lines)
    if value:
        return value

    for index, line in enumerate(lines):
        if re.fullmatch(r"INVOICE DATE|DATE OF ISSUE", line, re.I):
            dates = dates_after(lines, index)
            if dates:
                return dates[0]

    return None


def extract_due_date(lines):
    value = first_match(r"\bDue date\s*[:\-]?\s*(" + DATE_RE.pattern + r")", lines)
    if value:
        return value

    for index, line in enumerate(lines):
        if re.fullmatch(r"DUE DATE", line, re.I):
            dates = dates_after(lines, index)
            if len(dates) >= 2:
                return dates[1]

            if dates:
                return dates[0]

    return None

#either the last amount of stack or checks for amount beside total label
def extract_total_amount(lines):
    for index, line in enumerate(lines):
        if re.fullmatch(r"INVOICE TOTAL", line, re.I):
            values = [
                match.group(0)
                for value_line in lines[index + 1:index + 8]
                if (match := MONEY_RE.search(value_line))
            ]

            if values:
                return normalize_money(values[-1])

        match = re.search(
            r"\b(?:invoice\s+)?total\s*(?:\([A-Z]{3}\))?\s*[:\-]?\s*"
            r"([$₹€£]?\s*[\d,]+(?:\.\d{2})?(?:\s*[A-Z]{3})?)",
            line,
            re.I,
        )

        if match and not re.search(r"sub\s*total|subtotal", line, re.I):
            return normalize_money(match.group(1))

    money_after_total = []
    total_seen = False

    for line in lines:
        if re.fullmatch(r"TOTAL", line, re.I):
            total_seen = True
            continue

        if not total_seen or re.search(r"terms|please make|checks payable", line, re.I):
            continue

        for match in MONEY_RE.finditer(line):
            value = match.group(0).strip()
            if value and re.search(r"[$₹€£]|(?:AED|USD|INR|EUR|GBP)", value, re.I):
                money_after_total.append(value)

    if money_after_total:
        return normalize_money(money_after_total[-1])

    return None


def extract_currency(lines):
    for line in lines:
        currency = currency_from_text(line)
        if currency:
            return currency

    return None

#checks through the table structure
def extract_row_line_items(lines):
    items = []

    for line in lines:
        match = re.search(
            r"^(\d+(?:\.\d+)?)\s+(.+?)\s+([\d,]+(?:\.\d{2})?)\s+\$?([\d,]+(?:\.\d{2})?)$",
            line,
        )

        if match:
            items.append(
                {
                    "item_name": match.group(2).strip(),
                    "unit_price": match.group(3),
                    "quantity": match.group(1),
                    "amount": match.group(4),
                }
            )

    return items


def extract_stacked_line_items(lines):
    try:
        amount_header = next(
            index
            for index, line in enumerate(lines)
            if re.fullmatch(r"Amount", line, re.I)
            and index >= 2
            and re.search(r"QTY", lines[index - 1], re.I)
        )
    except StopIteration:
        return []

    table_lines = []

    for line in lines[amount_header + 1:]:
        if re.fullmatch(r"SUBTOTAL|DISCOUNT|\(TAX RATE\)|TAX|SHIPPING|INVOICE TOTAL|TOTAL", line, re.I):
            break

        table_lines.append(line)

    items = []

    for index in range(0, len(table_lines) - 3, 4):
        name, unit_price, quantity, amount = table_lines[index:index + 4]

        if (
            re.search(r"[A-Za-z]", name)
            and re.fullmatch(r"[\d,]+(?:\.\d{2})?", unit_price)
            and re.fullmatch(r"\d+(?:\.\d+)?", quantity)
        ):
            items.append(
                {
                    "item_name": name,
                    "unit_price": unit_price,
                    "quantity": quantity,
                    "amount": amount,
                }
            )

    return items


def extract_column_line_items(lines):
    if not any(re.fullmatch(r"DESCRIPTION", line, re.I) for line in lines):
        return []

    desc_start = next(index for index, line in enumerate(lines) if re.fullmatch(r"DESCRIPTION", line, re.I))
    descriptions = []

    for line in lines[desc_start + 1:]:
        if re.fullmatch(r"Shank you|Thank you|INVOICE #|UNIT PRICE", line, re.I):
            break

        match = re.match(r"^(\d+(?:\.\d+)?)\s+(.+)$", line)
        if match:
            descriptions.append((match.group(1), match.group(2).strip()))

    prices = extract_number_block(lines, "UNIT PRICE", r"Subtotal|Sales Tax.*|TOTAL|TERMS.*|AMOUNT")
    amounts = extract_number_block(lines, "AMOUNT", stop_after_numbers=True)

    return [
        {
            "item_name": name,
            "unit_price": prices[index] if index < len(prices) else None,
            "quantity": quantity,
            "amount": amounts[index] if index < len(amounts) else None,
        }
        for index, (quantity, name) in enumerate(descriptions)
    ]


def extract_number_block(lines, header, stop_pattern=None, stop_after_numbers=False):
    try:
        start = next(index for index, line in enumerate(lines) if re.fullmatch(header, line, re.I))
    except StopIteration:
        return []

    values = []

    for line in lines[start + 1:]:
        if stop_pattern and re.fullmatch(stop_pattern, line, re.I):
            break

        if re.fullmatch(r"[\d,]+(?:\.\d{2})?", line):
            values.append(line)
        elif stop_after_numbers and values:
            break

    return values


def extract_line_items(lines):
    return (
        extract_row_line_items(lines)
        or extract_stacked_line_items(lines)
        or extract_column_line_items(lines)
    )


def parse_invoice(pdf_path):
    try:
        text = read_pdf_text(pdf_path)
        lines = clean_lines(text)
        result = {
            "vendor": extract_vendor(lines),
            "invoice_no": extract_invoice_number(lines),
            "invoice_date": extract_invoice_date(lines),
            "due_date": extract_due_date(lines),
            "amount": extract_total_amount(lines),
            "currency": extract_currency(lines),
            "line_items": extract_line_items(lines),
        }
        logger.info('pdf_parser: parsed %s', pdf_path)
        return result
    except Exception as e:
        logger.error('Component failed: %s', e)
        raise
