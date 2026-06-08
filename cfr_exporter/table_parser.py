from __future__ import annotations

import re

import pandas as pd
from bs4 import BeautifulSoup
from .convertToScientific import convert_scientific, infer_scientific_columns

def parse_radionuclide(value):
    """Convert 'Ac-225 (a)' -> ('225Ac', 'a', 'Ac-225') etc."""
    if pd.isna(value):
        return value, "", ""

    s = str(value).strip()
    notes = re.findall(r"\(([^)]*)\)", s)
    note_text = "; ".join(n.strip() for n in notes if n.strip())
    core = re.sub(r"\s*\([^)]*\)", "", s).strip()

    m = re.match(r"^([A-Za-z]+)-(\d+)([A-Za-z]*)$", core)
    if not m:
        return s, note_text, core

    symbol = m.group(1)
    mass = m.group(2).zfill(3)
    suffix = m.group(3)
    formatted = f"{mass}{symbol}{suffix}"
    return formatted, note_text, core



def table_html_to_df(table_html: str) -> pd.DataFrame:
    """Parse one eCFR table into a DataFrame without assuming a fixed schema."""
    soup = BeautifulSoup(table_html, "xml")
    table = soup.find("TABLE") or soup.find("table")
    if table is None:
        raise ValueError("Could not parse selected table.")

    body = table.find("TBODY")
    tr_source = body.find_all("TR") if body else table.find_all("TR")

    rows = []
    for tr in tr_source:
        cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["TD", "TH"])]
        if cells:
            rows.append(cells)

    if not rows:
        raise ValueError("No rows found in the selected table.")

    headers = None
    thead = table.find("THEAD")
    if thead:
        header_tr = thead.find("TR")
        if header_tr:
            headers = [cell.get_text(" ", strip=True) for cell in header_tr.find_all(["TH", "TD"])]

    if headers is None:
        for tr in tr_source:
            if tr.find_all("TH"):
                headers = [cell.get_text(" ", strip=True) for cell in tr.find_all(["TH", "TD"])]
                break

    max_cols = max(len(r) for r in rows)
    rows = [r + [""] * (max_cols - len(r)) for r in rows]

    if headers:
        headers = [h if h else f"Column {i}" for i, h in enumerate(headers, start=1)]
        headers = headers + [f"Column {i}" for i in range(len(headers) + 1, max_cols + 1)]

        if rows and len(rows[0]) == len(headers[:len(rows[0])]):
            first_row = [str(x).strip() for x in rows[0]]
            header_row = [str(x).strip() for x in headers[:len(first_row)]]
            if first_row == header_row:
                rows = rows[1:]

    return pd.DataFrame(rows, columns=headers[:max_cols])


def format_df(df: pd.DataFrame):
    """Apply radionuclide parsing and numeric conversion heuristics."""
    scientific_cols = []

    # Reformat likely radionuclide columns only when present.
    for col in df.columns:
        col_lower = str(col).lower()
        if "symbol" in col_lower and "radionuclide" in col_lower:
            parsed = df[col].apply(parse_radionuclide).apply(pd.Series)
            parsed.columns = [col, "Symbol note", "Symbol core"]

            df = df.drop(columns=[col]).join(parsed)

            first_cols = [col, "Symbol note", "Symbol core"]
            other_cols = [c for c in df.columns if c not in first_cols]
            df = df[first_cols + other_cols]
            break

    # Infer and convert scientific columns
    scientific_cols = infer_scientific_columns(df)

    for col in scientific_cols:
        if col in df.columns:
            df[col] = df[col].apply(convert_scientific)

    return df, scientific_cols