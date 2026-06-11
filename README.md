# VERIFACE — AI Face-Recognition Attendance System

A Streamlit app where an **admin** registers students with a webcam photo, and **students**
log in and mark attendance by scanning their face. Built on InsightFace embeddings +
cosine-similarity matching, with an SQLite database.

## Quick start

```bash
# 1. install dependencies
pip install -r requirements.txt

# 2. create the database + default admin account (admin / admin123)
python create_database.py

# 3. run the app
streamlit run App.py
```

## How it works

| Piece | Job |
|---|---|
| `App.py` | Login page — routes admins and students to their consoles |
| `pages/Admin_Dashboard.py` | Stats, student registration (webcam), records, CSV export, analytics |
| `pages/Student_Dashboard.py` | Face-scan check-in kiosk + personal history |
| `db.py` | All SQLite work: tables, queries, the one-record-per-day rule |
| `auth.py` | PBKDF2 password hashing + login verification |
| `face_utils.py` | InsightFace model, embeddings, cosine-similarity matching |
| `ui.py` | The shared dark "biometric terminal" theme + custom components |
| `create_database.py` | One-time setup: tables + seeded admin account |
| `generate_embeddings.py` | Disaster recovery: rebuild `embeddings.pkl` from `images/` |

## The flow

1. **Admin** logs in (`admin / admin123` — change it), opens *Register Student*,
   fills in ID/name/department, captures a face photo, sets an initial password.
   The student's login username is their student ID.
2. **Student** logs in, captures their face. The app embeds the photo, finds the
   closest registered face by cosine similarity (threshold 0.40), checks it matches
   the *logged-in* account, and inserts one attendance row — at most once per day
   (enforced by a database UNIQUE constraint, not just app logic).
3. **Admin** watches the Overview trend, filters/downloads records as CSV, and
   reads per-student attendance percentages under Analytics.

## Security notes

- Passwords are stored as salted PBKDF2-SHA256 hashes — never plain text.
- Every page checks `st.session_state.role` and blocks unauthenticated access.
- A student can only mark **their own** attendance: the matched face must belong
  to the logged-in account.
- `attendance.db`, `embeddings.pkl` and `images/` are git-ignored (personal/biometric data).

## Known limitations

- No liveness detection — a printed photo could fool it. InsightFace's anti-spoofing
  model would be the next upgrade.
- One photo per student; averaging 3–5 captures would improve match robustness.
- SQLite suits a single classroom; move to Postgres for multi-site deployments.
