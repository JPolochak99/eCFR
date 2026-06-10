from __future__ import annotations

import uuid

import streamlit as st

from cfr_exporter.tableFunctions.table_to_data import table_html_to_df
from cfr_exporter.tableFunctions.table_formatter import format_df
from cfr_exporter.workbookContentBuilders.workbook_builder import (
    make_source_key,
    workbook_has_table,
)
from cfr_exporter.sanitize_names import sanitize_sheet_name

from cfr_exporter.ui.ui_error_dialog import show_error_dialog
from cfr_exporter.toast_messages import queue_toast
from cfr_exporter.ai_summary import render_ai_summary

def render_table_preview_and_actions(
    selected_item,
    title: str,
    subtitle: str,
    chapter: str,
    subchapter: str,
    part: str,
    subpart: str,
    section: str,
    effective_date_str: str,
):
    selected_df = table_html_to_df(selected_item["html"])
    formatted_df, _ = format_df(selected_df)

    formatted_source_key = make_source_key(
        title=title,
        subtitle=subtitle,
        chapter=chapter,
        subchapter=subchapter,
        part=part,
        subpart=subpart,
        section=section,
        effective_date_str=effective_date_str,
        table_index=selected_item["index"],
        mode="formatted",
    )

    render_ai_summary(
        selected_item=selected_item,
        formatted_df=formatted_df,
        section=section,
        summary_key=formatted_source_key,
    )

    st.markdown("### Add selected table to workbook")

    default_sheet_name = sanitize_sheet_name(f"{section}_T{selected_item['index']}")
    sheet_source_id = (
        f"{title}|{subtitle}|{chapter}|{subchapter}|"
        f"{part}|{subpart}|{section}|{effective_date_str}|{selected_item['index']}"
    )

    sheet_widget_key = f"sheet_name_{sheet_source_id}"

    sheet_name = st.text_input(
        "Sheet name for this table",
        value=default_sheet_name,
        key=sheet_widget_key,
    )

    preview_tab1, preview_tab2 = st.tabs(["Formatted preview", "Raw preview"])
    with preview_tab1:
        st.dataframe(formatted_df.head(15), width="stretch")
    with preview_tab2:
        st.dataframe(selected_df.head(15), width="stretch")

    add_col1, add_col2 = st.columns(2)

    

    raw_source_key = make_source_key(
        title=title,
        subtitle=subtitle,
        chapter=chapter,
        subchapter=subchapter,
        part=part,
        subpart=subpart,
        section=section,
        effective_date_str=effective_date_str,
        table_index=selected_item["index"],
        mode="raw",
    )

    with add_col1:
        if st.button("Add formatted table to workbook"):
            try:
                if workbook_has_table(st.session_state.workbook_tables, formatted_source_key):
                    queue_toast("That formatted table is already in the workbook.", "⚠️")
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
                    queue_toast(f"Added '{safe_sheet_name}' to workbook.", "✅") 
                
                st.rerun()

            except Exception as e:
                show_error_dialog(e)
    with add_col2:
        if st.button("Add raw table to workbook"):
            try:
                if workbook_has_table(st.session_state.workbook_tables, raw_source_key):
                    queue_toast("That raw table is already in the workbook.", "⚠️")
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
                    queue_toast(f"Added '{safe_sheet_name}' to workbook.", "✅")
                st.rerun()
            except Exception as e:
                show_error_dialog(e)

    