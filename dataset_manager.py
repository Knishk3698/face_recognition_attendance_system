import os
import re

import cv2


DATASET_DIR = "dataset"


def clean_folder_text(text):
    text = text.strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_-]", "", text)


def create_student_folder(roll_no, name):
    safe_roll_no = clean_folder_text(roll_no)
    safe_name = clean_folder_text(name)

    if not safe_roll_no or not safe_name:
        raise ValueError("Roll number and name must contain valid characters.")

    os.makedirs(DATASET_DIR, exist_ok=True)
    folder_path = os.path.join(DATASET_DIR, f"{safe_roll_no}_{safe_name}")

    if os.path.exists(folder_path):
        raise FileExistsError("Student folder already exists. Folder was not overwritten.")

    os.makedirs(folder_path)
    return folder_path


def capture_images(folder_path, total_images=15):
    if not os.path.isdir(folder_path):
        print("Error: Student folder does not exist.")
        return False

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Error: Webcam could not be opened.")
        return False

    face_detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    count = 0
    print("Webcam started.")
    print("Keep your face visible. Press q to stop early.")

    while count < total_images:
        success, frame = camera.read()

        if not success:
            print("Error: Could not read from webcam.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

        for (x, y, w, h) in faces:
            count += 1
            face_image = frame[y : y + h, x : x + w]
            image_path = os.path.join(folder_path, f"img{count}.jpg")
            cv2.imwrite(image_path, face_image)

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"Captured {count}/{total_images}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

            if count >= total_images:
                break

        cv2.imshow("Capture Student Images", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        try:
            if cv2.getWindowProperty("Capture Student Images", cv2.WND_PROP_VISIBLE) < 1:
                break
        except cv2.error:
            break

    camera.release()
    cv2.destroyAllWindows()

    print(f"Captured {count} images.")
    return count > 0
