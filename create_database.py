# create_database.py — one-time setup: builds the tables and seeds the admin login
# run it with:  python create_database.py

import auth                                                   # our password-hashing module
import db                                                     # our database module

db.init_db()                                                  # create users / students / attendance tables if missing

ADMIN_USER = "admin"                                          # the default admin username
ADMIN_PASS = "admin123"                                       # the default admin password (change it after first login!)

if db.get_user(ADMIN_USER) is None:                           # only seed if no admin account exists yet
    db.create_user(                                           # insert the admin login row
        ADMIN_USER,                                           # username
        auth.hash_password(ADMIN_PASS),                       # store the salted HASH, never the plain password
        "admin",                                              # role
    )
    print(f"Admin account created: {ADMIN_USER} / {ADMIN_PASS}")  # tell the person running the script
else:                                                         # an admin already exists
    print("Admin account already exists - nothing to do.")    # no changes made

print("Database ready at:", db.DB_PATH)                       # show exactly which file was created
