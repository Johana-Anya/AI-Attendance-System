import streamlit as st
import sqlite3

st.set_page_config(
    page_title="AI Attendance System",
    layout="wide"
)

conn = sqlite3.connect("attendance.db")

st.title("🎓 AI Attendance System")

username = st.text_input("Username")
password = st.text_input(
    "Password",
    type="password"
)

if st.button("Login"):

    cursor = conn.cursor()

    cursor.execute("""
    SELECT role
    FROM users
    WHERE username=?
    AND password=?
    """,
    (username,password))

    user = cursor.fetchone()

    if user:

        st.session_state.role = user[0]
        st.session_state.username = username

        if user[0] == "admin":
            st.switch_page(
                "pages/admin_dashboard.py"
            )

        else:
            st.switch_page(
                "pages/student_dashboard.py"
            )

    else:
        st.error("Invalid Login")