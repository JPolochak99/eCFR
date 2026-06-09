from __future__ import annotations

import re


def truncate(text: str, max_len: int = 100) -> str:
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."

