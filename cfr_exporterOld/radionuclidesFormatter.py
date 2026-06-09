from __future__ import annotations

import re
import pandas as pd
from .elements import ELEMENT_NAME_TO_SYMBOL

RADIONUCLIDE_SYMBOL_RE = re.compile(r"^([A-Z][a-z]?)-(\d+)([A-Za-z]*)$")
RADIONUCLIDE_NAME_RE = re.compile(r"^([A-Za-z][A-Za-z\s\-]+?)[\s\-]+(\d+)([A-Za-z]*)$")


def parse_radionuclide(value):
    """
    Normalize radionuclide text.

    Returns:
        formatted, note_text, footnote_text, core
    """
    if pd.isna(value):
        return value, "", "", ""

    s = str(value).strip()

    notes = re.findall(r"\(([^)]*)\)", s)

    footnotes = []
    descriptions = []

    for note in notes:
        note = note.strip().strip(",.; ")
        if re.fullmatch(r"[A-Za-z]", note):
            footnotes.append(note)
        else:
            descriptions.append(note)

    note_text = "; ".join(descriptions)
    footnote_text = ", ".join(footnotes)

    core = re.sub(r"\s*\([^)]*\)", "", s)
    core = re.sub(r"\s*,\s*", " ", core).strip()
    core = core.rstrip(",.; ")

    # Symbol form: Ac-225, Tc-99m
    m = RADIONUCLIDE_SYMBOL_RE.match(core)
    if m:
        symbol = m.group(1)
        mass = m.group(2).zfill(3)
        suffix = m.group(3)
        formatted = f"{mass}{symbol}{suffix}"
        return formatted, note_text, footnote_text, core

    # Full name form: Actinium-225, Actinium 225
    m = RADIONUCLIDE_NAME_RE.match(core)
    if m:
        element_name = m.group(1).strip().lower()
        symbol = ELEMENT_NAME_TO_SYMBOL.get(element_name)
        if symbol:
            mass = m.group(2).zfill(3)
            suffix = m.group(3)
            formatted = f"{mass}{symbol}{suffix}"
            return formatted, note_text, footnote_text, core

    return s, note_text, footnote_text, core


def is_radionuclide_column(column_name: str) -> bool:
    name = str(column_name).lower()
    return (
        "symbol" in name
        or "radionuclide" in name
        or "chemical" in name
    )