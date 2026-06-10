from __future__ import annotations

import uuid

import streamlit as st

from cfr_exporter.derived_sheet_builder import (
    DerivedSheetConfig,
    LookupConfig,
    build_derived_sheet,
)
from cfr_exporter.sanitize_names import sanitize_sheet_name
from cfr_exporter.toast_messages import queue_toast_and_rerun
from cfr_exporter.ui.ui_error_dialog import show_error_dialog


def table_label(item: dict) -> str:
    return f"{item['sheet_name']} — {item['title']}"


def render_derived_sheet_builder() -> None:
    if len(st.session_state.workbook_tables) < 2:
        st.info("Add at least two tables to the workbook before creating a derived sheet.")
        return

    with st.expander("Create derived sheet", expanded=False):
        workbook_tables = st.session_state.workbook_tables
        labels = [table_label(item) for item in workbook_tables]

        sheet_name = st.text_input(
            "New derived sheet name",
            value="Derived Sheet",
        )

        base_label = st.selectbox("Base table", labels)
        base_item = workbook_tables[labels.index(base_label)]
        base_df = base_item["df"]

        base_key_column = st.selectbox(
            "Base key column",
            list(base_df.columns),
        )

        base_columns = st.multiselect(
            "Columns to keep from base table",
            list(base_df.columns),
            default=list(base_df.columns)[:5],
        )

        st.markdown("#### Lookup tables")

        lookup_count = st.number_input(
            "Number of lookup tables",
            min_value=1,
            max_value=5,
            value=1,
            step=1,
        )

        lookups: list[LookupConfig] = []

        for i in range(int(lookup_count)):
            st.markdown(f"##### Lookup table {i + 1}")

            lookup_label = st.selectbox(
                f"Lookup table {i + 1}",
                labels,
                key=f"lookup_table_{i}",
            )
            lookup_item = workbook_tables[labels.index(lookup_label)]
            lookup_df = lookup_item["df"]

            lookup_key_column = st.selectbox(
                f"Lookup key column {i + 1}",
                list(lookup_df.columns),
                key=f"lookup_key_{i}",
            )

            available_lookup_columns = [
                c for c in lookup_df.columns
                if c != lookup_key_column
            ]

            default_lookup_columns = available_lookup_columns[-3:]

            lookup_columns = st.multiselect(
                f"Columns to return from lookup table {i + 1}",
                available_lookup_columns,
                default=default_lookup_columns,
                key=f"lookup_columns_{i}",
            )

            lookups.append(
                LookupConfig(
                    table_id=lookup_item["id"],
                    key_column=lookup_key_column,
                    columns=lookup_columns,
                )
            )

        if st.button("Create derived sheet"):
            try:
                config = DerivedSheetConfig(
                    sheet_name=sanitize_sheet_name(sheet_name),
                    base_table_id=base_item["id"],
                    base_key_column=base_key_column,
                    base_columns=base_columns,
                    lookups=lookups,
                )

                derived_df = build_derived_sheet(
                    st.session_state.workbook_tables,
                    config,
                )

                st.session_state.workbook_tables.append(
                    {
                        "id": str(uuid.uuid4()),
                        "source_key": f"derived:{config.sheet_name}:{uuid.uuid4()}",
                        "sheet_name": config.sheet_name,
                        "title": f"Derived: {config.sheet_name}",
                        "df": derived_df,
                    }
                )

                queue_toast_and_rerun(
                    f"Created derived sheet '{config.sheet_name}'.",
                    "✅",
                )

            except Exception as e:
                show_error_dialog(e)