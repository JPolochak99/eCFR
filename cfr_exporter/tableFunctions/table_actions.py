from __future__ import annotations

import uuid

import streamlit as st

from cfr_exporter.workbookContentBuilders.workbook_builder import (
    make_source_key,
    workbook_has_table,
)


def build_source_keys(
    *,
    title: str,
    subtitle: str,
    chapter: str,
    subchapter: str,
    part: str,
    subpart: str,
    section: str,
    effective_date_str: str,
    table_index: int,
) -> tuple[str, str]:
    formatted_source_key = make_source_key(
        title=title,
        subtitle=subtitle,
        chapter=chapter,
        subchapter=subchapter,
        part=part,
        subpart=subpart,
        section=section,
        effective_date_str=effective_date_str,
        table_index=table_index,
        mode="formatted",
    )

    raw_source_key = make_source_key(
        title=title,
        subtitle=subtitle,
        chapter=chapter,
        subchapter=subchapter,
        part=part,
        subpart=subpart,
        section=section,
        effective_date_str=effective_date_str,
        table_index=table_index,
        mode="raw",
    )

    return formatted_source_key, raw_source_key


def add_workbook_table(
    *,
    workbook_tables: list[dict],
    source_key: str,
    sheet_name: str,
    title: str,
    df,
    mode: str,
) -> tuple[bool, str]:
    if workbook_has_table(workbook_tables, source_key):
        return False, f"That {mode} table is already in the workbook."

    workbook_tables.append(
        {
            "id": str(uuid.uuid4()),
            "source_key": source_key,
            "sheet_name": sheet_name,
            "title": title,
            "df": df,
            "mode": mode,
        }
    )

    return True, f"Added '{sheet_name}' to workbook."