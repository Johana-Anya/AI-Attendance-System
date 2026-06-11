import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---------------- CONFIG ----------------

st.set_page_config(
    page_title="AI Attendance Dashboard",
    page_icon="🎓",
    layout="wide"
)

# ---------------- CSS ----------------

st.markdown("""
<style>

.stApp{
    background-color:#0E1117;
    color:white;
}

[data-testid="stSidebar"]{
    background-color:#111827;
}

.card{
    background:#1F2937;
    padding:20px;
    border-radius:15px;
    text-align:center;
    box-shadow:0px 4px 10px rgba(0,0,0,0.4);
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN CHECK ----------------

if "role" not in st.session_state:
    st.error("Please Login First")
    st.stop()

if st.session_state.role != "admin":
    st.error("Access Denied")
    st.stop()

# ---------------- SIDEBAR ----------------

st.sidebar.title("🎓 AI Attendance")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Students",
        "Attendance",
        "Analytics"
    ]
)

if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.switch_page("App.py")

# ---------------- DATABASE ----------------

conn = sqlite3.connect("attendance.db")

students = pd.read_sql_query(
    "SELECT * FROM students",
    conn
)

attendance = pd.read_sql_query(
    "SELECT * FROM attendance",
    conn
)

# ---------------- DASHBOARD ----------------

if menu == "Dashboard":

    st.title("🎓 AI Attendance Dashboard")

    total_students = len(students)

    total_attendance = len(attendance)

    if total_students > 0:
        attendance_percent = round(
            (total_attendance / total_students) * 100,
            2
        )
    else:
        attendance_percent = 0

    col1,col2,col3 = st.columns(3)

    with col1:
        st.metric(
            "👨‍🎓 Students",
            total_students
        )

    with col2:
        st.metric(
            "📋 Attendance Records",
            total_attendance
        )

    with col3:
        st.metric(
            "📊 Attendance %",
            f"{attendance_percent}%"
        )

    st.markdown("---")

    if len(attendance) > 0:

        attendance["date"] = pd.to_datetime(
            attendance["date"]
        )

        chart_data = (
            attendance.groupby(
                attendance["date"].dt.date
            )
            .size()
            .reset_index(name="count")
        )

        fig = px.line(
            chart_data,
            x="date",
            y="count",
            title="Attendance Trend"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if len(students) > 0:

        student_list = students["student_id"].tolist()

        selected_student = st.selectbox(
            "Select Student",
        student_list
    )
        
    if st.button("Delete Selected Student"):
        conn = sqlite3.connect("attendance.db")
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM students WHERE student_id=?",
            (selected_student,)
        )

        conn.commit()
        conn.close()

        st.success("Student Deleted")
        st.rerun()

# ---------------- STUDENTS ----------------

elif menu == "Students":

    st.title("👨‍🎓 Registered Students")

    st.dataframe(
        students,
        use_container_width=True
    )
if st.button("🗑 Delete All Students"):

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students")

    conn.commit()
    conn.close()

    st.success("All students deleted successfully")
    st.rerun()
    
# ---------------- ATTENDANCE ----------------

elif menu == "Attendance":

    st.title("📋 Attendance Records")

    st.dataframe(
        attendance,
        use_container_width=True
    )

    if st.button("📥 Export Excel"):

        attendance.to_excel(
            "attendance_report.xlsx",
            index=False
        )

        st.success(
            "Excel Exported Successfully"
        )

# ---------------- ANALYTICS ----------------

elif menu == "Analytics":

    st.title("📊 Attendance Analytics")

    if len(attendance) > 0:

        attendance_count = (
            attendance.groupby("student_id")
            .size()
            .reset_index(name="Attendance")
        )

        fig = px.bar(
            attendance_count,
            x="student_id",
            y="Attendance",
            title="Student Attendance Count"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No attendance records available."
        )

conn.close()
