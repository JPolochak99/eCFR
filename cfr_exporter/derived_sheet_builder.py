from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class DerivedLookupConfig:
    sheet_name: str
    base_table_id: str
    lookup_table_id: str
    base_key_col: str
    lookup_key_col: str
    base_columns: list[str]
    lookup_columns: list[str]
    join_type: str = "left"


def get_table_df(workbook_tables: list[dict], table_id: str) -> pd.DataFrame:
    for item in workbook_tables:
        if item["id"] == table_id:
            return item["df"].copy()
    raise ValueError(f"Table with id '{table_id}' was not found.")


def _normalize_key(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


def build_derived_sheet(
    workbook_tables: list[dict],
    config: DerivedLookupConfig,
) -> pd.DataFrame:
    base_df = get_table_df(workbook_tables, config.base_table_id)
    lookup_df = get_table_df(workbook_tables, config.lookup_table_id)

    if config.base_key_col not in base_df.columns:
        raise ValueError(f"Base key column '{config.base_key_col}' was not found.")
    if config.lookup_key_col not in lookup_df.columns:
        raise ValueError(f"Lookup key column '{config.lookup_key_col}' was not found.")

    base_cols = [c for c in config.base_columns if c in base_df.columns]
    lookup_cols = [c for c in config.lookup_columns if c in lookup_df.columns]

    if config.base_key_col not in base_cols:
        base_cols = [config.base_key_col] + base_cols

    if not lookup_cols:
        raise ValueError("Select at least one lookup column.")

    base = base_df[base_cols].copy()
    lookup = lookup_df[[config.lookup_key_col, *lookup_cols]].copy()

    base["_join_key"] = _normalize_key(base_df[config.base_key_col])
    lookup["_join_key"] = _normalize_key(lookup_df[config.lookup_key_col])

    lookup = lookup.drop_duplicates(subset=["_join_key"], keep="first")

    result = base.merge(
        lookup.drop(columns=[config.lookup_key_col]),
        how=config.join_type,
        on="_join_key",
    )

    return result.drop(columns=["_join_key"])