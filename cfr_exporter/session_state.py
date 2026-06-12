from __future__ import annotations

import streamlit as st


def init_state() -> None:
    defaults = {
        "app_loaded": False,
        "table_catalog": [],
        "endpoint_found": False,
        "endpoint_error": "",
        "workbook_tables": [],
        "effective_date_str": "",
        "workbook_name": "CFR Export Workbook",
        "sheet_name_source": "",
        "sheet_name_value": "",
        "toast_message": "",
        "toast_icon": "✅",
        "ai_summaries": {},
        "derived_sheets": [],
        "show_derived_builder": False,
        "active_search": {},
        "formatting": {"scientific_cols": []}, 
    }
    


    for key, value in defaults.items():
        st.session_state.setdefault(key, value)