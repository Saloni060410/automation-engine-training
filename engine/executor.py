import os
import sys
import json
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from components.email_reader import fetch_emails
from components.pdf_parser import parse_invoice
from components.llm_extractor import extract_invoice
from components.validator import validate_invoice

COMPONENTS = {
    'email_reader': fetch_emails,
    'pdf_parser': parse_invoice,
    'llm_extractor': extract_invoice,
    'validator': validate_invoice,
}


def _chain_params(component_name: str, prev_result) -> dict:
    """Build params for a step from the previous step's output when params is empty."""
    if component_name == 'llm_extractor':
        if isinstance(prev_result, dict):
            raw_text = "\n".join(f"{k}: {v}" for k, v in prev_result.items() if v)
        elif isinstance(prev_result, list):
            raw_text = "\n".join(str(item) for item in prev_result)
        else:
            raw_text = str(prev_result)
        return {'raw_text': raw_text}

    if component_name == 'validator':
        if hasattr(prev_result, 'model_dump'):
            inv = prev_result.model_dump()
        elif isinstance(prev_result, dict):
            inv = prev_result
        else:
            return {}
        try:
            amount = float(str(inv.get('amount') or 0).replace(',', ''))
        except (ValueError, TypeError):
            amount = 0
        return {'invoice': {
            'vendor':   inv.get('vendor') or '',
            'amount':   amount,
            'due_date': inv.get('due_date') or '',
            'currency': inv.get('currency') or '',
        }}

    if component_name == 'api_caller':
        if hasattr(prev_result, 'model_dump'):
            payload = prev_result.model_dump()
        elif isinstance(prev_result, dict):
            payload = prev_result
        else:
            payload = {'result': str(prev_result)}
        return {'url': 'https://httpbin.org/post', 'payload': payload}

    return {}


def execute_workflow(workflow: list) -> dict:
    execution_log = {
        'steps': [],
        'status': 'running'
    }

    has_error = False
    prev_result = None

    for step in workflow:
        step_number = step.get('step')
        component_name = step.get('component')
        params = step.get('params', {})

        # Auto-chain from previous step's output when params is empty
        if not params and prev_result is not None:
            params = _chain_params(component_name, prev_result)

        step_log = {
            'step': step_number,
            'component': component_name,
            'input_params': params,
            'output_summary': None,
            'duration_seconds': None,
            'status': None,
        }

        component_fn = COMPONENTS.get(component_name)
        if component_fn is None:
            step_log['status'] = 'error'
            step_log['output_summary'] = f"Unknown component: {component_name}"
            has_error = True
            execution_log['steps'].append(step_log)
            continue

        start = datetime.datetime.now()
        try:
            result = component_fn(**params)
            prev_result = result

            # Summarize output for the log
            if hasattr(result, 'model_dump'):
                summary = result.model_dump()
            elif isinstance(result, (dict, list)):
                summary = result
            else:
                summary = str(result)

            step_log['status'] = 'success'
            step_log['output_summary'] = summary

        except Exception as e:
            step_log['status'] = 'error'
            step_log['output_summary'] = str(e)
            has_error = True

        finally:
            duration = (datetime.datetime.now() - start).total_seconds()
            step_log['duration_seconds'] = round(duration, 3)

        execution_log['steps'].append(step_log)

    execution_log['status'] = 'partial' if has_error else 'completed'

    os.makedirs('logs', exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_path = f'logs/run_{timestamp}.json'

    with open(log_path, 'w') as f:
        json.dump(execution_log, f, indent=2, default=str)

    print(f"Log saved to {log_path}")
    return execution_log


if __name__ == "__main__":
    test_workflow = [
        {
            'step': 1,
            'component': 'email_reader',
            'params': {'limit': 2}
        },
        {
            'step': 2,
            'component': 'pdf_parser',
            'params': {'pdf_path': 'test_data/Invoice1.pdf'}
        },
        {
            'step': 3,
            'component': 'llm_extractor',
            'params': {'raw_text': 'Invoice Number: INV-001\nVendor: Vendor A\nAmount: 5000 INR\nDue Date: 2026-07-01'}
        },
        {
            'step': 4,
            'component': 'validator',
            'params': {
                'invoice': {
                    'vendor': 'Vendor A',
                    'amount': 5000,
                    'due_date': '2026-07-01',
                    'currency': 'INR'
                }
            }
        }
    ]

    result = execute_workflow(test_workflow)
    print(f"\nStatus: {result['status']}")
    for s in result['steps']:
        print(f"  Step {s['step']} ({s['component']}): {s['status']} in {s['duration_seconds']}s")
