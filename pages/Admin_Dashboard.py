# pages/Admin_Dashboard.py — the admin console: stats, registration, records, analytics

import os                                                     # built-in library for file paths
import sys                                                    # lets us add the project folder to the import path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # so 'import db' works from inside pages/

import pandas as pd                                           # pandas turns database rows into tables/charts
import plotly.express as px                                   # plotly draws the interactive charts
import streamlit as st                                        # Streamlit builds the web UI
from datetime import datetime                                 # used for today's date in the overview

import auth                                                   # password hashing for new student accounts
import db                                                     # all database queries
import face_utils                                             # face embeddings for registration
import ui                                                     # the shared design system

st.set_page_config(                                           # must be the first Streamlit call
    page_title="Admin Console — VERIFACE",                    # browser-tab title
    page_icon="🟢",                                           # browser-tab icon
    layout="wide",                                            # dashboards want the full screen width
    initial_sidebar_state="expanded",                         # always open the nav sidebar on arrival
)

ui.inject_css()                                               # apply the theme
ui.require_role("admin")                                      # kick out anyone who isn't a logged-in admin

# ---------------- sidebar navigation ----------------

st.sidebar.markdown(                                          # mini brand block at the top of the sidebar
    "<div class='eyebrow'>// VERIFACE</div><h3 style='margin-top:0'>Admin Console</h3>",
    unsafe_allow_html=True,
)

menu = st.sidebar.radio(                                      # the section switcher
    "Navigation",                                             # label (hidden below)
    ["Overview", "Register Student", "Students", "Attendance", "Analytics"],  # the five sections
    label_visibility="collapsed",                             # hide the label, the heading above is enough
)

st.sidebar.markdown("---")                                    # thin divider above the logout button

if st.sidebar.button("Log out", use_container_width=True):    # logout lives at the bottom of the sidebar
    st.session_state.clear()                                  # forget who was logged in
    st.switch_page("App.py")                                  # back to the login screen

ui.sidebar_status()                                           # pulsing SYSTEM ONLINE block under the logout button

# ---------------- shared data ----------------

students = pd.DataFrame(                                      # every student as a pandas table
    [dict(r) for r in db.get_students()]                      # convert sqlite rows to plain dicts first
)
attendance = pd.DataFrame(                                    # every attendance record as a pandas table
    [dict(r) for r in db.get_attendance()]
)

# ---------------- OVERVIEW ----------------

if menu == "Overview":                                        # the landing section

    ui.page_header("ADMIN CONSOLE", "Overview")               # standard page heading

    total_students = len(students)                            # how many students are registered
    present_today = db.attendance_count_today()               # how many were marked present today
    pct_today = round(present_today / total_students * 100) if total_students else 0  # today's REAL percentage (was records/students before — could exceed 100%)

    ui.metric_cards([                                         # the row of stat cards (short labels so they never wrap mid-word)
        ("Students", total_students),                         # card 1
        ("Present today", present_today, True),               # card 2, mint highlight
        ("Today %", f"{pct_today}%"),                         # card 3
        ("Records", len(attendance)),                         # card 4
    ])

    st.markdown("<br>", unsafe_allow_html=True)               # breathing room under the cards

    if not attendance.empty:                                  # only chart when there is data
        attendance["date"] = pd.to_datetime(attendance["date"])  # turn date text into real dates
        trend = (
            attendance.groupby(attendance["date"].dt.date)    # bucket the records by day
            .size()                                           # count records per day
            .reset_index(name="present")                      # back to a flat table with a 'present' column
        )
        fig = px.area(trend, x="date", y="present", title="Daily attendance trend")  # soft area chart
        fig.update_traces(line_color="#34F5C5", fillcolor="rgba(52,245,197,.12)")    # mint line + translucent fill
        st.plotly_chart(ui.style_chart(fig), use_container_width=True)               # themed chart, full width
    else:                                                     # no records yet
        st.info("No attendance records yet — they will appear here once students start checking in.")

# ---------------- REGISTER STUDENT ----------------

elif menu == "Register Student":                              # add a new student, photo and all

    ui.page_header("ENROLLMENT", "Register Student")          # standard page heading

    with st.form("register", clear_on_submit=False):          # one form so everything submits together
        col1, col2 = st.columns(2)                            # details on the left, photo on the right
        with col1:                                            # left column
            student_id = st.text_input("Student ID", placeholder="23AIDS001")   # the roll number (used as username too)
            name = st.text_input("Full name", placeholder="Johana Anya")        # display name
            department = st.text_input("Department", placeholder="AI & DS")     # department text
            password = st.text_input("Initial password", type="password")       # the student's first login password
        with col2:                                            # right column
            photo = st.camera_input("Face photo")             # live webcam capture for the face on file
        submitted = st.form_submit_button("Register student", use_container_width=True)  # the submit button

    if submitted:                                             # runs once the form is sent
        if not student_id or not name or not password:        # the three required fields
            st.error("Student ID, name and password are required.")  # explain what is missing
        elif photo is None:                                   # no photo captured
            st.error("Please capture a face photo before registering.")  # photo is mandatory
        else:                                                 # all inputs present — try the enrollment
            with st.spinner("Scanning face and creating profile…"):       # show progress while the model runs
                embedding = face_utils.embedding_from_bytes(photo.getvalue())  # turn the photo into a face fingerprint
            if embedding is None:                             # the model found no face in the shot
                st.error("No face detected in the photo — please retake it with good lighting.")
            else:                                             # we have a valid face
                os.makedirs("images", exist_ok=True)          # make sure the images folder exists
                image_path = os.path.join("images", f"{student_id}.jpg")  # file named after the roll number (names can collide, IDs can't)
                with open(image_path, "wb") as f:             # open the destination file for binary writing
                    f.write(photo.getvalue())                 # save the raw photo bytes
                if not db.add_student(student_id, name, department, image_path):  # insert the student row
                    st.error(f"Student ID '{student_id}' already exists.")        # duplicate roll number
                else:                                         # student row created — finish the enrollment
                    face_utils.add_embedding(student_id, embedding)               # store the face fingerprint
                    auth_hash = auth.hash_password(password)                      # hash the initial password
                    db.create_user(student_id, auth_hash, "student", student_id)  # login account: username = roll number
                    st.success(f"{name} registered — they can log in as '{student_id}'.")  # confirm everything worked
                    st.balloons()                             # small celebration

