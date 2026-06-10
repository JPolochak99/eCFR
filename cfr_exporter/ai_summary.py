from __future__ import annotations

import streamlit as st

from cfr_exporter.ai_helpers import summarize_table
from cfr_exporter.toast_messages import queue_toast
from cfr_exporter.ai_helpers import summarize_table, generate_basic_summary
from cfr_exporter.ui.ui_error_dialog import show_error_dialog


def render_ai_summary(selected_item, formatted_df, section: str, summary_key: str):
    current_summary = st.session_state.ai_summaries.get(summary_key)

    with st.expander("AI summary", expanded=False):
        if current_summary:
            st.markdown(current_summary["summary"])

            st.markdown("**Suggested sheet name**")
            st.write(current_summary["suggested_sheet_name"])

            if current_summary.get("key_columns"):
                st.markdown("**Key columns**")
                for col in current_summary["key_columns"]:
                    st.write(f"• {col}")

            if current_summary.get("notes"):
                st.markdown("**Notes**")
                for note in current_summary["notes"]:
                    st.write(f"• {note}")

        if st.button("Generate summary", key=f"ai_summary_btn_{selected_item['index']}"):
            try:
                with st.spinner("Generating AI summary..."):
                    try:
                        summary = summarize_table(
                            formatted_df,
                            table_title=selected_item.get("title") or f"Table {selected_item['index']}",
                            section=section,
                        )
                    except:
                        summary = generate_basic_summary(formatted_df)

                st.session_state.ai_summaries[summary_key] = summary
                queue_toast("AI summary ready.", "✅")
                st.rerun()

            except Exception as e:
                show_error_dialog(e)

        if not current_summary:
            st.info("Click **Generate summary** to see a plain-English explanation of this table.")