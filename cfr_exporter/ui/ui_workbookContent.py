from __future__ import annotations

import streamlit as st
from cfr_exporter.toast_messages import queue_toast_and_rerun
from cfr_exporter.ui.ui_empty_states import render_empty_workbook_state
from .moveSheet import move_item


def render_workbook_contents(workbook_tables):
    st.markdown("### Workbook Contents")

    if not workbook_tables:
        render_empty_workbook_state()
        return
    
    for i, item in enumerate(workbook_tables):
        cols = st.columns([5, 1, 1, 1])

        cols[0].write(f"{i+1}. {item['sheet_name']} — {item['title']}")
        
        #move up 
        if cols[1].button("↑", key=f"up_{item['id']}", disabled=(i == 0)):
            move_item(st.session_state.workbook_tables, i, i - 1)
            queue_toast_and_rerun(f"Moved '{item['sheet_name']}' up.", "✅")

        #move down
        if cols[2].button("↓", key=f"down_{item['id']}", disabled=(i == (len(workbook_tables)) - 1)):
            move_item(st.session_state.workbook_tables, i, i + 1)
            queue_toast_and_rerun(f"Moved '{item['sheet_name']}' down.", "✅")
        

        if cols[3].button("Remove", key=f"remove_{item['id']}"):
            st.session_state.workbook_tables = [
                x for x in st.session_state.workbook_tables
                if x["id"] != item["id"]
            ]
            queue_toast_and_rerun(f"Removed '{item['sheet_name']}' from workbook.", "✅")
            
    

