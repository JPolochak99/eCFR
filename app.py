import streamlit as st
from pathlib import Path
from io import BytesIO
import pandas as pd
from bs4 import BeautifulSoup
import requests

st.title("CFR to Excel Export")
title= st.text_input("Title", "49")
subtitle = st.text_input("Subtitle", "B")
chapter = st.text_input("Chapter", "I")
subchapter = st.text_input("Subchapter", "C")
part = st.text_input("Part", "173")
subpart = st.text_input("Subpart", "I")
section = st.text_input("Section", "173.435")
date = st.date_input("eCFR date")
#server_output_dir = st.text_input(
#    "Server output folder (optional)",
#    value=""
#)
def build_excel_bytes(title, subtitle, chapter, subchapter, part, subpart, section, date) -> bytes:
    BASE_URL = "https://www.ecfr.gov"
    DATE = date.isoformat()

    url = f"{BASE_URL}/api/versioner/v1/full/{DATE}/title-{title}.xml"

    params = {
        "subtitle": subtitle,
        "chapter": chapter,
        "subchapter": subchapter,
        "part": part,
        "subpart": subpart,
        "section": section,
    }

    headers = {
        "Accept": "application/xml,text/xml,*/*",
        "User-Agent": "Mozilla/5.0",
    }

    response = requests.get(url, headers=headers, params=params, timeout=60)
    response.raise_for_status()
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "xml")

    table = soup.find("TABLE", attrs={"class": "gpo_table"}) or soup.find("TABLE")
    if table is None:
        raise ValueError("Could not find a table in the response.xml file.")

    rows = []
    body = table.find("TBODY")
    tr_source = body.find_all("TR") if body else table.find_all("TR")

    for tr in tr_source:
        cells = [td.get_text(" ", strip=True) for td in tr.find_all(["TD", "TH"])]
        if not cells:
            continue
        rows.append(cells)

    if not rows:
        raise ValueError("No table rows were extracted.")

    max_cols = max(len(r) for r in rows)
    rows = [r + [""] * (max_cols - len(r)) for r in rows]

    columns = [
        "Symbol of radionuclide",
        "Element and atomic number",
        "A1 TBq",
        "A1 Ci",
        "A2 TBq",
        "A2 Ci",
        "Specific activity TBq/g",
        "Specific activity Ci/g",
    ]

    if len(columns) < max_cols:
        columns += [f"Column {i}" for i in range(len(columns) + 1, max_cols + 1)]
    else:
        columns = columns[:max_cols]

    df = pd.DataFrame(rows, columns=columns)

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="CFR")
    buffer.seek(0)
    return buffer.getvalue()

if st.button("Generate Excel"):
    try:
        excel_bytes = build_excel_bytes(title, subtitle, chapter, subchapter, part, subpart, section, date)
        file_name = f"section_{section.replace('.', '_')}.xlsx"

        st.success(f"Excel file created for section {section}.")

        st.download_button(
            label="Download Excel",
            data=excel_bytes,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as e:
        st.error(f"Failed to generate Excel: {e}")
