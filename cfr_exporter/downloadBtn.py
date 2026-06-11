import streamlit as st

from cfr_exporter.sanitize_names import sanitize_filename
from cfr_exporter.workbookContentBuilders.workbook_builder import build_workbook_bytes


def downloadWorkbook(sidebar_inputs):
    if not st.session_state.workbook_tables:
        return

    workbook_bytes = build_workbook_bytes(
        st.session_state.workbook_tables,
        metadata={
            "workbook_name": st.session_state.workbook_name,
            "title": sidebar_inputs["title"],
            "subtitle": sidebar_inputs["subtitle"],
            "chapter": sidebar_inputs["chapter"],
            "subchapter": sidebar_inputs["subchapter"],
            "part": sidebar_inputs["part"],
            "subpart": sidebar_inputs["subpart"],
            "section": sidebar_inputs["section"],
            "effective_date_str": st.session_state.effective_date_str,
        },
    )

    final_workbook_name = sanitize_filename(st.session_state.workbook_name) + ".xlsx"

    st.download_button(
        "Download workbook",
        workbook_bytes,
        file_name=final_workbook_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )