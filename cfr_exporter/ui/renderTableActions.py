from __future__ import annotations

import streamlit as st

from cfr_exporter.sanitize_names import sanitize_sheet_name
from cfr_exporter.tableFunctions.table_actions import (
    add_workbook_table,
    build_source_keys,
)
from cfr_exporter.toast_messages import queue_toast_and_rerun
from cfr_exporter.ui.ui_error_dialog import show_error_dialog


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
    controls_enabled: bool = True,
):
    if not controls_enabled:
        st.warning("Search inputs have changed. Click 'Find Tables' to refresh the current table.")

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

    sheet_name = _render_sheet_name_input(
        selected_item=selected_item,
        title=title,
        subtitle=subtitle,
        chapter=chapter,
        subchapter=subchapter,
        part=part,
        subpart=subpart,
        section=section,
        effective_date_str=effective_date_str,
    )

    add_col1, add_col2 = st.columns(2)

    with add_col1:
        _render_add_button(
            button_label="Add formatted table to workbook",
            source_key=formatted_source_key,
            sheet_name=sheet_name,
            title=selected_item.get("title") or f"Table {selected_item['index']}",
            df=formatted_df,
            mode="formatted",
            controls_enabled=controls_enabled,
        )

    with add_col2:
        _render_add_button(
            button_label="Add raw table to workbook",
            source_key=raw_source_key,
            sheet_name=sheet_name,
            title=selected_item.get("title") or f"Table {selected_item['index']}",
            df=selected_df,
            mode="raw",
            controls_enabled=controls_enabled,
        )


def _render_sheet_name_input(
    *,
    selected_item,
    title: str,
    subtitle: str,
    chapter: str,
    subchapter: str,
    part: str,
    subpart: str,
    section: str,
    effective_date_str: str,
) -> str:
    default_sheet_name = sanitize_sheet_name(f"{section}_T{selected_item['index']}")
    sheet_source_id = (
        f"{title}|{subtitle}|{chapter}|{subchapter}|"
        f"{part}|{subpart}|{section}|{effective_date_str}|{selected_item['index']}"
    )

    return st.text_input(
        "Sheet name for this table",
        value=default_sheet_name,
        key=f"sheet_name_{sheet_source_id}",
    )


def _render_add_button(
    *,
    button_label: str,
    source_key: str,
    sheet_name: str,
    title: str,
    df,
    mode: str,
    controls_enabled: bool,
):
    
    clicked = st.button(button_label, disabled=not controls_enabled)
    if not clicked:
        return

    try:
        safe_sheet_name = sanitize_sheet_name(sheet_name)

        added, message = add_workbook_table(
            workbook_tables=st.session_state.workbook_tables,
            source_key=source_key,
            sheet_name=safe_sheet_name,
            title=title,
            df=df,
            mode=mode,
        )

        icon = "✅" if added else "⚠️"
        queue_toast_and_rerun(message, icon)

    except Exception as e:
        show_error_dialog(e)