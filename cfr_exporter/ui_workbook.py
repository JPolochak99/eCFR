from __future__ import annotations

import streamlit as st


def render_workbook_contents(workbook_tables):
    st.markdown("### Workbook contents")

    if not workbook_tables:
        st.caption("No tables have been added yet.")
        return

    for i, item in enumerate(workbook_tables, start=1):
        cols = st.columns([4, 1])
        cols[0].write(f"{i}. {item['sheet_name']} — {item['title']}")

        if cols[1].button("Remove", key=f"remove_{item['id']}"):
            st.session_state.workbook_tables = [
                x for x in st.session_state.workbook_tables
                if x["id"] != item["id"]
            ]
            st.rerun()

    clear_col1, _ = st.columns([1, 3])
    with clear_col1:
        if st.button("Clear workbook"):
            st.session_state.workbook_tables = []
            st.rerun()