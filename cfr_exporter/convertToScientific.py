import re
import pandas as pd

def convert_scientific_columns_for_export(df, formatting: dict):
    df = df.copy()

    for col_name in formatting.get("scientific_cols", []):
        if col_name in df.columns:
            df[col_name] = df[col_name].apply(scientific_text_to_float)

    return df

def scientific_text_to_float(value):
    if pd.isna(value):
        return value

    s = str(value).strip()

    # Replace unicode minus
    s = s.replace("−", "-")

    # Replace multiplication forms
    s = re.sub(r"\s*[×x]\s*10\s*", "E", s)

    try:
        return float(s)
    except ValueError:
        return value