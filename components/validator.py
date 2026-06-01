"""Invoice validator component for the automation engine.

Applies business rules to validate invoice dictionaries
against a set of approved vendors, credit limits, date
constraints, and accepted currencies. The four enforced rules
are: (1) vendor must be in the APPROVED_VENDORS list, (2)
amount must be positive and within the vendor credit limit,
(3) due date must be a future date in ISO format, (4) currency
must be INR or USD. Returns a result dict with 'valid' boolean
and an 'errors' list. All validation errors are collected
before returning so every problem is visible at once.
"""

import logging
import datetime

logger = logging.getLogger(__name__)

APPROVED_VENDORS = ['Vendor A', 'Vendor B', 'Vendor C', 'Vendor D']

CREDIT_LIMITS = {
    'Vendor A': 50000,
    'Vendor B': 30000,
    'Vendor C': 75000,
    'Vendor D': 20000,
}


def validate_invoice(invoice: dict) -> dict:
    try:
        return _validate(invoice)
    except Exception as e:
        logger.error('Component failed: %s', e)
        raise


def _validate(invoice: dict) -> dict:
    errors = []

    vendor = invoice.get('vendor', '')
    if vendor not in APPROVED_VENDORS:
        errors.append('Vendor not approved')

    amount = invoice.get('amount', 0)
    if not isinstance(amount, (int, float)) or amount <= 0:
        errors.append('Amount must be greater than zero')
    credit_limit = CREDIT_LIMITS.get(vendor)
    if credit_limit is not None and amount > credit_limit:
        errors.append(f'Amount exceeds credit limit of {credit_limit}')
    elif credit_limit is None and vendor in APPROVED_VENDORS:
        errors.append('No credit limit defined for vendor')

    due_date = invoice.get('due_date')
    try:
        if isinstance(due_date, str):
            due_date = datetime.date.fromisoformat(due_date)
        if due_date <= datetime.date.today():
            errors.append('Due date is not in the future')
    except (TypeError, ValueError):
        errors.append('Invalid due date format')

    currency = invoice.get('currency', '')
    if currency not in ['INR', 'USD']:
        errors.append('Currency must be INR or USD')

    result = {'valid': len(errors) == 0, 'errors': errors}
    logger.info('validator: valid=%s errors=%s', result['valid'], errors)
    return result
