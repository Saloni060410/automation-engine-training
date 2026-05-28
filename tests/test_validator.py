import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import datetime
from components.validator import validate_invoice


def future_date(days=10):
    return (datetime.date.today() + datetime.timedelta(days=days)).isoformat()


def past_date(days=5):
    return (datetime.date.today() - datetime.timedelta(days=days)).isoformat()


# Valid cases

def test_valid_invoice_inr():
    invoice = {
        'vendor': 'Vendor A',
        'amount': 10000,
        'due_date': future_date(),
        'currency': 'INR',
    }
    result = validate_invoice(invoice)
    assert result['valid'] is True
    assert result['errors'] == []


def test_valid_invoice_usd():
    invoice = {
        'vendor': 'Vendor B',
        'amount': 25000,
        'due_date': future_date(days=30),
        'currency': 'USD',
    }
    result = validate_invoice(invoice)
    assert result['valid'] is True
    assert result['errors'] == []


# Invalid cases 

def test_invalid_vendor():
    invoice = {
        'vendor': 'Unknown Corp',
        'amount': 5000,
        'due_date': future_date(),
        'currency': 'INR',
    }
    result = validate_invoice(invoice)
    assert result['valid'] is False
    assert 'Vendor not approved' in result['errors']


def test_exceeds_credit_limit():
    invoice = {
        'vendor': 'Vendor A',
        'amount': 99999,
        'due_date': future_date(),
        'currency': 'USD',
    }
    result = validate_invoice(invoice)
    assert result['valid'] is False
    assert any('credit limit' in e for e in result['errors'])


def test_past_due_date():
    invoice = {
        'vendor': 'Vendor C',
        'amount': 1000,
        'due_date': past_date(),
        'currency': 'INR',
    }
    result = validate_invoice(invoice)
    assert result['valid'] is False
    assert 'Due date is not in the future' in result['errors']
