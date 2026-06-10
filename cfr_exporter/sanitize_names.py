from __future__ import annotations

import re

INVALID_SHEET_CHARS = r"[:\\/?*\[\]]"

def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", str(name).strip())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or "CFR Export Workbook"

def sanitize_sheet_name(name: str) -> str:
    cleaned = re.sub(INVALID_SHEET_CHARS, "_", str(name).strip())
    cleaned = cleaned[:31].strip()
    return cleaned or "Sheet1"

def truncate(text: str, max_len: int = 100) -> str:
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."