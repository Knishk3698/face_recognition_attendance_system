# Face Attendance System

A Python face-recognition attendance system that uses a webcam to register students, capture face images, recognize known students, and store daily attendance records in SQLite.

## Features

- Add students with roll number, name, batch, and captured face images
- Capture training images from a webcam
- Mark attendance using real-time face recognition
- Prevent duplicate attendance for the same student on the same date
- Search student attendance history from the desktop UI
- Store student and attendance data locally in SQLite

## Tech Stack

- Python
- Tkinter
- OpenCV
- face_recognition
- NumPy
- SQLite

## Project Structure

```text
.
|-- back_end/
|   |-- __init__.py
|   |-- database.py          # SQLite schema and database helpers
|   |-- dataset_manager.py   # Dataset folder and webcam image capture helpers
|   `-- main.py              # Command-line student management flow
|-- front_end/
|   |-- __init__.py
|   `-- app.py               # Tkinter desktop application
|-- requirements.txt         # Python dependencies
|-- README.md
`-- .gitignore
```

Runtime files such as `database.db`, `dataset/`, virtual environments, and Python cache folders are intentionally ignored by Git.

## Requirements

- Python 3.10 or later recommended
- A working webcam
- CMake/build tools may be required for installing `face-recognition` and its `dlib` dependency on some systems

## Setup

1. Clone the repository:

```bash
git clone https://github.com/Knishk3698/face_recognition_attendance_system.git
cd face_recognition_attendance_system
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Start the desktop application:

```bash
python front_end/app.py
```

The app provides options to:

- Mark attendance
- Add a student and capture face images
- Check attendance records

You can also run the command-line student module:

```bash
python -m back_end.main
```

## Notes

- The SQLite database is created automatically as `database.db`.
- Student face images are saved under `dataset/`.
- Press `q` or `Esc` to close webcam windows.
- Attendance is limited to one record per student per day.
