from __future__ import annotations

import datetime as dt

import streamlit as st


def render_sidebar() -> dict[str, object]:
    with st.sidebar:
        st.header("CFR target")
        title = st.text_input("Title", "49")
        subtitle = st.text_input("Subtitle", "B")
        chapter = st.text_input("Chapter", "I")
        subchapter = st.text_input("Subchapter", "C")
        part = st.text_input("Part", "173")
        subpart = st.text_input("Subpart", "I")
        section = st.text_input("Section", "173.435")

        use_latest = st.checkbox("Use latest available eCFR date", value=True)

        custom_date = dt.date.today()
        if not use_latest:
            custom_date = st.date_input("Custom eCFR date", value=dt.date.today())


        find_clicked = st.button("Find Tables")

    return {
        "title": title,
        "subtitle": subtitle,
        "chapter": chapter,
        "subchapter": subchapter,
        "part": part,
        "subpart": subpart,
        "section": section,
        "use_latest": use_latest,
        "custom_date": custom_date,
        "find_clicked": find_clicked,
    }