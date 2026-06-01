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
