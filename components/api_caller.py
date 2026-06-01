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
