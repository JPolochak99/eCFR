from __future__ import annotations

import streamlit as st

from cfr_exporter.ai_summary import render_ai_summary
from cfr_exporter.tableFunctions.table_formatter import format_df
from cfr_exporter.tableFunctions.table_to_data import table_html_to_df


def load_table(selected_item):
    selected_df = table_html_to_df(selected_item["html"])
    formatted_df, _ = format_df(selected_df)
    return selected_df, formatted_df


def render_table_preview(selected_item, formatted_df, selected_df, section, summary_key):
    st.markdown("### Table preview")

    preview_tab1, preview_tab2 = st.tabs(["Formatted preview", "Raw preview"])
    with preview_tab1:
        st.dataframe(formatted_df.head(15), width="stretch")
    with preview_tab2:
        st.dataframe(selected_df.head(15), width="stretch")

    render_ai_summary(
        selected_item=selected_item,
        formatted_df=formatted_df,
        section=section,
        summary_key=summary_key,
    )

    