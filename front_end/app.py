import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk

import cv2
import face_recognition
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from back_end.database import (
    add_student,
    create_table,
    get_all_students,
    get_student_attendance,
    get_student_by_roll,
    mark_attendance,
)
from back_end.dataset_manager import create_student_folder


def load_known_faces():
    known_encodings = []
    known_roll_numbers = []

    for student in get_all_students():
        roll_no = student[1]
        image_folder = student[4]

        if not os.path.isdir(image_folder):
            continue

        for image_name in os.listdir(image_folder):
            image_path = os.path.join(image_folder, image_name)
            image = cv2.imread(image_path)

            if image is None:
                continue

            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(rgb_image)

            if encodings:
                known_encodings.append(encodings[0])
                known_roll_numbers.append(roll_no)

    return known_encodings, known_roll_numbers


def open_mark_attendance():
    known_encodings, known_roll_numbers = load_known_faces()

    if not known_encodings:
        messagebox.showerror("No Images", "Please add a student and capture images first.")
        return

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        messagebox.showerror("Camera Error", "Webcam could not be opened.")
        return

    window_name = "Mark Attendance"
    cv2.namedWindow(window_name)

    while True:
        success, frame = camera.read()

        if not success:
            break

        small_frame = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(small_frame)
        face_encodings = face_recognition.face_encodings(small_frame, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_index = np.argmin(distances)
            matches = face_recognition.compare_faces(known_encodings, face_encoding)

            if matches[best_index]:
                roll_no = known_roll_numbers[best_index]
                confidence = max(0, min(1, 1 - float(distances[best_index])))
                marked, message = mark_attendance(roll_no, confidence)

                top, right, bottom, left = face_location
                top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f"{roll_no} {confidence:.2f}",
                    (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75,
                    (255, 255, 255),
                    2,
                )

                if marked:
                    print(message)

        cv2.imshow(window_name, frame)
        key = cv2.waitKey(1)

        try:
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                break
        except cv2.error:
            break

        if key == ord("q") or key == 27:
            break

    camera.release()
    cv2.destroyAllWindows()


def capture_student_images(folder_path, total_images=25):
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        messagebox.showerror("Camera Error", "Webcam could not be opened.")
        return False

    count = 0
    window_name = "Capture Student Images"
    cv2.namedWindow(window_name)

    while count < total_images:
        success, frame = camera.read()

        if not success:
            break

        cv2.putText(
            frame,
            f"Press SPACE to capture: {count}/{total_images}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

        cv2.imshow(window_name, frame)
        key = cv2.waitKey(1)

        try:
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                break
        except cv2.error:
            break

        if key == 32:
            count += 1
            image_path = os.path.join(folder_path, f"img{count}.jpg")
            cv2.imwrite(image_path, frame)
        elif key == ord("q") or key == 27:
            break

    camera.release()
    cv2.destroyAllWindows()
    return count > 0


def open_add_student():
    window = tk.Toplevel(root)
    window.title("Add Student")
    window.geometry("360x330")
    window.resizable(False, False)

    tk.Label(window, text="Name").pack(pady=(20, 4))
    name_entry = tk.Entry(window, width=32)
    name_entry.pack()

    tk.Label(window, text="Roll No").pack(pady=(12, 4))
    roll_entry = tk.Entry(window, width=32)
    roll_entry.pack()

    tk.Label(window, text="Batch").pack(pady=(12, 4))
    batch_entry = tk.Entry(window, width=32)
    batch_entry.pack()

    status_label = tk.Label(window, text="Images not captured", fg="red")
    status_label.pack(pady=12)

    student_data = {"folder": None}

    def capture_images():
        name = name_entry.get().strip()
        roll_no = roll_entry.get().strip()
        batch = batch_entry.get().strip()

        if not name or not roll_no or not batch:
            messagebox.showerror("Missing Details", "Enter name, roll no, and batch first.")
            return

        if get_student_by_roll(roll_no):
            messagebox.showerror("Duplicate", "This roll number already exists.")
            return

        try:
            folder_path = create_student_folder(roll_no, name)
        except Exception as error:
            messagebox.showerror("Folder Error", str(error))
            return

        if capture_student_images(folder_path, total_images=15):
            student_data["folder"] = folder_path
            status_label.config(text="Images captured", fg="green")
        else:
            messagebox.showerror("Image Error", "No images were captured.")

    def save_student():
        name = name_entry.get().strip()
        roll_no = roll_entry.get().strip()
        batch = batch_entry.get().strip()

        if not name or not roll_no or not batch:
            messagebox.showerror("Missing Details", "Enter name, roll no, and batch.")
            return

        if not student_data["folder"]:
            messagebox.showerror("Missing Images", "Capture student images first.")
            return

        if add_student(roll_no, name, batch, student_data["folder"]):
            messagebox.showinfo("Saved", "Student saved successfully.")
            window.destroy()

    tk.Button(window, text="Capture Images", command=capture_images, width=22).pack(pady=8)
    tk.Button(window, text="Save Student", command=save_student, width=22).pack(pady=8)


def open_check_attendance():
    window = tk.Toplevel(root)
    window.title("Check Attendance")
    window.geometry("760x460")

    form = tk.Frame(window)
    form.pack(pady=12)

    tk.Label(form, text="Name").grid(row=0, column=0, padx=5)
    name_entry = tk.Entry(form, width=18)
    name_entry.grid(row=0, column=1, padx=5)

    tk.Label(form, text="Roll No").grid(row=0, column=2, padx=5)
    roll_entry = tk.Entry(form, width=18)
    roll_entry.grid(row=0, column=3, padx=5)

    tk.Label(form, text="Batch").grid(row=0, column=4, padx=5)
    batch_entry = tk.Entry(form, width=18)
    batch_entry.grid(row=0, column=5, padx=5)

    columns = ("date", "time", "confidence")
    table = ttk.Treeview(window, columns=columns, show="headings")
    table.heading("date", text="Date")
    table.heading("time", text="Time")
    table.heading("confidence", text="Confidence")
    table.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    def search():
        for item in table.get_children():
            table.delete(item)

        name = name_entry.get().strip()
        roll_no = roll_entry.get().strip()
        batch = batch_entry.get().strip()

        if not name or not roll_no or not batch:
            messagebox.showerror("Missing Details", "Enter name, roll no, and batch.")
            return

        records = get_student_attendance(roll_no, name, batch)

        if not records:
            messagebox.showinfo("No Record", "No student or attendance record found.")
            return

        for record in records:
            if record[3] is not None:
                table.insert("", tk.END, values=(record[3], record[4], f"{record[5]:.2f}"))

    tk.Button(form, text="Search", command=search).grid(row=0, column=6, padx=8)


create_table()

root = tk.Tk()
root.title("Face Attendance System")
root.geometry("430x320")
root.resizable(False, False)

tk.Label(root, text="Face Attendance System", font=("Arial", 18, "bold")).pack(pady=28)

tk.Button(root, text="1. Mark Attendance", command=open_mark_attendance, width=30, height=2).pack(pady=8)
tk.Button(root, text="2. Add Student", command=open_add_student, width=30, height=2).pack(pady=8)
tk.Button(root, text="3. Check Attendance", command=open_check_attendance, width=30, height=2).pack(pady=8)

tk.Label(root, text="Press q or Esc to close webcam windows.").pack(pady=14)

root.mainloop()
