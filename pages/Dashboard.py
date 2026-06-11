import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(
    page_title="Dashboard",
    layout="wide"
)

st.title("📊 Dashboard")

try:

    conn = sqlite3.connect(
        "attendance.db"
    )

    students = pd.read_sql_query(
        "SELECT * FROM students",
        conn
    )

    attendance = pd.read_sql_query(
        "SELECT * FROM attendance",
        conn
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Students",
        len(students)
    )

    col2.metric(
        "Attendance Records",
        len(attendance)
    )

    col3.metric(
        "Today's Attendance",
        len(attendance)
    )

    st.subheader(
        "Attendance Records"
    )

    st.dataframe(
        attendance,
        use_container_width=True
    )

    conn.close()

except Exception as e:

    st.error(
        f"Database Error: {e}"
    )