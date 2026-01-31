import streamlit as st
import os

import redis
import time

def check_password():
    """
    Returns True if the user has a password set in the session state.
    Otherwise questions the user for a password.
    Blocks login for 30 seconds after 3 failed attempts (Global Lock).
    """
    
    # If already correctly authenticated, return True
    if st.session_state.get("password_correct", False):
        return True

    # Connect to Redis
    redis_host = os.environ.get("REDIS_HOST", "localhost")
    try:
        r = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)
        # Check connection
        r.ping()
    except redis.ConnectionError:
        st.error(f"Cannot connect to Redis at {redis_host}. Login unavailable.")
        st.stop()
        return False

    # Check for Global Lock
    lock_key = "login_lock"
    fail_key = "login_failures"
    lock_duration = 30
    max_failures = 3

    # Check for Global Lock
    lock_key = "login_lock"
    fail_key = "login_failures"
    lock_duration = 30
    max_failures = 3

    is_locked = False
    if r.exists(lock_key):
        is_locked = True
        ttl = r.ttl(lock_key)
        st.error(f"⚠️ Too many failed attempts. Login locked. Please wait {ttl} seconds.")
    
    # Get credentials from environment variables
    env_user = os.environ.get("LOGIN_USER")
    env_password = os.environ.get("LOGIN_PASSWORD")
    
    # Strict mode: if vars are missing, nobody can log in.
    if not env_user or not env_password:
        st.error("Login credentials are not configured in the environment.")
        st.stop()
        return False



    st.header("Login Request")
    
    # Show input for user/password
    with st.form("credentials"):
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password", key="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if is_locked:
                # If locked, do not process credentials. 
                # The lockout message is already displayed at the top.
                pass
            elif username == env_user and password == env_password:
                st.session_state["password_correct"] = True
                # Reset failures on success
                r.delete(fail_key)
                st.rerun()
            else:
                # Increment failure counter
                failures = r.incr(fail_key)
                if failures >= max_failures:
                    # Set lock
                    r.setex(lock_key, lock_duration, "locked")
                    r.delete(fail_key)
                    st.error(f"❌ Incorrect. Login locked for {lock_duration} seconds.")
                else:
                    remaining = max_failures - failures
                    st.error(f"😕 User not known or password incorrect. {remaining} attempts remaining.")
    
    # Stop execution of the calling script if not authenticated
    st.stop()
    return False
