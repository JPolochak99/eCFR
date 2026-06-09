from __future__ import annotations

import datetime as dt

import requests

TITLES_URL = "https://www.ecfr.gov/api/versioner/v1/titles.json"

def resolve_effective_date(title: str, use_latest: bool, custom_date: dt.date) -> str:
    if use_latest:
        return get_latest_available_date(title)
    return custom_date.isoformat()


def get_latest_available_date(title: str) -> str:
    resp = requests.get(TITLES_URL, timeout=30)
    resp.raise_for_status()
    payload = resp.json()

    title_num = int(title)
    for item in payload.get("titles", []):
        try:
            if int(item.get("number")) == title_num:
                latest = item.get("up_to_date_as_of")
                if not latest:
                    raise ValueError(f"No up_to_date_as_of found for Title {title}")
                return latest
        except (TypeError, ValueError):
            continue

    raise ValueError(f"Title {title} not found in titles.json")
