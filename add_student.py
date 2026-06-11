import sqlite3

conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

cursor.execute("""
INSERT INTO students
(student_id,name,department)
VALUES
('23AIDS001','Johana','AI & DS')
""")

conn.commit()
conn.close()

print("Student Added")