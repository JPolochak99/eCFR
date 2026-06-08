from __future__ import annotations

from bs4 import BeautifulSoup


def truncate(text: str, max_len: int = 50) -> str:
    return text if len(text) <= max_len else text[:max_len] + "..."


def build_table_catalog(xml_text: str, title_len: int = 100):
    """Return a list of table descriptors extracted from the eCFR XML."""
    soup = BeautifulSoup(xml_text, "xml")
    tables = soup.find_all("TABLE")

    catalog = []
    for i, table in enumerate(tables, start=1):
        caption = table.find("CAPTION")
        caption_text = caption.get_text(" ", strip=True) if caption else ""

        prev = table.find_previous(
            ["H1", "H2", "H3", "H4", "H5", "H6", "P", "DIV", "B", "STRONG"]
        )
        prev_text = prev.get_text(" ", strip=True) if prev else ""

        title_text = caption_text or prev_text or ""
        title_text = truncate(title_text, max_len=title_len)

        catalog.append(
            {
                "index": i,
                "label": f"Table {i}",
                "title": title_text,
                "html": str(table),
            }
        )

    return catalog
