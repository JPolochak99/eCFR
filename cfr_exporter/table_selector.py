import streamlit as st

def get_filtered_catalog(catalog, table_filter_text: str):
    if not table_filter_text.strip():
        return catalog
    q = table_filter_text.strip().lower()
    return [item for item in catalog if q in str(item.get("title", "")).lower()]

def select_table(catalog, table_filter_text: str):
    filtered_catalog = get_filtered_catalog(catalog, table_filter_text)

    if not filtered_catalog:
        st.warning("No tables match that filter. Showing all tables instead.")
        filtered_catalog = catalog

    labels = [f"Table {item['index']}" for item in filtered_catalog]

    if len(labels) == 1:
        st.info("1 table found.")
        selected_index = 0
    else:
        st.warning(f"Multiple tables found: {len(labels)}")
        selected_label = st.selectbox("Available tables", labels)
        selected_index = labels.index(selected_label)

    selected_item = filtered_catalog[selected_index]

    if selected_item.get("title"):
        st.caption(selected_item["title"])

    return selected_item