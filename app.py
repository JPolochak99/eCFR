from __future__ import annotations

import streamlit as st

from cfr_exporter.date_utils import resolve_effective_date
from cfr_exporter.session_state import init_state
from cfr_exporter.table_finder import find_tables
from cfr_exporter.ui_renderSideBar import render_sidebar
from cfr_exporter.ui_tablePreview import render_table_preview_and_actions
from cfr_exporter.ui_tableSelector import render_table_selector
from cfr_exporter.ui_workbook import render_workbook_contents
from cfr_exporter.workbook_builder import build_workbook_bytes
from cfr_exporter.sanitize_names import sanitize_filename

st.title("CFR to Excel Export")

init_state()
sidebar_inputs = render_sidebar()

if sidebar_inputs["find_clicked"]:
    try:
        effective_date_str = resolve_effective_date(
            sidebar_inputs["title"],
            sidebar_inputs["use_latest"],
            sidebar_inputs["custom_date"],
        )
        st.session_state.effective_date_str = effective_date_str
        st.session_state.table_catalog = find_tables(
            sidebar_inputs["title"],
            sidebar_inputs["subtitle"],
            sidebar_inputs["chapter"],
            sidebar_inputs["subchapter"],
            sidebar_inputs["part"],
            sidebar_inputs["subpart"],
            sidebar_inputs["section"],
            effective_date_str,
        )
        st.session_state.endpoint_error = ""
    except Exception as e:
        st.session_state.table_catalog = []
        st.session_state.endpoint_error = str(e)

if st.session_state.endpoint_error:
    st.error(st.session_state.endpoint_error)

left, center, right = st.columns([1, 1, 1])

st.subheader("Workbook")

st.session_state.workbook_name = st.text_input(
    "Workbook name",
    value=st.session_state.workbook_name,
    key="workbook_name_input",
    width="stretch",
)

if st.session_state.table_catalog:
    selected_item = render_table_selector(
        st.session_state.table_catalog,
    )

    try:
        render_table_preview_and_actions(
            selected_item=selected_item,
            title=sidebar_inputs["title"],
            subtitle=sidebar_inputs["subtitle"],
            chapter=sidebar_inputs["chapter"],
            subchapter=sidebar_inputs["subchapter"],
            part=sidebar_inputs["part"],
            subpart=sidebar_inputs["subpart"],
            section=sidebar_inputs["section"],
            effective_date_str=st.session_state.effective_date_str,
        )
    except Exception as e:
        st.session_state.table_catalog = []
        st.error(f"Could not prepare selected table: {e}")

render_workbook_contents(st.session_state.workbook_tables)

if st.session_state.workbook_tables:
    workbook_bytes = build_workbook_bytes(st.session_state.workbook_tables)
    final_workbook_name = sanitize_filename(st.session_state.workbook_name) + ".xlsx"

    st.download_button(
        "Download workbook",
        workbook_bytes,
        file_name=final_workbook_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )