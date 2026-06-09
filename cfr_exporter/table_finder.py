from .ecfr_client import fetch_api
from .table_catalog import build_table_catalog

def find_tables(
    title: str,
    subtitle: str,
    chapter: str,
    subchapter: str,
    part: str,
    subpart: str,
    section: str,
    effective_date_str: str,
):
    """
    Fetch the eCFR XML for the requested section and return the table catalog.
    """
    xml_text = fetch_api(
        title=title,
        subtitle=subtitle,
        chapter=chapter,
        subchapter=subchapter,
        part=part,
        subpart=subpart,
        section=section,
        date_str=effective_date_str,
    )

    return build_table_catalog(xml_text)