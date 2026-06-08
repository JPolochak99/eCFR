from __future__ import annotations

import requests

ECFR_BASE_URL = "https://www.ecfr.gov"
DEFAULT_TIMEOUT_SECONDS = 60


def fetch_page(
        title, 
        subtitle, 
        chapter, 
        subchapter, 
        part, 
        subpart, 
        section, 
        date_str):
    
    base_url = "https://www.ecfr.gov"

    url = f"{base_url}/api/versioner/v1/full/{date_str}/title-{title}.xml"
    params = {
        "subtitle": subtitle,
        "chapter": chapter,
        "subchapter": subchapter,
        "part": part,
        "subpart": subpart,
        "section": section,
    }
    headers = {
        "Accept": "application/xml,text/xml,*/*",
        "User-Agent": "Mozilla/5.0",
    }

    response = requests.get(url, headers=headers, params=params, timeout=60)
    response.raise_for_status()
    response.encoding = "utf-8"
    return response.text

TITLES_URL = "https://www.ecfr.gov/api/versioner/v1/titles.json"


def get_latest_available_date(title_number: str) -> str:
    """
    Return the eCFR 'up_to_date_as_of' for a title, e.g. '2026-06-04'.
    """
    resp = requests.get(TITLES_URL, timeout=30)
    resp.raise_for_status()
    payload = resp.json()

    title_num = int(title_number)

    for title in payload.get("titles", []):
        if int(title["number"]) == title_num:
            latest = title.get("up_to_date_as_of")
            if not latest:
                raise ValueError(f"No up_to_date_as_of found for Title {title_number}")
            return latest

    raise ValueError(f"Title {title_number} not found in titles.json")