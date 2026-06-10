from __future__ import annotations

import re

from bs4 import BeautifulSoup
from cfr_exporter.sanitize_names import truncate



def build_table_catalog(xml_text: str):
    soup = BeautifulSoup(xml_text, "xml")
    tables = soup.find_all("TABLE")

    catalog = []
    for i, table in enumerate(tables, start=1):
        caption = table.find("CAPTION")
        caption_text = caption.get_text(" ", strip=True) if caption else ""

        prev = table.find_previous([
            "H1", "H2", "H3", "H4", "H5", "H6", "P", "DIV", "B", "STRONG"
        ])
        prev_text = prev.get_text(" ", strip=True) if prev else ""

        title_text = caption_text or prev_text or f"Table {i}"
        title_text = truncate(re.sub(r"\s+", " ", title_text), max_len=100)

        catalog.append(
            {
                "index": i,
                "label": f"Table {i}",
                "title": title_text,
                "html": str(table),
            }
        )

    return catalog
