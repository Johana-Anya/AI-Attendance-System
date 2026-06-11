import face_recognition
import cv2
import os
import numpy as np

known_encodings = []
known_names = []

path = "images"

for image_name in os.listdir(path):
    image = face_recognition.load_image_file(
        f"{path}/{image_name}"
    )

    encoding = face_recognition.face_encodings(image)[0]

    known_encodings.append(encoding)
    known_names.append(
        os.path.splitext(image_name)[0]
    )

cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    faces = face_recognition.face_locations(rgb)

    encodings = face_recognition.face_encodings(
        rgb,
        faces
    )

    for face_encoding, face_location in zip(
        encodings,
        faces
    ):

        matches = face_recognition.compare_faces(
            known_encodings,
            face_encoding
        )

        name = "Unknown"

        face_distance = face_recognition.face_distance(
            known_encodings,
            face_encoding
        )

        best_match = np.argmin(face_distance)

        if matches[best_match]:
            name = known_names[best_match]

        top, right, bottom, left = face_location

        cv2.rectangle(
            frame,
            (left, top),
            (right, bottom),
            (0,255,0),
            2
        )

        cv2.putText(
            frame,
            name,
            (left, top-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2
        )

    cv2.imshow("Attendance", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()