# ---------------- STUDENTS ----------------

elif menu == "Students":                                      # view and manage registered students

    ui.page_header("DIRECTORY", "Registered Students")        # standard page heading

    if students.empty:                                        # nobody registered yet
        st.info("No students registered yet — use the Register Student section.")  # point at the fix
    else:                                                     # we have students to show
        st.dataframe(                                         # the full directory table
            students[["student_id", "name", "department"]],   # hide the internal image_path column
            use_container_width=True, hide_index=True,        # full width, no row numbers
        )

        st.markdown("<br>", unsafe_allow_html=True)           # spacing before the danger zone

        with st.expander("⚠ Remove a student"):               # destructive actions tucked into an expander
            target = st.selectbox(                            # pick who to remove
                "Student to remove",
                students["student_id"].tolist(),              # all roll numbers
                format_func=lambda sid: f"{sid} — {students.set_index('student_id').loc[sid, 'name']}",  # show 'ID — Name'
            )
            confirm = st.checkbox("I understand this also deletes their login and face data")  # explicit confirmation
            if st.button("Delete student", disabled=not confirm):  # button stays disabled until confirmed
                db.delete_student(target)                     # remove student row + login account
                face_utils.remove_embedding(target)           # remove their face fingerprint
                row = students.set_index("student_id").loc[target]                  # find their record
                if row["image_path"] and os.path.exists(row["image_path"]):        # if their photo file exists
                    os.remove(row["image_path"])              # delete the photo too
                st.success(f"{target} removed.")              # confirm
                st.rerun()                                    # refresh the page so the table updates

# ---------------- ATTENDANCE ----------------

elif menu == "Attendance":                                    # browse and export the raw records

    ui.page_header("RECORDS", "Attendance Log")               # standard page heading

    if attendance.empty:                                      # nothing recorded yet
        st.info("No attendance records yet.")                 # nothing else to draw
    else:                                                     # we have records
        dates = sorted(attendance["date"].unique(), reverse=True)        # every distinct day, newest first
        picked = st.selectbox("Filter by date", ["All dates"] + list(dates))  # optional single-day filter
        view = attendance if picked == "All dates" else attendance[attendance["date"] == picked]  # apply the filter

        st.dataframe(                                         # the filtered records table
            view[["student_id", "name", "date", "time"]],     # hide the internal id column
            use_container_width=True, hide_index=True,        # full width, no row numbers
        )

        st.download_button(                                   # real browser download (old app wrote Excel to the server's disk)
            "⬇ Download CSV",                                 # button label
            view.to_csv(index=False).encode(),                # the table as CSV bytes
            file_name=f"attendance_{picked.replace(' ', '_')}_{datetime.now():%Y%m%d}.csv",  # tidy filename
            mime="text/csv",                                  # tells the browser it's a CSV
        )

# ---------------- ANALYTICS ----------------

elif menu == "Analytics":                                     # per-student statistics

    ui.page_header("INSIGHTS", "Analytics")                   # standard page heading

    if attendance.empty or students.empty:                    # need both students and records
        st.info("Analytics will appear once attendance has been recorded.")  # nothing to compute yet
    else:                                                     # enough data to analyse
        days_total = attendance["date"].nunique()             # how many distinct class days exist in the data
        per_student = (
            attendance.groupby("student_id")                  # bucket records per student
            .size()                                           # count each student's records
            .reset_index(name="days_present")                 # flat table with a days_present column
        )
        per_student = students[["student_id", "name"]].merge( # attach names, include students with zero records
            per_student, on="student_id", how="left"
        ).fillna({"days_present": 0})                         # zero for students never marked present
        per_student["attendance_%"] = (                       # each student's true percentage
            per_student["days_present"] / days_total * 100
        ).round(1)

        fig = px.bar(                                         # bar chart of percentages
            per_student.sort_values("attendance_%"),          # lowest attenders first so they stand out
            x="attendance_%", y="name", orientation="h",      # horizontal bars read better with names
            title=f"Attendance % over {days_total} recorded day(s)",
        )
        st.plotly_chart(ui.style_chart(fig), use_container_width=True)  # themed chart, full width

        st.dataframe(                                         # the same numbers as a sortable table
            per_student.sort_values("attendance_%", ascending=False),   # best attenders on top
            use_container_width=True, hide_index=True,        # full width, no row numbers
        )
