import streamlit as st
import sqlite3
import pickle
import cv2
import numpy as np
from datetime import datetime
from face_utils import model

st.set_page_config(
    page_title="Student Dashboard",
    layout="wide"
)

st.title("🎓 Student Attendance")

if "username" not in st.session_state:
    st.error("Please Login First")
    st.stop()

st.success(
    f"Welcome {st.session_state['username']}"
)

# Load embeddings
try:
    with open("embeddings.pkl", "rb") as f:
        embeddings = pickle.load(f)
except:
    st.error("embeddings.pkl not found. Run generate_embeddings.py first.")
    st.stop()

camera_image = st.camera_input(
    "📷 Capture Face For Attendance"
)

if camera_image is not None:

    file_bytes = np.asarray(
        bytearray(camera_image.read()),
        dtype=np.uint8
    )

    img = cv2.imdecode(
        file_bytes,
        1
    )

    faces = model.get(img)

    if len(faces) == 0:

        st.error("No Face Detected")

    else:

        current_embedding = faces[0].embedding

        matched_student = None
        min_distance = 999

        for student_id, stored_embedding in embeddings.items():

            distance = np.linalg.norm(
                current_embedding - stored_embedding
            )

            if distance < min_distance:

                min_distance = distance
                matched_student = student_id

        if min_distance < 25:

            st.success(
                f"Face Recognized: {matched_student}"
            )

            conn = sqlite3.connect(
                "attendance.db"
            )

            cursor = conn.cursor()

            today = datetime.now().strftime(
                "%Y-%m-%d"
            )

            current_time = datetime.now().strftime(
                "%H:%M:%S"
            )

            cursor.execute("""
            SELECT *
            FROM attendance
            WHERE student_id=?
            AND date=?
            """,
            (
                matched_student,
                today
            ))

            already_marked = cursor.fetchone()

            if already_marked:

                st.warning(
                    "Attendance Already Marked Today"
                )

            else:
                conn.commit()
                
                

                conn.commit()

                st.success(
                    "Attendance Marked Successfully"
                )

            conn.close()

        else:

            st.error(
                "Face Not Registered"
            )

if st.button("Logout"):

    st.session_state.clear()

    st.switch_page("App.py")