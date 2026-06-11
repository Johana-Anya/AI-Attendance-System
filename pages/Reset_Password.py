import streamlit as st
import sqlite3

st.title("🔑 Reset Student Password")

username = st.text_input("Student Username")

new_password = st.text_input(
    "New Password",
    type="password"
)

if st.button("Reset Password"):

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET password=?
    WHERE username=?
    """,
    (
        new_password,
        username
    ))

    conn.commit()
    conn.close()

    st.success("Password Updated Successfully")