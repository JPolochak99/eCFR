from __future__ import annotations

import streamlit as st

from cfr_exporter.ecfr_client import fetch_page
from cfr_exporter.excel_writer import df_to_excel_bytes
from cfr_exporter.table_catalog import build_table_catalog
from cfr_exporter.table_parser import format_df, table_html_to_df
from cfr_exporter.ecfr_client import get_latest_available_date
import datetime



st.title("CFR to Excel Export")

# Inputs
with st.sidebar:
    st.header("CFR target")
    title = st.text_input("Title", "49")
    subtitle = st.text_input("Subtitle", "B")
    chapter = st.text_input("Chapter", "I")
    subchapter = st.text_input("Subchapter", "C")
    part = st.text_input("Part", "173")
    subpart = st.text_input("Subpart", "I")
    section = st.text_input("Section", "173.435")
    use_latest = st.checkbox("Use latest available eCFR date", value=True)
    if not use_latest:
        date = st.date_input(
            "Custom eCFR date",
            value=datetime.date.today()
        )

    st.header("Table selection")
    table_filter = st.text_input("Optional table filter", "")



if use_latest:
    try:
        effective_date_str = get_latest_available_date(title)
        st.caption(f"Using latest available date for Title {title}: {effective_date_str}")
    except Exception as e:
        st.error(f"Could not determine latest date: {e}")
        effective_date_str = date.isoformat()
else:
    effective_date_str = date.isoformat()


# Session state
if "table_catalog" not in st.session_state:
    st.session_state.table_catalog = []
if "endpoint_found" not in st.session_state:
    st.session_state.endpoint_found = False
if "endpoint_error" not in st.session_state:
    st.session_state.endpoint_error = ""



def get_filtered_catalog(catalog, table_filter_text: str):
    if not table_filter_text.strip():
        return catalog
    q = table_filter_text.strip().lower()
    return [item for item in catalog if q in item["title"].lower()]


# Actions
if st.button("Find Tables"):
    try:
        xml_text = fetch_page(title, subtitle, chapter, subchapter, part, subpart, section, effective_date_str)
        catalog = build_table_catalog(xml_text)
        st.session_state.table_catalog = catalog
        st.session_state.endpoint_found = True
        st.session_state.endpoint_error = ""
    except Exception as e:
        st.session_state.table_catalog = []
        st.session_state.endpoint_found = False
        st.session_state.endpoint_error = str(e)
        st.error(f"Failed to find tables: {e}")

if st.session_state.endpoint_error:
    st.info(st.session_state.endpoint_error)

# Table selection + download
if st.session_state.endpoint_found and st.session_state.table_catalog:
    filtered_catalog = get_filtered_catalog(st.session_state.table_catalog, table_filter)

    if not filtered_catalog:
        st.warning("No tables match that filter. Showing all tables instead.")
        filtered_catalog = st.session_state.table_catalog

    labels = [item["label"] for item in filtered_catalog]

    if len(labels) == 1:
        st.info("1 table found.")
        selected_index = 0
    else:
        st.warning(f"Multiple tables found: {len(labels)}")
        selected_label = st.selectbox("Available tables", labels)
        selected_index = labels.index(selected_label)

    selected_item = filtered_catalog[selected_index]

    if selected_item["title"]:
        st.caption(selected_item["title"])

    try:
        selected_df = table_html_to_df(selected_item["html"])
        formatted_df, numeric_cols = format_df(selected_df)

        col1, col2 = st.columns(2)

        with col1:
            formatted_bytes = df_to_excel_bytes(
                formatted_df,
                sheet_name="CFR",
                styled=True,
                numeric_cols=numeric_cols,
            )
            st.download_button(
                "Download Formatted Excel",
                formatted_bytes,
                file_name=f"section_{section.replace('.', '_')}_formatted.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        with col2:
            raw_bytes = df_to_excel_bytes(
                selected_df,
                sheet_name="CFR",
                styled=False,
                numeric_cols=None,
            )
            st.download_button(
                "Download Raw Excel",
                raw_bytes,
                file_name=f"section_{section.replace('.', '_')}_raw.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    except Exception as e:
        st.error(f"Could not prepare selected table: {e}")