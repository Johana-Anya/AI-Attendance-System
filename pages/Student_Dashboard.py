# pages/Student_Dashboard.py — the student kiosk: scan your face, get marked present

import os                                                     # built-in library for file paths
import sys                                                    # lets us add the project folder to the import path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # so 'import db' works from inside pages/

import pandas as pd                                           # turns attendance history into a table
import streamlit as st                                        # Streamlit builds the web UI
from datetime import datetime                                 # for showing today's date

import db                                                     # all database queries
import face_utils                                             # face matching
import ui                                                     # the shared design system

st.set_page_config(                                           # must be the first Streamlit call
    page_title="Check In — VERIFACE",                         # browser-tab title
    page_icon="🟢",                                           # browser-tab icon
    layout="centered",                                        # a kiosk works best as one centered column
)

ui.inject_css()                                               # apply the theme
ui.require_role("student")                                    # kick out anyone who isn't a logged-in student

me = st.session_state.student_id                              # this student's roll number, saved at login
student = db.get_student(me)                                  # their full record from the database
display_name = student["name"] if student else st.session_state.username  # prefer the real name

ui.page_header("CHECK-IN TERMINAL", f"Hello, {display_name.split()[0]}")  # greet them by first name

st.markdown(                                                  # today's date in mono under the heading
    f"<p style='font-family:JetBrains Mono, monospace; color:var(--muted)'>"
    f"{datetime.now():%A, %d %B %Y}</p>",
    unsafe_allow_html=True,
)

history = db.get_student_attendance(me)                       # this student's full attendance history
today = datetime.now().strftime("%Y-%m-%d")                   # today's date as text
marked_today = any(row["date"] == today for row in history)   # have they already checked in today?

ui.metric_cards([                                             # two quick stats at the top
    ("Days attended", len(history)),                          # total days present
    ("Today", "PRESENT ✓" if marked_today else "NOT MARKED", marked_today),  # mint highlight once present
])

st.markdown("<br>", unsafe_allow_html=True)                   # spacing before the camera

if marked_today:                                              # nothing more to do today
    st.success("You're already marked present today — see you tomorrow!")  # friendly confirmation
else:                                                         # not yet marked — show the scanner
    shot = st.camera_input("Position your face in the frame and capture")  # live webcam capture

    if shot is not None:                                      # runs once a photo is taken
        with st.spinner("Scanning…"):                         # show progress while the model runs
            embedding = face_utils.embedding_from_bytes(shot.getvalue())  # photo → face fingerprint

        if embedding is None:                                 # the model found no face
            st.error("No face detected — make sure your face is well lit and centred.")
        else:                                                 # we have a face, try to match it
            match_id, score = face_utils.match_face(embedding)  # compare against every registered face

            if match_id is None:                              # nobody was similar enough
                st.error("Face not recognized — please contact your admin if this keeps happening.")
            elif match_id != me:                              # recognized... but as a DIFFERENT student
                st.error("This face doesn't match the logged-in account.")  # stops checking in for a friend
            else:                                             # the face matches the logged-in student
                ui.scan_result(display_name, me, score)       # show the glowing identity badge
                if db.mark_attendance(me):                    # write today's record (the original app never inserted anything here)
                    st.success("Attendance marked — have a great day!")  # confirm the write
                    st.balloons()                             # small celebration
                    st.rerun()                                # refresh so the page flips to 'already marked'
                else:                                         # the UNIQUE rule said it already exists
                    st.warning("Attendance was already marked today.")  # explain why nothing was written

if history:                                                   # show their personal history if any exists
    st.markdown("<br>", unsafe_allow_html=True)               # spacing above the table
    st.markdown("<div class='eyebrow'>// YOUR HISTORY</div>", unsafe_allow_html=True)  # small section label
    st.dataframe(                                             # their dates and times
        pd.DataFrame([dict(r) for r in history]),             # sqlite rows → pandas table
        use_container_width=True, hide_index=True,            # full width, no row numbers
    )

st.markdown("---")                                            # divider above the logout button

if st.button("Log out"):                                      # let the student end their session
    st.session_state.clear()                                  # forget who was logged in
    st.switch_page("App.py")                                  # back to the login screen
