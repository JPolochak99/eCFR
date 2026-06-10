from __future__ import annotations

import json
from typing import Any

import pandas as pd
import streamlit as st
from openai import OpenAI

TABLE_SUMMARY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
            "description": "Plain-English summary of what the table contains.",
        },
        "key_columns": {
            "type": "array",
            "items": {"type": "string"},
            "description": "The most important columns in the table.",
        },
        "suggested_sheet_name": {
            "type": "string",
            "description": "Short workbook-friendly sheet name.",
        },
        "notes": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Important caveats, footnotes, or unusual formatting notes.",
        },
    },
    "required": ["summary", "key_columns", "suggested_sheet_name", "notes"],
    "additionalProperties": False,
}


def summarize_table(
    df: pd.DataFrame,
    *,
    table_title: str,
    section: str,
    model: str = "gpt-4.1-mini",
) -> dict[str, Any]:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    preview_csv = df.head(25).fillna("").to_csv(index=False)

    prompt = f"""
You are helping a user understand a CFR table.

Return JSON only.
Use short, practical language.

Table title: {table_title}
CFR section: {section}

Table preview:
{preview_csv}
""".strip()

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": (
                    "You summarize CFR tables for workbook users. "
                    "Return only JSON that matches the requested schema."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt,
                    }
                ],
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "table_summary",
                "schema": TABLE_SUMMARY_SCHEMA,
                "strict": True,
            }
        },
    )

    raw = getattr(response, "output_text", "")
    if not raw:
        raise ValueError("AI summary returned no text.")

    return json.loads(raw)


def generate_basic_summary(df):
    return {
        "summary": (
            f"This table contains {len(df)} rows "
            f"and {len(df.columns)} columns."
        ),
        "key_columns": list(df.columns[:5]),
        "suggested_sheet_name": "CFR Table",
        "notes": [],
    }