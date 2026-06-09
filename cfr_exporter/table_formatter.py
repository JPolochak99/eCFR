from __future__ import annotations
from .radionuclides import is_radionuclide_column, parse_radionuclide
import pandas as pd

def format_df(df: pd.DataFrame):
    """Apply radionuclide parsing only."""
    for col in df.columns:
        if is_radionuclide_column(col):
            parsed = df[col].apply(parse_radionuclide).apply(pd.Series)
            parsed.columns = [col, "Symbol note", "Symbol footnotes", "Symbol core"]

            df = df.drop(columns=[col]).join(parsed)

            first_cols = [col, "Symbol note", "Symbol footnotes", "Symbol core"]
            other_cols = [c for c in df.columns if c not in first_cols]
            df = df[first_cols + other_cols]
            break

    return df, []
