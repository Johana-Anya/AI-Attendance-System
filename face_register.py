import cv2
import os

name = input("Enter Student Name: ")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    cv2.imshow("Capture Face", frame)

    key = cv2.waitKey(1)

    if key == ord('s'):
        os.makedirs("images", exist_ok=True)

        cv2.imwrite(f"images/{name}.jpg", frame)
        print("Face Saved")
        break

cap.release()
cv2.destroyAllWindows()
st.sidebar.title("Student Registration")

name = st.sidebar.text_input(
    "Student Name"
)

image = st.sidebar.camera_input(
    "Take Photo"
)

if st.sidebar.button("Save Student"):

    if image:

        with open(
            f"images/{name}.jpg",
            "wb"
        ) as f:

            f.write(image.getbuffer())

        st.success("Student Saved")