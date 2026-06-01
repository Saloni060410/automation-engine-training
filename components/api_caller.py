"""API caller component for the automation engine.

Sends invoice data to external REST endpoints (such as SAP or
mock systems) via HTTP POST requests. Implements a three-
attempt retry loop with a one-second delay between attempts to
handle transient network errors. Each request uses a 10-second
timeout. On success, returns the parsed JSON response dict.
If all three attempts fail, the last exception is re-raised
to the caller. All failures are logged via Python's logging
module. Default headers can be overridden for auth tokens or
content-type customization.
"""

import time
import logging
import requests

logger = logging.getLogger(__name__)


def post_to_api(url: str, payload: dict, headers: dict = {}) -> dict:
    last_exc = None
    for attempt in range(3):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            logger.info('api_caller: POST %s succeeded on attempt %d', url, attempt + 1)
            return response.json()
        except Exception as e:
            last_exc = e
            logger.error('Component failed: %s', e)
            if attempt < 2:
                time.sleep(1)
    raise last_exc
