import streamlit as st
import os

def check_password():
    """
    Returns True if the user has a password set in the session state.
    Otherwise questions the user for a password.
    """
    
    # If already correctly authenticated, return True
    if st.session_state.get("password_correct", False):
        return True

    # Get credentials from environment variables
    # We default to empty string if not set, which matches nothing if user inputs something,
    # or handle explicitly.
    env_user = os.environ.get("LOGIN_USER")
    env_password = os.environ.get("LOGIN_PASSWORD")
    
    # Optional: If env vars are NOT set, you might want to allow access or fail.
    # Here we assume strict mode: if vars are missing, nobody can log in.
    if not env_user or not env_password:
        st.error("Login credentials are not configured in the environment.")
        st.stop()
        return False

    st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

    st.header("Login Request")
    
    # Show input for user/password
    with st.form("credentials"):
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password", key="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if username == env_user and password == env_password:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("😕 User not known or password incorrect")
    
    # Stop execution of the calling script if not authenticated
    st.stop()
    return False
