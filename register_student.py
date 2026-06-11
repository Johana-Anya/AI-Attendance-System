# register_student.py

import cv2
import os

name = input("Enter Student Name: ")

os.makedirs("images", exist_ok=True)

cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()

    cv2.imshow("Register Face", frame)

    key = cv2.waitKey(1)

    if key == ord("s"):

        cv2.imwrite(
            f"images/{name}.jpg",
            frame
        )

        print("Saved")
        break

cap.release()
cv2.destroyAllWindows()