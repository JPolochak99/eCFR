import streamlit as st
from io import BytesIO
import pandas as pd
from bs4 import BeautifulSoup
import requests

from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter
import re

st.title("CFR to Excel Export")

title = st.text_input("Title", "49")
subtitle = st.text_input("Subtitle", "B")
chapter = st.text_input("Chapter", "I")
subchapter = st.text_input("Subchapter", "C")
part = st.text_input("Part", "173")
subpart = st.text_input("Subpart", "I")
section = st.text_input("Section", "173.435")
date = st.date_input("eCFR date")


import pandas as pd

def parse_radionuclide(value):
    if pd.isna(value):
        return value, "", ""

    s = str(value).strip()

    # Pull out all parenthetical notes, e.g. "(short lived)", "(a)", "(d)"
    notes = re.findall(r"\(([^)]*)\)", s)
    note_text = "; ".join(n.strip() for n in notes if n.strip())

    # Remove all parenthetical parts from the string
    core = re.sub(r"\s*\([^)]*\)", "", s).strip()

    # Match the base radionuclide pattern, e.g. Np-236 or Tc-99m
    m = re.match(r"^([A-Za-z]+)-(\d+)([A-Za-z]*)$", core)
    if not m:
        return s, note_text, ""

    symbol = m.group(1)
    mass = m.group(2).zfill(3)
    suffix = m.group(3)

    formatted = f"{mass}{symbol}{suffix}"
    return formatted, note_text, core


def convert_scientific(value):
    if pd.isna(value):
        return value

    s = str(value).strip()

    # Leave text values alone
    if s == "" or s.lower() == "unlimited" or "see §" in s:
        return s

    # Normalize spacing and minus sign
    s = s.replace("−", "-")

    # Match forms like:
    # 1.0 × 10 1
    # 8.0 × 10 -1
    m = re.match(r"^([0-9.]+)\s*×\s*10\s*([+-]?\d+)$", s)

    if m:
        mantissa = float(m.group(1))
        exponent = int(m.group(2))
        return mantissa * (10 ** exponent)

    try:
        return float(s)
    except:
        return value
    

def build_excel_bytes_formatted(title, subtitle, chapter, subchapter, part, subpart, section, date) -> bytes:
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

    base_columns = [
        "Symbol of radionuclide",
        "Element and atomic number",
        "A1 TBq",
        "A1 Ci",
        "A2 TBq",
        "A2 Ci",
        "Specific activity TBq/g",
        "Specific activity Ci/g",
    ]

    columns = base_columns[:max_cols]

    if len(columns) < max_cols:
        columns += [f"Column {i}" for i in range(len(columns) + 1, max_cols + 1)]

    df = pd.DataFrame(rows, columns=columns)

    parsed = df["Symbol of radionuclide"].apply(parse_radionuclide).apply(pd.Series)
    parsed.columns = ["Symbol of radionuclide", "Symbol note", "Symbol core"]

    df = df.drop(columns=["Symbol of radionuclide"]).join(parsed)

    # Put the new radionuclide columns first
    first_cols = [
        "Symbol of radionuclide",
        "Symbol note",
        "Symbol core",
    ]
    other_cols = [c for c in df.columns if c not in first_cols]
    df = df[first_cols + other_cols]

    numeric_cols = [
        "A1 TBq",
        "A1 Ci",
        "A2 TBq",
        "A2 Ci",
        "Specific activity TBq/g",
        "Specific activity Ci/g",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(convert_scientific)
    
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="CFR")

        ws = writer.book["CFR"]
        last_row = ws.max_row
        last_col = ws.max_column
        table_ref = f"A1:{get_column_letter(last_col)}{last_row}"

        sci_format = "0.0E+00"
        for col_name in numeric_cols:
            if col_name in df.columns:
                col_idx = df.columns.get_loc(col_name) + 1
                for row in range(2, ws.max_row + 1):
                    ws.cell(row=row, column=col_idx).number_format = sci_format

        excel_table = Table(displayName="CFRTable", ref=table_ref)
        style = TableStyleInfo(
            name="TableStyleMedium2",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False,
        )
        excel_table.tableStyleInfo = style
        ws.add_table(excel_table)

    buffer.seek(0)
    return buffer.getvalue()


def build_excel_bytes_raw(title, subtitle, chapter, subchapter, part, subpart, section, date) -> bytes:
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


col1, col2 = st.columns(2)

with col1:
    formatted = st.button("Generate Excel (Formatted)")

with col2:
    raw = st.button("Generate Excel (Raw)")


if formatted:
    try:
        excel_bytes = build_excel_bytes_formatted(
            title,
            subtitle,
            chapter,
            subchapter,
            part,
            subpart,
            section,
            date
        )

        st.success("Formatted Excel created")

        st.download_button(
            "Download Formatted Excel",
            excel_bytes,
            file_name=f"section_{section.replace('.','_')}_formatted.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Formatted export failed: {e}")



if raw:
    try:
        excel_bytes = build_excel_bytes_raw(
            title,
            subtitle,
            chapter,
            subchapter,
            part,
            subpart,
            section,
            date
        )

        st.success("Raw Excel created")

        st.download_button(
            "Download Raw Excel",
            excel_bytes,
            file_name=f"section_{section.replace('.','_')}_raw.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Raw export failed: {e}")