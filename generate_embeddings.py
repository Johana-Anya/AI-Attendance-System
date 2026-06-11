# generate_embeddings.py — rebuilds embeddings.pkl from every photo in images/
# normally not needed (registration saves embeddings live) — use this to recover after losing the .pkl file
# run it with:  python generate_embeddings.py

import os                                                     # built-in library for listing files

import face_utils                                             # our face module (model + save/load helpers)

IMAGES_DIR = "images"                                         # folder holding one photo per student, named <student_id>.jpg

embeddings = {}                                               # will hold {student_id: face fingerprint}

for filename in os.listdir(IMAGES_DIR):                       # walk through every file in the images folder
    student_id = os.path.splitext(filename)[0]                # '23AIDS001.jpg' → '23AIDS001'
    path = os.path.join(IMAGES_DIR, filename)                 # full path to the photo
    embedding = face_utils.embedding_from_file(path)          # photo → face fingerprint (None if no face found)
    if embedding is None:                                     # the model could not find a face in this photo
        print(f"  ✗ {filename}: no face detected, skipped")   # report it instead of crashing
        continue                                              # move on to the next photo
    embeddings[student_id] = embedding                        # store this student's fingerprint
    print(f"  ✓ {filename}: embedded")                        # progress line per photo

face_utils.save_embeddings(embeddings)                        # write the whole dictionary to embeddings.pkl

print(f"Done — {len(embeddings)} embedding(s) saved to {face_utils.EMBEDDINGS_PATH}")  # summary
