from __future__ import annotations

import streamlit as st

from cfr_exporter.clearWorkbookBtn import clearWorkbook
from cfr_exporter.date_utils import resolve_effective_date
from cfr_exporter.downloadBtn import downloadWorkbook
from cfr_exporter.session_state import init_state
from cfr_exporter.tableFunctions.table_actions import build_source_keys
from cfr_exporter.tableFunctions.table_finder import find_tables
from cfr_exporter.ui.renderTableActions import render_table_actions
from cfr_exporter.ui.ui_derived_sheet_builder import render_derived_sheet_builder
from cfr_exporter.ui.ui_empty_states import (
    render_no_tables_state,
    render_start_state,
)
from cfr_exporter.ui.ui_error_dialog import show_error_dialog
from cfr_exporter.ui.ui_renderSideBar import render_sidebar
from cfr_exporter.ui.ui_tablePreview import load_table, render_table_preview
from cfr_exporter.ui.ui_tableSelector import render_table_selector
from cfr_exporter.ui.ui_workbookContent import render_workbook_contents
from cfr_exporter.ui.renderAdvancedFormatting import render_advanced_formatting


def current_search_inputs(sidebar_inputs: dict) -> dict:
    return {
        "title": sidebar_inputs["title"],
        "subtitle": sidebar_inputs["subtitle"],
        "chapter": sidebar_inputs["chapter"],
        "subchapter": sidebar_inputs["subchapter"],
        "part": sidebar_inputs["part"],
        "subpart": sidebar_inputs["subpart"],
        "section": sidebar_inputs["section"],
    }


def search_inputs_match(sidebar_inputs: dict) -> bool:
    active = st.session_state.get("active_search", {})

    if not active:
        return False

    current = current_search_inputs(sidebar_inputs)

    return all(
        str(active.get(key, "")) == str(current.get(key, ""))
        for key in current
    )


st.title("CFR to Excel Export")
init_state()

if st.session_state.get("toast_message"):
    st.toast(st.session_state.toast_message, icon=st.session_state.toast_icon)
    st.session_state.toast_message = ""
    st.session_state.toast_icon = "✅"

sidebar_inputs = render_sidebar()

if sidebar_inputs["find_clicked"]:
    try:
        with st.spinner("Searching eCFR..."):
            effective_date_str = resolve_effective_date(
                sidebar_inputs["title"],
                sidebar_inputs["use_latest"],
                sidebar_inputs["custom_date"],
            )

            table_catalog = find_tables(
                sidebar_inputs["title"],
                sidebar_inputs["subtitle"],
                sidebar_inputs["chapter"],
                sidebar_inputs["subchapter"],
                sidebar_inputs["part"],
                sidebar_inputs["subpart"],
                sidebar_inputs["section"],
                effective_date_str,
            )

        st.session_state.effective_date_str = effective_date_str
        st.session_state.table_catalog = table_catalog
        st.session_state.active_search = {
            **current_search_inputs(sidebar_inputs),
            "effective_date_str": effective_date_str,
        }
        st.session_state.endpoint_error = ""

    except Exception as e:
        st.session_state.table_catalog = []
        st.session_state.endpoint_error = str(e)
        show_error_dialog(e)

catalog_matches_sidebar = search_inputs_match(sidebar_inputs)

if st.session_state.endpoint_error:
    st.error("Unable to load CFR data.")
elif sidebar_inputs["find_clicked"] and not st.session_state.table_catalog:
    render_no_tables_state()
elif not st.session_state.table_catalog:
    render_start_state()

st.subheader("Workbook")

st.session_state.workbook_name = st.text_input(
    "Workbook name",
    value=st.session_state.workbook_name,
    key="workbook_name_input",
    width="stretch",
)

if st.session_state.table_catalog:

    selected_item = render_table_selector(st.session_state.table_catalog)

    try:
        selected_df, formatted_df = load_table(selected_item)

        active_search = st.session_state.active_search

        formatted_source_key, raw_source_key = build_source_keys(
            title=active_search["title"],
            subtitle=active_search["subtitle"],
            chapter=active_search["chapter"],
            subchapter=active_search["subchapter"],
            part=active_search["part"],
            subpart=active_search["subpart"],
            section=active_search["section"],
            effective_date_str=active_search["effective_date_str"],
            table_index=selected_item["index"],
        )

        render_table_preview(
            selected_item=selected_item,
            formatted_df=formatted_df,
            selected_df=selected_df,
            section=active_search["section"],
            summary_key=formatted_source_key,
        )

        render_table_actions(
            selected_item=selected_item,
            formatted_df=formatted_df,
            selected_df=selected_df,
            title=active_search["title"],
            subtitle=active_search["subtitle"],
            chapter=active_search["chapter"],
            subchapter=active_search["subchapter"],
            part=active_search["part"],
            subpart=active_search["subpart"],
            section=active_search["section"],
            effective_date_str=active_search["effective_date_str"],
            controls_enabled=catalog_matches_sidebar,
        )

    except Exception as e:
        st.session_state.table_catalog = []
        show_error_dialog(e)

render_workbook_contents(st.session_state.workbook_tables)

if len(st.session_state.workbook_tables) >= 2:
    render_derived_sheet_builder()

render_advanced_formatting()

downloadWorkbook(sidebar_inputs)
clearWorkbook()
