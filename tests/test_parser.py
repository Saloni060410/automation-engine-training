# test_parser.py

import os

from components.pdf_parser import parse_invoice


TEST_FOLDER = "test_data"


def test_all_invoices():

    files = os.listdir(TEST_FOLDER)

    pdf_files = [f for f in files if f.endswith(".pdf")]

    for pdf in pdf_files:

        path = os.path.join(TEST_FOLDER, pdf)

        print("\n" + "=" * 70)
        print(f"PROCESSING: {pdf}")
        print("=" * 70)

        result = parse_invoice(path)

        print("\nFINAL RESULT:\n")

        print(result)


if __name__ == "__main__":
    test_all_invoices()