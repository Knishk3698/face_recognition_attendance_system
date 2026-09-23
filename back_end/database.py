import sqlite3


DB_NAME = "database.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_table():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_no TEXT UNIQUE,
                name TEXT,
                batch TEXT,
                image_folder TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_no TEXT,
                date TEXT,
                time TEXT,
                confidence REAL,
                UNIQUE (roll_no, date),
                FOREIGN KEY (roll_no) REFERENCES students (roll_no)
            )
            """
        )
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS unique_attendance_per_day
            ON attendance (roll_no, date)
            """
        )
        conn.commit()
    except sqlite3.Error as error:
        print("Database error:", error)
    finally:
        conn.close()


def add_student(roll_no, name, batch, image_folder):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO students (roll_no, name, batch, image_folder)
            VALUES (?, ?, ?, ?)
            """,
            (roll_no, name, batch, image_folder),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print("Error: This roll number already exists.")
        return False
    except sqlite3.Error as error:
        print("Database error:", error)
        return False
    finally:
        conn.close()


def get_student_by_roll(roll_no):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, roll_no, name, batch, image_folder FROM students WHERE roll_no = ?",
            (roll_no,),
        )
        return cursor.fetchone()
    except sqlite3.Error as error:
        print("Database error:", error)
        return None
    finally:
        conn.close()


def get_all_students():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, roll_no, name, batch, image_folder FROM students")
        return cursor.fetchall()
    except sqlite3.Error as error:
        print("Database error:", error)
        return []
    finally:
        conn.close()


def mark_attendance(roll_no, confidence):
    from datetime import datetime

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO attendance (roll_no, date, time, confidence)
            VALUES (?, ?, ?, ?)
            """,
            (roll_no, date, time, confidence),
        )
        conn.commit()
        return True, f"Attendance marked for {roll_no}"
    except sqlite3.IntegrityError:
        return False, f"Attendance already marked today for {roll_no}"
    except sqlite3.Error as error:
        return False, f"Database error: {error}"
    finally:
        conn.close()


def get_student_attendance(roll_no, name, batch):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT s.roll_no, s.name, s.batch, a.date, a.time, a.confidence
            FROM students s
            LEFT JOIN attendance a ON a.roll_no = s.roll_no
            WHERE s.roll_no = ? AND lower(s.name) = lower(?) AND lower(s.batch) = lower(?)
            ORDER BY a.date DESC, a.time DESC
            """,
            (roll_no, name, batch),
        )
        return cursor.fetchall()
    except sqlite3.Error as error:
        print("Database error:", error)
        return []
    finally:
        conn.close()
