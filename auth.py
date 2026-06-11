# auth.py — password hashing and login checking (passwords are NEVER stored as plain text)

import hashlib                                                # built-in library with the PBKDF2 hashing function
import secrets                                                # built-in library for cryptographically secure random salts

import db                                                     # our own database module (db.py)

ITERATIONS = 200_000                                          # how many times PBKDF2 re-hashes — high number = slow to crack


def hash_password(password, salt=None):
    """Turn a plain password into 'salt$hash' text that is safe to store."""
    if salt is None:                                          # no salt supplied means we are creating a brand-new hash
        salt = secrets.token_hex(16)                          # generate 16 random bytes as 32 hex characters
    digest = hashlib.pbkdf2_hmac(                             # run the PBKDF2 key-derivation function
        "sha256",                                             # underlying hash algorithm
        password.encode(),                                    # the password as bytes
        salt.encode(),                                        # the salt as bytes (makes identical passwords hash differently)
        ITERATIONS,                                           # number of rounds
    ).hex()                                                   # convert the raw bytes to readable hex text
    return f"{salt}${digest}"                                 # store salt and hash together, separated by '$'


def verify_password(password, stored):
    """Check a typed password against the stored 'salt$hash' string."""
    try:                                                      # guard against a malformed stored value
        salt, _ = stored.split("$")                           # recover the salt that was used originally
    except ValueError:                                        # stored value didn't contain a '$'
        return False                                          # treat malformed data as a failed login
    return secrets.compare_digest(                            # constant-time comparison (defeats timing attacks)
        hash_password(password, salt),                        # re-hash the typed password with the SAME salt
        stored,                                               # and compare with what's in the database
    )


def login(username, password):
    """Return the user's role ('admin'/'student') if credentials are right, else None."""
    user = db.get_user(username)                              # fetch the account row from the database
    if user is None:                                          # no such username
        return None                                           # login fails
    if not verify_password(password, user["password_hash"]):  # password doesn't match the stored hash
        return None                                           # login fails
    return user                                               # success — give the caller the full user row
