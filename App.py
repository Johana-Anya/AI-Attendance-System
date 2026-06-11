# App.py — the login page (the first screen everyone sees)

import streamlit as st                                        # Streamlit builds the web UI

import auth                                                   # our password-checking module
import db                                                     # our database module
import ui                                                     # our shared design system

st.set_page_config(                                           # must be the FIRST Streamlit call on the page
    page_title="VERIFACE — AI Attendance",                    # browser-tab title
    page_icon="🟢",                                           # browser-tab icon
    layout="centered",                                        # narrow centered column suits a login card
    initial_sidebar_state="collapsed",                        # no sidebar needed before logging in
)

db.init_db()                                                  # make sure all tables exist before anything queries them
ui.inject_css()                                               # apply the biometric-terminal theme

# the animated scan-ring logo plus the product wordmark, centered
st.markdown(
    """
    <div class='fade-in' style='text-align:center; padding-top:1.5rem'>
        <div class='scan-ring'><div class='beam'></div></div>
        <div class='eyebrow' style='text-align:center'>// FACIAL RECOGNITION ATTENDANCE</div>
        <h1 style='margin:.1rem 0 .4rem 0'>VERIFACE</h1>
        <p style='color:var(--muted); margin-bottom:1.1rem'>Sign in to continue to your console</p>
    </div>
    """,
    unsafe_allow_html=True,                                   # allow the custom HTML through
)

ui.ticker("System online · Engine BUFFALO_L · 512-D embeddings · Threshold 0.40")  # techy status line under the wordmark
st.markdown("<br>", unsafe_allow_html=True)                   # breathing room before the form

left, mid, right = st.columns([1, 2, 1])                      # squeeze the form into the middle 50% of the page

with mid:                                                     # everything inside renders in that middle column
    with st.form("login"):                                    # a form lets Enter-key submit the login
        username = st.text_input("Username")                  # username field
        password = st.text_input("Password", type="password") # password field, characters hidden
        submitted = st.form_submit_button(                    # the login button
            "Authenticate", use_container_width=True          # stretch it across the form
        )

    if submitted:                                             # only runs after the button (or Enter) is pressed
        user = auth.login(username.strip(), password)         # check the credentials against the database
        if user is None:                                      # wrong username or password
            st.error("Invalid credentials — please try again.")  # show the failure message
        else:                                                 # credentials are correct
            st.session_state.role = user["role"]              # remember the role for page guards
            st.session_state.username = user["username"]      # remember who is logged in
            st.session_state.student_id = user["student_id"]  # remember their roll number (None for admins)
            if user["role"] == "admin":                       # admins go to the admin console
                st.switch_page("pages/Admin_Dashboard.py")    # exact filename — the original app had a broken path here
            else:                                             # everyone else is a student
                st.switch_page("pages/Student_Dashboard.py")  # send them to the attendance camera page

    # small footer hint with the seeded demo credentials
    st.markdown(
        "<p style='text-align:center; color:var(--muted); font-size:.75rem; "
        "font-family:JetBrains Mono, monospace; margin-top:1rem'>"
        "default admin · <b>admin / admin123</b></p>",
        unsafe_allow_html=True,                               # allow the custom HTML through
    )
