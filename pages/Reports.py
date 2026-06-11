import streamlit as st
import sqlite3
import pandas as pd

st.title("📑 Reports")

conn = sqlite3.connect("attendance.db")

df = pd.read_sql_query(
    "SELECT * FROM attendance",
    conn
)

st.dataframe(df)

file_name = "attendance_report.xlsx"

df.to_excel(
    file_name,
    index=False
)

with open(file_name, "rb") as file:

    st.download_button(
        "Download Excel",
        file,
        file_name=file_name
    )

students = pd.read_sql_query(
    "SELECT * FROM students",
    conn
)