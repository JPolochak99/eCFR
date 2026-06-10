from __future__ import annotations

import streamlit as st


def render_start_state():
    st.markdown("### Ready to build a Workbook")
    st.info("Use the sidebar to choose a CFR title, part, section, and date, then click **Find Tables**.")


def render_no_tables_state():
    st.warning("No tables were found for this request.")
    st.write("Try a different section, date, or use the latest available eCFR date.")


def render_empty_workbook_state():
    st.caption("No tables have been added yet.")
    st.write("Find a table, choose a sheet name, and add it to your workbook.")