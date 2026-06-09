from __future__ import annotations

import requests


def fetch_api(
    title: str,
    subtitle: str,
    chapter: str,
    subchapter: str,
    part: str,
    subpart: str,
    section: str,
    date_str: str,
) -> str:
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


