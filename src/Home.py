import streamlit as st
from auth import check_password

st.set_page_config(
    page_title="Jobby",
    page_icon="🤖",
)


# Hide sidebar if not logged in (Separation of Concerns: UI logic here, Auth logic in check_password)
if not st.session_state.get("password_correct", False):
    st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

check_password()

st.title("Welcome to Jobby 🤖")

st.markdown("""
This tool helps you analyze job interview transcriptions using AI. 

### How to use:
1. Navigate to the **Interview Analyzer** page from the sidebar.
2. Upload an audio recording of an interview.
3. The AI will transcribe the audio and generate a detailed analysis, including:
    - Executive Summary
    - Skills Assessment
    - Behavioral Analysis (STAR method)
    - Sentiment Analysis
    - And more!

You can also browse and re-analyze past interviews using a different prompt.
""")
