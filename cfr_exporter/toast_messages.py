import streamlit as st

def queue_toast(message: str, icon: str = "✅") -> None:
    st.session_state.toast_message = message
    st.session_state.toast_icon = icon