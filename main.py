from database import add_student, create_table, get_all_students, get_student_by_roll
from dataset_manager import capture_images, create_student_folder


def add_student_flow():
    roll_no = input("Enter roll number: ").strip()
    name = input("Enter student name: ").strip()
    batch = input("Enter batch: ").strip()

    if not roll_no or not name or not batch:
        print("Error: Roll number, name, and batch are required.")
        return

    if get_student_by_roll(roll_no):
        print("Error: Student with this roll number already exists.")
        return

    try:
        folder_path = create_student_folder(roll_no, name)
    except Exception as error:
        print("Error:", error)
        return

    if add_student(roll_no, name, batch, folder_path):
        print("Student added successfully.")
        print("Image folder:", folder_path)


def capture_images_flow():
    roll_no = input("Enter roll number: ").strip()
    student = get_student_by_roll(roll_no)

    if not student:
        print("Error: Student not found.")
        return

    image_folder = student[4]
    capture_images(image_folder, total_images=15)


def display_students():
    students = get_all_students()

    if not students:
        print("No students found.")
        return

    print("\nStudents:")
    print("-" * 80)
    for student in students:
        print(
            f"ID: {student[0]} | Roll No: {student[1]} | "
            f"Name: {student[2]} | Batch: {student[3]} | Folder: {student[4]}"
        )
    print("-" * 80)


def main():
    create_table()

    while True:
        print("\nFacial Recognition Attendance - Student Module")
        print("1. Add Student")
        print("2. Capture Images")
        print("3. Display Students")
        print("4. Exit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            add_student_flow()
        elif choice == "2":
            capture_images_flow()
        elif choice == "3":
            display_students()
        elif choice == "4":
            print("Exiting.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
