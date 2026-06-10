from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class LookupConfig:
    table_id: str
    key_column: str
    columns: list[str]


@dataclass
class DerivedSheetConfig:
    sheet_name: str
    base_table_id: str
    base_key_column: str
    base_columns: list[str]
    lookups: list[LookupConfig]


def get_table_by_id(workbook_tables: list[dict], table_id: str) -> dict:
    for item in workbook_tables:
        if item["id"] == table_id:
            return item
    raise ValueError(f"Table with id '{table_id}' was not found.")


def normalize_join_key(series: pd.Series) -> pd.Series:
    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )


def build_derived_sheet(
    workbook_tables: list[dict],
    config: DerivedSheetConfig,
) -> pd.DataFrame:
    base_item = get_table_by_id(workbook_tables, config.base_table_id)
    base_df = base_item["df"].copy()

    if config.base_key_column not in base_df.columns:
        raise ValueError(f"Base key column '{config.base_key_column}' was not found.")

    base_cols = [c for c in config.base_columns if c in base_df.columns]

    if config.base_key_column not in base_cols:
        base_cols = [config.base_key_column] + base_cols

    result = base_df[base_cols].copy()
    result["_join_key"] = normalize_join_key(base_df[config.base_key_column])

    for i, lookup_config in enumerate(config.lookups, start=1):
        lookup_item = get_table_by_id(workbook_tables, lookup_config.table_id)
        lookup_df = lookup_item["df"].copy()

        if lookup_config.key_column not in lookup_df.columns:
            raise ValueError(
                f"Lookup key column '{lookup_config.key_column}' was not found."
            )

        lookup_cols = [
            c for c in lookup_config.columns
            if c in lookup_df.columns and c != lookup_config.key_column
        ]

        if not lookup_cols:
            continue

        lookup_subset = lookup_df[[lookup_config.key_column] + lookup_cols].copy()
        lookup_subset["_join_key"] = normalize_join_key(
            lookup_df[lookup_config.key_column]
        )

        lookup_subset = lookup_subset.drop_duplicates(
            subset=["_join_key"],
            keep="first",
        )

        rename_map = {}
        for col in lookup_cols:
            if col in result.columns:
                rename_map[col] = f"{col}_lookup_{i}"

        lookup_subset = lookup_subset.rename(columns=rename_map)

        result = result.merge(
            lookup_subset.drop(columns=[lookup_config.key_column]),
            how="left",
            on="_join_key",
        )

    return result.drop(columns=["_join_key"])