from __future__ import annotations

import streamlit as st


def get_error_content(error: Exception):
    text = str(error)

    if "503" in text or "Service Unavailable" in text:
        return {
            "title": "eCFR Service Unavailable",
            "message": "The eCFR service is currently unavailable.",
            "suggestions": [
                "Try again in a few minutes",
                "Use a different date",
                "Verify the CFR inputs"
            ]
        }

    if "404" in text or "Not Found" in text:
        return {
            "title": "CFR Content Not Found",
            "message": "The requested CFR content could not be located.",
            "suggestions": [
                "Verify Title, Part, and Section",
                "Try a different publication date"
            ]
        }

    if "No tables found" in text:
        return {
            "title": "No Tables Found",
            "message": "The selected section does not contain any tables.",
            "suggestions": [
                "Verify the section number",
                "Try another CFR section"
            ]
        }

    return {
        "title": "Unexpected Error",
        "message": "An unexpected error occurred while processing the request.",
        "suggestions": [
            "Try again",
            "Check your inputs",
            "Review technical details below"
        ]
    }


@st.dialog("Error")
def show_error_dialog(error: Exception):
    content = get_error_content(error)

    st.error(content["title"])
    st.write(content["message"])

    st.markdown("### Suggested Actions")
    for item in content["suggestions"]:
        st.markdown(f"- {item}")

    with st.expander("Technical Details"):
        st.code(str(error))

    if st.button("Close"):
        st.rerun()