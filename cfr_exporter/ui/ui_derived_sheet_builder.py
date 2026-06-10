from __future__ import annotations

import uuid

import streamlit as st

from cfr_exporter.derived_sheet_builder import DerivedLookupConfig, build_derived_sheet
from cfr_exporter.sanitize_names import sanitize_sheet_name
from cfr_exporter.toast_messages import queue_toast_and_rerun
from cfr_exporter.ui.ui_error_dialog import show_error_dialog


def _table_label(item: dict) -> str:
    return f"{item['sheet_name']} — {item['title']}"


def render_derived_sheet_builder():
    st.markdown("### Derived sheet builder")

    if not st.session_state.workbook_tables:
        st.info("Add at least one table to the workbook first.")
        return

    table_options = st.session_state.workbook_tables
    labels = [_table_label(item) for item in table_options]

    with st.expander("Create derived sheet", expanded=False):
        sheet_name = st.text_input("New sheet name", value="Derived Sheet")

        base_label = st.selectbox("Base table", labels)
        base_item = table_options[labels.index(base_label)]

        base_columns = st.multiselect(
            "Columns from base table",
            list(base_item["df"].columns),
            default=list(base_item["df"].columns)[:3],
        )

        use_lookup = st.checkbox("Join with another table", value=False)

        base_key = st.selectbox("Base key column", list(base_item["df"].columns))

        lookup_item = None
        lookup_key = None
        lookup_columns = []
        join_type = "left"

        if use_lookup:
            lookup_label = st.selectbox("Lookup table", labels)
            lookup_item = table_options[labels.index(lookup_label)]

            lookup_key = st.selectbox("Lookup key column", list(lookup_item["df"].columns))
            lookup_columns = st.multiselect(
                "Columns from lookup table",
                list(lookup_item["df"].columns),
                default=[c for c in list(lookup_item["df"].columns) if c != lookup_key][:2],
            )
            join_type = st.selectbox("Join type", ["left", "inner", "right"], index=0)

        if st.button("Create derived sheet"):
            try:
                config = DerivedLookupConfig(
                    sheet_name=sanitize_sheet_name(sheet_name),
                    base_table_id=base_item["id"],
                    lookup_table_id=lookup_item["id"] if lookup_item else None,
                    base_key_col=base_key,
                    lookup_key_col=lookup_key,
                    base_columns=base_columns,
                    lookup_columns=lookup_columns,
                    join_type=join_type,
                )

                derived_df = build_derived_sheet(st.session_state.workbook_tables, config)

                st.session_state.workbook_tables.append(
                    {
                        "id": str(uuid.uuid4()),
                        "source_key": f"derived:{config.sheet_name}",
                        "sheet_name": config.sheet_name,
                        "title": f"Derived: {config.sheet_name}",
                        "df": derived_df,
                    }
                )

                queue_toast_and_rerun(f"Created derived sheet '{config.sheet_name}'.", "✅")

            except Exception as e:
                show_error_dialog(e)