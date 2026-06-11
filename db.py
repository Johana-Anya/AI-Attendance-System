# db.py — single place for ALL database work (connections, tables, queries)

import sqlite3                                                # built-in library that talks to the SQLite database file
import os                                                     # built-in library for file-path handling
from datetime import datetime                                 # built-in class used to stamp attendance with date + time

# absolute path to the database file, kept next to this script so it works no matter where you run from
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attendance.db")


def get_connection():
    """Open one connection to the database and return it."""
    conn = sqlite3.connect(DB_PATH)                           # open (or create) the attendance.db file
    conn.row_factory = sqlite3.Row                            # make rows behave like dicts (row["name"]) instead of plain tuples
    return conn                                               # hand the open connection back to the caller


def init_db():
    """Create every table the app needs (safe to run many times)."""
    with get_connection() as conn:                            # 'with' auto-commits and closes the connection when done
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id            INTEGER PRIMARY KEY AUTOINCREMENT,  -- unique row number, filled in automatically
                username      TEXT UNIQUE NOT NULL,               -- login name, no duplicates allowed
                password_hash TEXT NOT NULL,                      -- salted hash of the password (never the real password)
                role          TEXT NOT NULL,                      -- either 'admin' or 'student'
                student_id    TEXT                                -- links a student login to their students row (NULL for admins)
            )
        """)                                                  # run the SQL that creates the users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students(
                student_id TEXT PRIMARY KEY,                      -- roll number, e.g. 23AIDS001 (the one true ID everywhere)
                name       TEXT NOT NULL,                         -- student's display name
                department TEXT,                                  -- e.g. 'AI & DS'
                image_path TEXT                                   -- where the registered face photo is stored on disk
            )
        """)                                                  # run the SQL that creates the students table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attendance(
                id         INTEGER PRIMARY KEY AUTOINCREMENT,     -- unique row number for each attendance record
                student_id TEXT NOT NULL,                         -- which student this record belongs to
                name       TEXT,                                  -- student name copied in so reports read nicely
                date       TEXT NOT NULL,                         -- day of attendance, format YYYY-MM-DD
                time       TEXT NOT NULL,                         -- clock time it was marked, format HH:MM:SS
                UNIQUE(student_id, date)                          -- database-level rule: one record per student per day
            )
        """)                                                  # run the SQL that creates the attendance table


# ---------------- user queries ----------------

def create_user(username, password_hash, role, student_id=None):
    """Insert one login account; returns False if the username is taken."""
    try:                                                      # try the insert and watch for a duplicate-username error
        with get_connection() as conn:                        # open the database
            conn.execute(
                "INSERT INTO users (username, password_hash, role, student_id) VALUES (?, ?, ?, ?)",
                (username, password_hash, role, student_id),  # '?' placeholders stop SQL-injection attacks
            )                                                 # run the insert
        return True                                           # insert worked
    except sqlite3.IntegrityError:                            # raised when the UNIQUE rule on username is violated
        return False                                          # tell the caller the username already exists


def get_user(username):
    """Fetch one user row by username (or None if it doesn't exist)."""
    with get_connection() as conn:                            # open the database
        return conn.execute(
            "SELECT * FROM users WHERE username = ?",         # look the user up by exact username
            (username,),
        ).fetchone()                                          # fetchone() returns the first row or None


def update_password(username, password_hash):
    """Store a new password hash for an existing user."""
    with get_connection() as conn:                            # open the database
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE username = ?",  # overwrite only that user's hash
            (password_hash, username),
        )                                                     # run the update


# ---------------- student queries ----------------

def add_student(student_id, name, department, image_path):
    """Insert one student; returns False if the student_id is taken."""
    try:                                                      # watch for a duplicate student_id
        with get_connection() as conn:                        # open the database
            conn.execute(
                "INSERT INTO students (student_id, name, department, image_path) VALUES (?, ?, ?, ?)",
                (student_id, name, department, image_path),   # all four columns for the new student
            )                                                 # run the insert
        return True                                           # insert worked
    except sqlite3.IntegrityError:                            # student_id is the PRIMARY KEY, duplicates raise this
        return False                                          # tell the caller this ID already exists


def get_students():
    """Return every student row as a list."""
    with get_connection() as conn:                            # open the database
        return conn.execute(
            "SELECT * FROM students ORDER BY student_id"      # alphabetical by roll number for tidy tables
        ).fetchall()                                          # fetchall() returns all matching rows as a list


def get_student(student_id):
    """Return one student row by ID (or None)."""
    with get_connection() as conn:                            # open the database
        return conn.execute(
            "SELECT * FROM students WHERE student_id = ?",    # exact match on the roll number
            (student_id,),
        ).fetchone()                                          # first row or None


def delete_student(student_id):
    """Remove a student plus their login, attendance history stays for records."""
    with get_connection() as conn:                            # open the database
        conn.execute("DELETE FROM students WHERE student_id = ?", (student_id,))   # remove the student row
        conn.execute("DELETE FROM users    WHERE student_id = ?", (student_id,))   # remove their login account too


# ---------------- attendance queries ----------------

def mark_attendance(student_id):
    """Write today's attendance for a student; returns False if already marked."""
    student = get_student(student_id)                         # look the student up so we can store their name as well
    name = student["name"] if student else student_id         # fall back to the ID if the row is somehow missing
    today = datetime.now().strftime("%Y-%m-%d")               # today's date as text, e.g. 2026-06-12
    now = datetime.now().strftime("%H:%M:%S")                 # current clock time as text, e.g. 09:41:05
    try:                                                      # watch for the one-per-day UNIQUE rule
        with get_connection() as conn:                        # open the database
            conn.execute(
                "INSERT INTO attendance (student_id, name, date, time) VALUES (?, ?, ?, ?)",
                (student_id, name, today, now),               # the actual row being written  <-- this INSERT was missing in the original app
            )                                                 # run the insert
        return True                                           # marked successfully
    except sqlite3.IntegrityError:                            # UNIQUE(student_id, date) fired — already marked today
        return False                                          # tell the caller it was a duplicate


def get_attendance():
    """Return every attendance row, newest first."""
    with get_connection() as conn:                            # open the database
        return conn.execute(
            "SELECT * FROM attendance ORDER BY date DESC, time DESC"  # most recent records at the top
        ).fetchall()                                          # all rows as a list


def get_student_attendance(student_id):
    """Return one student's attendance history, newest first."""
    with get_connection() as conn:                            # open the database
        return conn.execute(
            "SELECT date, time FROM attendance WHERE student_id = ? ORDER BY date DESC",
            (student_id,),                                    # only this student's rows
        ).fetchall()                                          # all their rows as a list


def attendance_count_today():
    """Count how many students were marked present today."""
    today = datetime.now().strftime("%Y-%m-%d")               # today's date as text
    with get_connection() as conn:                            # open the database
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM attendance WHERE date = ?",  # count rows stamped with today's date
            (today,),
        ).fetchone()                                          # single row holding the count
    return row["c"]                                           # pull the number out of the row
