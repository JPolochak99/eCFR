from __future__ import annotations

import re

import pandas as pd

SCI_HEADER_HINTS = (
    "tbq", "ci", "bq", "specific activity", "activity",
    "dose", "concentration", "energy", "mass", "half-life"
)

SCI_HEADER_BLOCKLIST = (
    "symbol", "note", "element", "name", "title", "footnote", "reference"
)

NUMERIC_RE = re.compile(
    r"""^\s*
    [+-]?
    (?:
        \d+(?:\.\d+)?      # 12 or 12.3
        |
        \.\d+              # .3
    )
    (?:\s*(?:e|×\s*10)\s*[+-]?\d+)?   # optional scientific part
    \s*$""",
    re.IGNORECASE | re.VERBOSE
)

def normalize_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip().replace("−", "-").replace("×", "x").replace("X", "x")

def looks_numericish(value):
    s = normalize_text(value)
    if not s:
        return False
    if s.lower() in {"unlimited"}:
        return False
    return bool(NUMERIC_RE.match(s))

def infer_scientific_columns(df, min_value_frac=0.6):
    candidates = []

    for col in df.columns:
        colname = str(col).lower()

        if any(bad in colname for bad in SCI_HEADER_BLOCKLIST):
            continue

        series = df[col].dropna().astype(str).str.strip()
        if series.empty:
            continue

        numeric_frac = series.map(looks_numericish).mean()
        header_hint = any(hint in colname for hint in SCI_HEADER_HINTS)

        if header_hint and numeric_frac >= 0.3:
            candidates.append(col)
            continue

        if numeric_frac >= min_value_frac:
            candidates.append(col)

    return candidates

def convert_scientific(value):
    if pd.isna(value):
        return value

    s = str(value).strip()

    if s == "" or s.lower() == "unlimited" or "see §" in s:
        return s

    s = s.replace("−", "-").replace("×", "x").replace("X", "x")
    s = re.sub(r"\s+", " ", s)

    m = re.match(r"^([0-9.]+)\s*x\s*10\s*([+-]?\d+)$", s)
    if m:
        mantissa = float(m.group(1))
        exponent = int(m.group(2))
        return mantissa * (10 ** exponent)

    try:
        return float(s)
    except Exception:
        return value