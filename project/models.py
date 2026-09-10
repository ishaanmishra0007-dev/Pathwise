from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column("user_id", db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column("password", db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    student = db.relationship(
        "Student",
        back_populates="user",
        uselist=False
    )

    teacher = db.relationship(
        "Teacher",
        back_populates="user",
        uselist=False
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class CareerPath(db.Model):
    __tablename__ = "careers"

    id = db.Column("career_id", db.Integer, primary_key=True)
    name = db.Column("career_name", db.String(100), nullable=False)
    description = db.Column(db.Text)

    courses = db.relationship(
        "Course",
        back_populates="career",
        lazy=True
    )


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column("course_id", db.Integer, primary_key=True)
    career_id = db.Column(
        db.Integer,
        db.ForeignKey("careers.career_id")
    )
    name = db.Column("course_name", db.String(150), nullable=False)

    career = db.relationship(
        "CareerPath",
        back_populates="courses"
    )

    topics = db.relationship(
        "Topic",
        back_populates="course",
        lazy=True
    )


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(
        "student_id",
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    career_id = db.Column(
        db.Integer,
        db.ForeignKey("careers.career_id"),
        nullable=True
    )

    # Beginner / Intermediate / Advanced
    skill_level = db.Column(
        db.String(20),
        nullable=True
    )

    user = db.relationship(
        "User",
        back_populates="student"
    )

    career = db.relationship(
        "CareerPath"
    )

    progress = db.relationship(
        "StudentProgress",
        back_populates="student",
        lazy=True
    )

    quiz_results = db.relationship(
        "QuizResult",
        back_populates="student",
        lazy=True
    )

    certificates = db.relationship(
        "Certificate",
        back_populates="student",
        lazy=True
    )


class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(
        "teacher_id",
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="teacher"
    )


class Topic(db.Model):
    __tablename__ = "topics"

    id = db.Column(
        "topic_id",
        db.Integer,
        primary_key=True
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.course_id")
    )

    name = db.Column(
        "topic_name",
        db.String(150),
        nullable=False
    )

    order = db.Column(
        "topic_order",
        db.Integer,
        default=0
    )

    course = db.relationship(
        "Course",
        back_populates="topics"
    )

    materials = db.relationship(
        "LearningMaterial",
        back_populates="topic",
        lazy=True
    )

    progress = db.relationship(
        "StudentProgress",
        back_populates="topic",
        lazy=True
    )


class LearningMaterial(db.Model):
    __tablename__ = "materials"

    id = db.Column(
        "material_id",
        db.Integer,
        primary_key=True
    )

    topic_id = db.Column(
        db.Integer,
        db.ForeignKey("topics.topic_id")
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("teachers.teacher_id")
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(db.Text)

    file_path = db.Column(
        db.String(300)
    )

    created_at = db.Column(
        db.DateTime
    )

    topic = db.relationship(
        "Topic",
        back_populates="materials"
    )


class Test(db.Model):
    __tablename__ = "tests"

    id = db.Column(
        "test_id",
        db.Integer,
        primary_key=True
    )

    topic_id = db.Column(
        db.Integer,
        db.ForeignKey("topics.topic_id")
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("teachers.teacher_id")
    )

    name = db.Column(
        "test_name",
        db.String(200),
        nullable=False
    )

    questions = db.relationship(
        "QuizQuestion",
        back_populates="test",
        lazy=True
    )


class QuizQuestion(db.Model):
    __tablename__ = "questions"

    id = db.Column(
        "question_id",
        db.Integer,
        primary_key=True
    )

    test_id = db.Column(
        db.Integer,
        db.ForeignKey("tests.test_id")
    )

    text = db.Column(
        "question_text",
        db.Text,
        nullable=False
    )

    option_a = db.Column(
        db.String(255)
    )

    option_b = db.Column(
        db.String(255)
    )

    option_c = db.Column(
        db.String(255)
    )

    option_d = db.Column(
        db.String(255)
    )

    correct_answer = db.Column(
        db.String(1)
    )

    test = db.relationship(
        "Test",
        back_populates="questions"
    )


class StudentProgress(db.Model):
    __tablename__ = "student_progress"

    id = db.Column(
        "progress_id",
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.student_id")
    )

    topic_id = db.Column(
        db.Integer,
        db.ForeignKey("topics.topic_id")
    )

    status = db.Column(
        db.String(50)
    )

    student = db.relationship(
        "Student",
        back_populates="progress"
    )

    topic = db.relationship(
        "Topic",
        back_populates="progress"
    )


class QuizResult(db.Model):
    __tablename__ = "quiz_results"

    id = db.Column(
        "quiz_result_id",
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.student_id")
    )

    score = db.Column(
        db.Integer
    )

    recommended_career_id = db.Column(
        db.Integer,
        db.ForeignKey("careers.career_id")
    )

    attempted_at = db.Column(
        db.DateTime
    )

    student = db.relationship(
        "Student",
        back_populates="quiz_results"
    )

    recommended_career = db.relationship(
        "CareerPath"
    )


class Certificate(db.Model):
    __tablename__ = "certificates"

    id = db.Column(
        "certificate_id",
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.student_id")
    )

    certificate_type = db.Column(
        db.String(100)
    )

    issue_date = db.Column(
        db.Date
    )

    certificate_path = db.Column(
        db.String(300)
    )

    student = db.relationship(
        "Student",
        back_populates="certificates"
    )