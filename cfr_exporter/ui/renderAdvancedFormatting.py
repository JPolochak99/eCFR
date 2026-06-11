from __future__ import annotations

import streamlit as st

from cfr_exporter.toast_messages import queue_toast_and_rerun


def _sheet_label(item: dict) -> str:
    return f"{item['sheet_name']} — {item.get('mode', 'sheet')}"


def render_advanced_formatting():
    if not st.session_state.workbook_tables:
        return

    with st.expander("Advanced Formatting", expanded=False):
        st.write("Choose workbook sheets and columns to format in Excel.")

        sheet_options = st.session_state.workbook_tables
        sheet_labels = [_sheet_label(item) for item in sheet_options]

        selected_labels = st.multiselect(
            "Sheets to format",
            sheet_labels,
            default=[],
            placeholder="Select one or more sheets",
        )

        if not selected_labels:
            st.info("Select at least one sheet to continue.")
            return

        format_option = st.selectbox(
            "Format option",
            [
                "Scientific notation",
                "Number with 2 decimals",
                "Percent",
            ],
        )

        for label in selected_labels:
            item = sheet_options[sheet_labels.index(label)]
            df = item["df"]

            selected_columns = st.multiselect(
                f"Columns for {item['sheet_name']}",
                list(df.columns),
                default=[],
                key=f"format_cols_{item['id']}_{format_option}",
                placeholder="Select columns",
            )

            if st.button(
                f"Apply formatting to {item['sheet_name']}",
                key=f"apply_format_{item['id']}_{format_option}",
            ):
                item.setdefault("formatting", {})

                if format_option == "Scientific notation":
                    item["formatting"]["scientific_cols"] = selected_columns

                elif format_option == "Number with 2 decimals":
                    item["formatting"]["number_2_decimal_cols"] = selected_columns

                elif format_option == "Percent":
                    item["formatting"]["percent_cols"] = selected_columns

                queue_toast_and_rerun(
                    f"Applied formatting to '{item['sheet_name']}'.",
                    "✅",
                )