from __future__ import annotations

from io import BytesIO
import re
import pandas as pd


INVALID_SHEET_CHARS = r"[:\\/?*\[\]]"


def sanitize_sheet_name(name: str) -> str:
    cleaned = re.sub(INVALID_SHEET_CHARS, "_", name.strip())
    cleaned = cleaned[:31].strip()
    return cleaned or "Sheet1"


def unique_sheet_name(name: str, used_names: set[str]) -> str:
    base = sanitize_sheet_name(name)

    if base not in used_names:
        used_names.add(base)
        return base

    i = 2
    while True:
        suffix = f"_{i}"
        candidate = base[:31 - len(suffix)] + suffix
        if candidate not in used_names:
            used_names.add(candidate)
            return candidate
        i += 1


def build_workbook_bytes(workbook_tables):
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        used_names = set()

        for item in workbook_tables:
            sheet_name = unique_sheet_name(item["sheet_name"], used_names)
            item["df"].to_excel(writer, index=False, sheet_name=sheet_name)

    buffer.seek(0)
    return buffer.getvalue()
