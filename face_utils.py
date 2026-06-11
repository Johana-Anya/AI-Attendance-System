# face_utils.py — everything to do with faces: loading the AI model, making embeddings, matching them

import os                                                     # built-in library for file paths
import pickle                                                 # built-in library that saves/loads Python objects to a file
import cv2                                                    # OpenCV — decodes images into pixel arrays
import numpy as np                                            # NumPy — fast math on those arrays

# absolute path to the embeddings file, kept next to this script
EMBEDDINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "embeddings.pkl")

# similarity needed to call two faces "the same person" (cosine similarity, 1.0 = identical)
MATCH_THRESHOLD = 0.40

_model = None                                                 # private slot so the heavy AI model is loaded only ONCE


def get_model():
    """Load the InsightFace model the first time it's needed, then reuse it."""
    global _model                                             # we want to write to the module-level variable above
    if _model is None:                                        # only do the slow loading once per app run
        from insightface.app import FaceAnalysis             # import here so the app starts fast
        _model = FaceAnalysis(                                # create the face detection + recognition pipeline
            name="buffalo_l",                                 # the standard high-accuracy model pack
            providers=["CPUExecutionProvider"],               # run on CPU (works on any machine, no GPU needed)
        )
        _model.prepare(ctx_id=0, det_size=(640, 640))         # warm the model up at 640x640 detection resolution
    return _model                                             # hand back the ready-to-use model


def embedding_from_image(img):
    """Take a decoded image array and return one face embedding (or None if no face)."""
    if img is None:                                           # the image failed to load/decode
        return None                                           # nothing we can do
    faces = get_model().get(img)                              # run face detection + recognition on the image
    if len(faces) == 0:                                       # the model found no face at all
        return None                                           # report failure instead of crashing  <-- original code crashed here
    largest = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))  # if several faces, keep the biggest one
    return largest.normed_embedding                           # the length-1 (normalized) 512-number fingerprint of the face


def embedding_from_bytes(image_bytes):
    """Same as above but starting from raw uploaded/camera bytes."""
    arr = np.frombuffer(image_bytes, dtype=np.uint8)          # wrap the raw bytes in a NumPy array
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)                 # decode JPEG/PNG bytes into a pixel array
    return embedding_from_image(img)                          # reuse the function above


def embedding_from_file(image_path):
    """Same as above but starting from an image file on disk."""
    img = cv2.imread(image_path)                              # read and decode the file in one step
    return embedding_from_image(img)                          # reuse the shared logic


def load_embeddings():
    """Read the saved {student_id: embedding} dictionary from disk."""
    if not os.path.exists(EMBEDDINGS_PATH):                   # no file yet (no students registered)
        return {}                                             # start with an empty dictionary
    with open(EMBEDDINGS_PATH, "rb") as f:                    # open the file in binary-read mode
        return pickle.load(f)                                 # turn the file back into a Python dictionary


def save_embeddings(embeddings):
    """Write the {student_id: embedding} dictionary to disk."""
    with open(EMBEDDINGS_PATH, "wb") as f:                    # open the file in binary-write mode
        pickle.dump(embeddings, f)                            # serialize the dictionary into the file


def add_embedding(student_id, embedding):
    """Add or replace one student's embedding in the saved file."""
    embeddings = load_embeddings()                            # read what we have so far
    embeddings[student_id] = embedding                        # insert/overwrite this student's fingerprint
    save_embeddings(embeddings)                               # write the updated dictionary back


def remove_embedding(student_id):
    """Delete one student's embedding from the saved file."""
    embeddings = load_embeddings()                            # read the current dictionary
    embeddings.pop(student_id, None)                          # remove the entry if present (no error if absent)
    save_embeddings(embeddings)                               # write the updated dictionary back


def match_face(embedding, embeddings=None):
    """Compare one face against every registered student; return (student_id, score) or (None, score)."""
    if embeddings is None:                                    # caller didn't pass the dictionary in
        embeddings = load_embeddings()                        # so load it from disk ourselves
    best_id, best_score = None, -1.0                          # start with "no match found yet"
    for student_id, stored in embeddings.items():             # walk through every registered face
        score = float(np.dot(embedding, stored))              # cosine similarity = dot product of normalized vectors  <-- replaces the fragile raw-distance check
        if score > best_score:                                # found a closer match than anything so far
            best_id, best_score = student_id, score           # remember it
    if best_score >= MATCH_THRESHOLD:                         # close enough to confidently say it's the same person
        return best_id, best_score                            # return the winner and how confident we are
    return None, best_score                                   # nobody was close enough — face not registered
