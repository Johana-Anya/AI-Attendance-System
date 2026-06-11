import streamlit as st
import sqlite3
import os

st.set_page_config(
    page_title="Register Student",
    layout="wide"
)

st.title("👨‍🎓 Register Student")

student_id = st.text_input(
    "Student ID"
)

name = st.text_input(
    "Student Name"
)

department = st.text_input(
    "Department"
)

password = st.text_input(
    "Password",
    type="password"
)

image = st.camera_input(
    "Capture Face"
)

if st.button("Register Student"):

    if not student_id:
        st.error("Enter Student ID")

    elif not name:
        st.error("Enter Student Name")

    elif not department:
        st.error("Enter Department")

    elif not password:
        st.error("Enter Password")

    elif image is None:
        st.error("Capture Student Face")

    else:

        os.makedirs(
            "images",
            exist_ok=True
        )

        image_path = f"images/{student_id}.jpg"

        with open(image_path, "wb") as f:
            f.write(image.getbuffer())

        conn = sqlite3.connect(
            "attendance.db"
        )

        cursor = conn.cursor()

        try:

            # Save student details
            cursor.execute("""
            INSERT INTO students
            (
                student_id,
                name,
                department,
                image_path
            )
            VALUES (?,?,?,?)
            """,
            (
                student_id,
                name,
                department,
                image_path
            ))

            # Create login account
            cursor.execute("""
            INSERT INTO users
            (
                username,
                password,
                role
            )
            VALUES (?,?,?)
            """,
            (
                student_id,
                password,
                "student"
            ))

            conn.commit()

            st.success(
                "✅ Student Registered Successfully"
            )

            st.info(
                f"Login Username: {student_id}"
            )

        except Exception as e:

            st.error(
                f"Database Error: {e}"
            )

        finally:

            conn.close()