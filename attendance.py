import sqlite3
from datetime import datetime

def mark_attendance(name):

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")

    cursor.execute("""
    SELECT * FROM attendance
    WHERE name=? AND date=?
    """, (name,date))

    result = cursor.fetchone()

    if result is None:

        cursor.execute("""
        INSERT INTO attendance
        (name,date,time)
        VALUES (?,?,?)
        """,(name,date,time))

        conn.commit()

    conn.close()