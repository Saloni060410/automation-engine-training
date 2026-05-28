import requests


def post_to_api(url: str, payload: dict, headers: dict = {}) -> dict:
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
