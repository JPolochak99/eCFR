from __future__ import annotations

import streamlit as st

from cfr_exporter.toast_messages import queue_toast_and_rerun
from cfr_exporter.ui.ui_empty_states import render_empty_workbook_state
from cfr_exporter.ui.moveSheet import move_sheet
from cfr_exporter.sanitize_names import sanitize_sheet_name

def render_workbook_contents(workbook_tables):
    st.markdown("### Workbook Contents")

    if not workbook_tables:
        render_empty_workbook_state()
        return

    for i, item in enumerate(workbook_tables):
        mode = item.get("mode", "sheet")
        df = item.get("df")
        row_count = len(df) if df is not None else 0
        col_count = len(df.columns) if df is not None else 0

        edit_key = f"editing_{item['id']}"

        with st.container(border=True):
            top_cols = st.columns([9, 1])

            with top_cols[0]:
                st.markdown(f"#### {i + 1}. {item['sheet_name']}")

            with top_cols[1]:
                if st.button("edit", key=f"edit_{item['id']}"):
                    st.session_state[edit_key] = not st.session_state.get(edit_key, False)
                    st.rerun()


            if st.session_state.get(edit_key, False):
                new_name = st.text_input(
                    "Edit sheet name",
                    value=item["sheet_name"],
                    key=f"rename_{item['id']}",
                )

                save_col, cancel_col = st.columns([1, 5])

                with save_col:
                    if st.button("Save", key=f"save_rename_{item['id']}"):
                        item["sheet_name"] = sanitize_sheet_name(new_name)
                        st.session_state[edit_key] = False
                        queue_toast_and_rerun(
                            f"Renamed sheet to '{item['sheet_name']}'.",
                            "✅",
                        )

                with cancel_col:
                    if st.button("Cancel", key=f"cancel_rename_{item['id']}"):
                        st.session_state[edit_key] = False
                        st.rerun()
                        
            # card body here
            st.write(f"**Type:** {mode}")
            st.write(f"**Size:** {row_count} rows × {col_count} columns")

            bottom_cols = st.columns([5, .5, .5, 1])

            with bottom_cols[1]:
                if st.button("↑", key=f"up_{item['id']}", disabled=(i == 0)):
                    move_sheet(st.session_state.workbook_tables, i, i - 1)
                    queue_toast_and_rerun(f"Moved '{item['sheet_name']}' up.", "✅")

            with bottom_cols[2]:
                if st.button("↓", key=f"down_{item['id']}", disabled=(i == len(workbook_tables) - 1)):
                    move_sheet(st.session_state.workbook_tables, i, i + 1)
                    queue_toast_and_rerun(f"Moved '{item['sheet_name']}' down.", "✅")

            with bottom_cols[3]:
                if st.button("Remove", key=f"remove_{item['id']}"):
                    st.session_state.workbook_tables = [
                        x for x in st.session_state.workbook_tables
                        if x["id"] != item["id"]
                    ]
                    queue_toast_and_rerun(
                        f"Removed '{item['sheet_name']}' from workbook.",
                        "🗑️",
                    )