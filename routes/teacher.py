from flask import Blueprint, render_template

from services.database import get_db_connection


teacher = Blueprint(
    "teacher",
    __name__,
    url_prefix="/teacher"
)


@teacher.route("/dashboard")
def dashboard():

    connection = get_db_connection()
    cursor = connection.cursor()

    # Total students
    cursor.execute("SELECT COUNT(*) FROM students")
    student_count = cursor.fetchone()[0]

    # Total materials
    cursor.execute("SELECT COUNT(*) FROM materials")
    material_count = cursor.fetchone()[0]

    # Total tests
    cursor.execute("SELECT COUNT(*) FROM tests")
    test_count = cursor.fetchone()[0]

    # Student list
    cursor.execute("""
        SELECT
            u.name,
            c.career_name
        FROM students AS s
        JOIN users AS u
            ON s.user_id = u.user_id
        LEFT JOIN careers AS c
            ON s.career_id = c.career_id
        ORDER BY s.student_id
    """)

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "teacher/dashboard.html",
        student_count=student_count,
        material_count=material_count,
        test_count=test_count,
        students=students
    )