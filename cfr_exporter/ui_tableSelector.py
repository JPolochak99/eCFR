from __future__ import annotations

import streamlit as st



def render_table_selector(catalog):
    

    labels = [f"Table {item['index']}" for item in catalog]

    if len(labels) == 1:
        st.info("1 table found.")
        selected_index = 0
    else:
        st.warning(f"Multiple tables found: {len(labels)}")
        selected_label = st.selectbox("Available tables", labels)
        selected_index = labels.index(selected_label)

    selected_item = catalog[selected_index]

    if selected_item.get("title"):
        st.caption(selected_item["title"])

    return selected_item