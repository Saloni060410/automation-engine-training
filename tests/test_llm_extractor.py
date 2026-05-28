# test_llm_extractor.py

from components.llm_extractor import (
    extract_invoice
)


# Sample invoice 1
invoice_1 = """
Invoice Number: INV-1001
Vendor: Adobe Inc.
Invoice Date: 2025-07-10
Due Date: 2025-07-20
Currency: USD
Total Amount: 599.00 USD

Items:
Creative Cloud Subscription 1 599.00
"""


# Sample invoice 2
invoice_2 = """
INVOICE # US-001

From:
East Repair Inc.

Invoice Date: 11/02/2019
Due Date: 26/02/2019

Total: 154.06 USD

Items:
Front and rear brake cables 2 100.00
New set of pedal arms 1 54.06
"""


# Sample invoice 3
invoice_3 = """
Invoice Number: 0000007

Vendor:
Your Company Inc.

Invoice Date: 10-02-2023
Due Date: 10-16-2023

Invoice Total: 577.50 USD

Items:
Web Design 1 400
Hosting 1 177.50
"""


# Run all three invoices through the extractor and print results
def run_tests():

    invoices = [
        invoice_1,
        invoice_2,
        invoice_3
    ]

    for index, invoice_text in enumerate(invoices):

        print("\n" + "=" * 70)
        print(f"TESTING INVOICE {index + 1}")
        print("=" * 70)

        result = extract_invoice(invoice_text)

        print("\nFINAL STRUCTURED OUTPUT:\n")

        print(result.model_dump())


if __name__ == "__main__":
    run_tests()