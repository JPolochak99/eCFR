from __future__ import annotations

import re

def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", str(name).strip())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or "CFR Export Workbook"
