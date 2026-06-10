from __future__ import annotations

import uuid

import streamlit as st

from cfr_exporter.sanitize_names import sanitize_sheet_name
from cfr_exporter.toast_messages import queue_toast_and_rerun
from cfr_exporter.workbookContentBuilders.workbook_builder import (
    make_source_key,
    workbook_has_table,
)
from cfr_exporter.ui.ui_error_dialog import show_error_dialog


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
):
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


def render_table_actions(
    selected_item,
    formatted_df,
    selected_df,
    title: str,
    subtitle: str,
    chapter: str,
    subchapter: str,
    part: str,
    subpart: str,
    section: str,
    effective_date_str: str,
):
    st.markdown("### Add selected table to workbook")

    formatted_source_key, raw_source_key = build_source_keys(
        title=title,
        subtitle=subtitle,
        chapter=chapter,
        subchapter=subchapter,
        part=part,
        subpart=subpart,
        section=section,
        effective_date_str=effective_date_str,
        table_index=selected_item["index"],
    )

    default_sheet_name = sanitize_sheet_name(f"{section}_T{selected_item['index']}")
    sheet_source_id = (
        f"{title}|{subtitle}|{chapter}|{subchapter}|"
        f"{part}|{subpart}|{section}|{effective_date_str}|{selected_item['index']}"
    )

    sheet_name = st.text_input(
        "Sheet name for this table",
        value=default_sheet_name,
        key=f"sheet_name_{sheet_source_id}",
    )

    add_col1, add_col2 = st.columns(2)

    with add_col1:
        if st.button("Add formatted table to workbook"):
            try:
                if workbook_has_table(st.session_state.workbook_tables, formatted_source_key):
                    queue_toast_and_rerun("That formatted table is already in the workbook.", "⚠️")
                else:
                    safe_sheet_name = sanitize_sheet_name(sheet_name)
                    st.session_state.workbook_tables.append(
                        {
                            "id": str(uuid.uuid4()),
                            "source_key": formatted_source_key,
                            "sheet_name": safe_sheet_name,
                            "title": selected_item.get("title") or f"Table {selected_item['index']}",
                            "df": formatted_df,
                        }
                    )
                    queue_toast_and_rerun(f"Added '{safe_sheet_name}' to workbook.", "✅")
            except Exception as e:
                show_error_dialog(e)

    with add_col2:
        if st.button("Add raw table to workbook"):
            try:
                if workbook_has_table(st.session_state.workbook_tables, raw_source_key):
                    queue_toast_and_rerun("That raw table is already in the workbook.", "⚠️")
                else:
                    safe_sheet_name = sanitize_sheet_name(sheet_name)
                    st.session_state.workbook_tables.append(
                        {
                            "id": str(uuid.uuid4()),
                            "source_key": raw_source_key,
                            "sheet_name": safe_sheet_name,
                            "title": selected_item.get("title") or f"Table {selected_item['index']}",
                            "df": selected_df,
                        }
                    )
                    queue_toast_and_rerun(f"Added '{safe_sheet_name}' to workbook.", "✅")
            except Exception as e:
                show_error_dialog(e)