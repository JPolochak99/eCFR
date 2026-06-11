import streamlit as st

from cfr_exporter.toast_messages import queue_toast_and_rerun

def clearWorkbook():
    if not st.session_state.workbook_tables:
        return

    if st.button("Clear Workbook"):
        st.session_state.workbook_tables = []
        queue_toast_and_rerun("Cleared all tables from workbook.", "✅")