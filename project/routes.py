from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from . import db
from .models import (
    User,
    Student,
    CareerPath,
    Course,
    Topic,
    LearningMaterial,
    Test,
    QuizQuestion,
    QuizResult,
    Certificate,
    StudentProgress
)


bp = Blueprint("main", __name__)


# =========================================================
# HOME
# =========================================================

@bp.route("/")
def index():
    return render_template("index.html")


# =========================================================
# REGISTER
# =========================================================

@bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not name or not email or not password:
            flash("Please fill all required fields.", "error")
            return redirect(url_for("main.register"))

        # Student portal only
        role = "student"

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            flash(
                "Email already registered. Please login.",
                "error"
            )
            return redirect(url_for("main.login"))

        new_user = User(
            name=name,
            email=email,
            role=role
        )

        new_user.set_password(password)

        db.session.add(new_user)

        # Generate user ID
        db.session.flush()

        student = Student(
            user_id=new_user.id
        )

        db.session.add(student)

        db.session.commit()

        flash(
            "Account created successfully. Please login.",
            "success"
        )

        return redirect(
            url_for("main.login")
        )

    return render_template("register.html")


# =========================================================
# LOGIN
# =========================================================

@bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        user = User.query.filter_by(
            email=email
        ).first()

        if user and user.check_password(password):

            login_user(user)

            flash(
                "Logged in successfully.",
                "success"
            )

            return redirect(
                url_for("main.student_dashboard")
            )

        flash(
            "Invalid email or password.",
            "error"
        )

        return redirect(
            url_for("main.login")
        )

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@bp.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "Logged out successfully.",
        "success"
    )

    return redirect(
        url_for("main.index")
    )


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@bp.route("/student/dashboard")
@login_required
def student_dashboard():

    if current_user.role != "student":

        flash(
            "Access denied.",
            "error"
        )

        return redirect(
            url_for("main.index")
        )

    student = current_user.student

    career = None
    courses = []
    materials = []

    if student and student.career:

        career = student.career

        courses = (
            Course.query
            .filter_by(career_id=career.id)
            .order_by(Course.id)
            .all()
        )

        for course in courses:

            topics = (
                Topic.query
                .filter_by(course_id=course.id)
                .order_by(Topic.order)
                .all()
            )

            for topic in topics:

                topic_materials = (
                    LearningMaterial.query
                    .filter_by(topic_id=topic.id)
                    .all()
                )

                materials.extend(
                    topic_materials
                )

    return render_template(
        "student_dashboard.html",
        student=student,
        career=career,
        courses=courses,
        materials=materials
    )


# =========================================================
# I KNOW MY CAREER
# CAREER SELECTION
# =========================================================

@bp.route(
    "/student/career",
    methods=["GET", "POST"]
)
@login_required
def select_career():

    if current_user.role != "student":

        flash(
            "Access denied.",
            "error"
        )

        return redirect(
            url_for("main.index")
        )

    student = current_user.student

    if not student:

        flash(
            "Student profile not found.",
            "error"
        )

        return redirect(
            url_for("main.student_dashboard")
        )

    careers = (
        CareerPath.query
        .order_by(CareerPath.id)
        .all()
    )

    if request.method == "POST":

        career_id = request.form.get(
            "career_id"
        )

        if not career_id:

            flash(
                "Please select a career.",
                "error"
            )

            return redirect(
                url_for("main.select_career")
            )

        try:

            career_id = int(career_id)

        except ValueError:

            flash(
                "Invalid career selected.",
                "error"
            )

            return redirect(
                url_for("main.select_career")
            )

        career = db.session.get(
            CareerPath,
            career_id
        )

        if not career:

            flash(
                "Invalid career selected.",
                "error"
            )

            return redirect(
                url_for("main.select_career")
            )

        student.career_id = career.id

        # Reset skill level for new career
        student.skill_level = None

        db.session.commit()

        flash(
            f"Career selected: {career.name}",
            "success"
        )

        return redirect(
            url_for(
                "main.skill_assessment",
                career_id=career.id
            )
        )

    return render_template(
        "select_career.html",
        careers=careers
    )


# =========================================================
# I KNOW MY CAREER
# 5-QUESTION SKILL ASSESSMENT
# =========================================================

@bp.route(
    "/student/assessment/<int:career_id>",
    methods=["GET", "POST"]
)
@login_required
def skill_assessment(career_id):

    if current_user.role != "student":

        flash(
            "Access denied.",
            "error"
        )

        return redirect(
            url_for("main.index")
        )

    student = current_user.student

    if not student:

        flash(
            "Student profile not found.",
            "error"
        )

        return redirect(
            url_for("main.student_dashboard")
        )

    career = db.session.get(
        CareerPath,
        career_id
    )

    if not career:

        flash(
            "Career not found.",
            "error"
        )

        return redirect(
            url_for("main.student_dashboard")
        )

    # -----------------------------------------------------
    # Find courses for this career
    # -----------------------------------------------------

    all_courses = (
        Course.query
        .filter_by(career_id=career.id)
        .order_by(Course.id)
        .all()
    )

    # Remove duplicate courses
    courses = []
    seen_course_names = set()

    for course in all_courses:

        if course.name not in seen_course_names:

            courses.append(course)

            seen_course_names.add(
                course.name
            )

    questions = []

    # -----------------------------------------------------
    # Career
    #   ↓
    # Course
    #   ↓
    # Topic
    #   ↓
    # Test
    #   ↓
    # Question
    # -----------------------------------------------------

    for course in courses:

        topics = (
            Topic.query
            .filter_by(course_id=course.id)
            .order_by(Topic.order)
            .all()
        )

        for topic in topics:

            tests = (
                Test.query
                .filter_by(topic_id=topic.id)
                .order_by(Test.id)
                .all()
            )

            for test in tests:

                test_questions = (
                    QuizQuestion.query
                    .filter_by(test_id=test.id)
                    .order_by(QuizQuestion.id)
                    .all()
                )

                questions.extend(
                    test_questions
                )

    # -----------------------------------------------------
    # Remove duplicate questions
    # -----------------------------------------------------

    unique_questions = {}

    for question in questions:

        unique_questions[
            question.id
        ] = question

    questions = list(
        unique_questions.values()
    )

    # -----------------------------------------------------
    # ONLY SHOW 5 QUESTIONS
    #
    # Other questions remain in PostgreSQL
    # for future topic tests.
    # -----------------------------------------------------

    questions = questions[:5]

    # -----------------------------------------------------
    # SUBMIT ASSESSMENT
    # -----------------------------------------------------

    if request.method == "POST":

        correct = 0

        for question in questions:

            answer = request.form.get(
                f"question_{question.id}"
            )

            if (
                answer
                and question.correct_answer
                and answer.upper()
                == question.correct_answer.upper()
            ):

                correct += 1

        total_questions = len(
            questions
        )

        if total_questions == 0:

            flash(
                "No assessment questions are available for this career.",
                "error"
            )

            return redirect(
                url_for(
                    "main.select_career"
                )
            )

        # -------------------------------------------------
        # Calculate score
        # -------------------------------------------------

        score = round(
            (correct / total_questions) * 100
        )

        # -------------------------------------------------
        # Determine skill level
        # -------------------------------------------------

        if score < 40:

            level = "Beginner"

        elif score < 70:

            level = "Intermediate"

        else:

            level = "Advanced"

        # -------------------------------------------------
        # Save career and skill level
        # -------------------------------------------------

        student.career_id = career.id
        student.skill_level = level

        # -------------------------------------------------
        # Save assessment result
        # -------------------------------------------------

        result = QuizResult(
            student_id=student.id,
            score=score,
            recommended_career_id=career.id,
            attempted_at=datetime.utcnow()
        )

        db.session.add(result)

        db.session.commit()

        return render_template(
            "assessment_result.html",
            career=career,
            score=score,
            level=level
        )

    # -----------------------------------------------------
    # SHOW ASSESSMENT
    # -----------------------------------------------------

    return render_template(
        "skill_assessment.html",
        career=career,
        questions=questions
    )


# =========================================================
# PERSONALIZED LEARNING PATH
# =========================================================

@bp.route("/student/learning-path")
@login_required
def learning_path():

    if current_user.role != "student":

        flash(
            "Access denied.",
            "error"
        )

        return redirect(
            url_for("main.index")
        )

    student = current_user.student

    if not student:

        flash(
            "Student profile not found.",
            "error"
        )

        return redirect(
            url_for("main.index")
        )

    if not student.career:

        flash(
            "Please select a career first.",
            "warning"
        )

        return redirect(
            url_for("main.select_career")
        )

    career = student.career

    level = student.skill_level or "Beginner"

    # -----------------------------------------------------
    # GET COURSES
    # -----------------------------------------------------

    all_courses = (
        Course.query
        .filter_by(career_id=career.id)
        .order_by(Course.id)
        .all()
    )

    # Remove duplicate courses
    courses = []
    seen_course_names = set()

    for course in all_courses:

        if course.name not in seen_course_names:

            courses.append(course)

            seen_course_names.add(
                course.name
            )

    learning_path_data = []

    # -----------------------------------------------------
    # BUILD LEARNING PATH
    # -----------------------------------------------------

    for course in courses:

        topics = (
            Topic.query
            .filter_by(course_id=course.id)
            .order_by(Topic.order)
            .all()
        )

        if not topics:
            continue

        # Beginner
        if level == "Beginner":

            selected_topics = topics

            start_message = (
                "Start with the fundamentals and "
                "build your knowledge step by step."
            )

        # Intermediate
        elif level == "Intermediate":

            if len(topics) > 1:
                selected_topics = topics[1:]
            else:
                selected_topics = topics

            start_message = (
                "You already have some knowledge, "
                "so you can move faster through the basics."
            )

        # Advanced
        else:

            if len(topics) > 1:
                selected_topics = topics[1:]
            else:
                selected_topics = topics

            start_message = (
                "Focus on practical and advanced concepts. "
                "Review fundamentals whenever necessary."
            )

        # -------------------------------------------------
        # CREATE PROGRESS RECORDS
        # -------------------------------------------------

        for topic in selected_topics:

            existing_progress = (
                StudentProgress.query
                .filter_by(
                    student_id=student.id,
                    topic_id=topic.id
                )
                .first()
            )

            if not existing_progress:

                progress = StudentProgress(
                    student_id=student.id,
                    topic_id=topic.id,
                    status="Not Started"
                )

                db.session.add(progress)

        learning_path_data.append({
            "course": course,
            "topics": selected_topics,
            "message": start_message
        })

    db.session.commit()

    # =====================================================
    # EXTERNAL LEARNING RESOURCES
    # =====================================================

    resources = {

        # -------------------------------------------------
        # DATA ANALYST
        # -------------------------------------------------

        "Data Analyst": {

            "courses": [
                {
                    "name": "Kaggle - Python",
                    "description": "Learn Python fundamentals for data analysis.",
                    "url": "https://www.kaggle.com/learn/python"
                },
                {
                    "name": "Kaggle - Pandas",
                    "description": "Practice data manipulation and analysis with Pandas.",
                    "url": "https://www.kaggle.com/learn/pandas"
                },
                {
                    "name": "Kaggle - Intro to SQL",
                    "description": "Learn SQL queries and database analysis.",
                    "url": "https://www.kaggle.com/learn/intro-to-sql"
                }
            ],

            "books": [
                {
                    "name": "Python for Data Analysis",
                    "author": "Wes McKinney",
                    "url": "https://www.oreilly.com/library/view/python-for-data/9781098104023/"
                },
                {
                    "name": "Storytelling with Data",
                    "author": "Cole Nussbaumer Knaflic",
                    "url": "https://www.storytellingwithdata.com/books"
                },
                {
                    "name": "An Introduction to Statistical Learning",
                    "author": "Gareth James, Daniela Witten, Trevor Hastie and Robert Tibshirani",
                    "url": "https://www.statlearning.com/"
                }
            ],

            "resources": [
                {
                    "name": "Kaggle Learn",
                    "description": "Hands-on data science tutorials and exercises.",
                    "url": "https://www.kaggle.com/learn"
                }
            ]
        },

        # -------------------------------------------------
        # WEB DEVELOPER
        # -------------------------------------------------

        "Web Developer": {

            "courses": [
                {
                    "name": "MDN Learn Web Development",
                    "description": "Structured learning path covering HTML, CSS and JavaScript.",
                    "url": "https://developer.mozilla.org/en-US/docs/Learn_web_development"
                },
                {
                    "name": "freeCodeCamp",
                    "description": "Interactive web development lessons and projects.",
                    "url": "https://www.freecodecamp.org/learn/"
                }
            ],

            "books": [
                {
                    "name": "Eloquent JavaScript",
                    "author": "Marijn Haverbeke",
                    "url": "https://eloquentjavascript.net/"
                },
                {
                    "name": "HTML and CSS: Design and Build Websites",
                    "author": "Jon Duckett",
                    "url": "https://www.google.com/search?q=HTML+and+CSS+Design+and+Build+Websites+Jon+Duckett"
                }
            ],

            "resources": [
                {
                    "name": "MDN Web Docs",
                    "description": "Documentation and tutorials for HTML, CSS and JavaScript.",
                    "url": "https://developer.mozilla.org/"
                },
                {
                    "name": "MDN Curriculum",
                    "description": "A structured curriculum for new front-end developers.",
                    "url": "https://developer.mozilla.org/en-US/curriculum/"
                }
            ]
        },

        # -------------------------------------------------
        # AI / ML ENGINEER
        # -------------------------------------------------

        "AI/ML Engineer": {

            "courses": [
                {
                    "name": "Kaggle - Python",
                    "description": "Build the Python foundation needed for machine learning.",
                    "url": "https://www.kaggle.com/learn/python"
                },
                {
                    "name": "Kaggle - Intro to Machine Learning",
                    "description": "Learn core machine learning concepts and build your first models.",
                    "url": "https://www.kaggle.com/learn/intro-to-machine-learning"
                },
                {
                    "name": "An Introduction to Statistical Learning - Python",
                    "description": "Learn statistical learning concepts with Python.",
                    "url": "https://www.statlearning.com/online-courses"
                }
            ],

            "books": [
                {
                    "name": "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow",
                    "author": "Aurélien Géron",
                    "url": "https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/"
                },
                {
                    "name": "An Introduction to Statistical Learning",
                    "author": "Gareth James, Daniela Witten, Trevor Hastie and Robert Tibshirani",
                    "url": "https://www.statlearning.com/"
                }
            ],

            "resources": [
                {
                    "name": "Kaggle Learn",
                    "description": "Hands-on machine learning tutorials, exercises and projects.",
                    "url": "https://www.kaggle.com/learn"
                }
            ]
        },

        # -------------------------------------------------
        # CYBERSECURITY
        # -------------------------------------------------

        "Cybersecurity": {

            "courses": [
                {
                    "name": "Google Cybersecurity Certificate",
                    "description": "Learn cybersecurity foundations, networking, Linux, SQL and security operations.",
                    "url": "https://grow.google/intl/en_in/cybersecurity-course/"
                }
            ],

            "books": [
                {
                    "name": "The Linux Command Line",
                    "author": "William Shotts",
                    "url": "https://linuxcommand.org/tlcl.php"
                },
                {
                    "name": "The Web Application Hacker's Handbook",
                    "author": "Dafydd Stuttard and Marcus Pinto",
                    "url": "https://owasp.org/www-project-web-security-testing-guide/"
                }
            ],

            "resources": [
                {
                    "name": "OWASP Web Security Testing Guide",
                    "description": "Comprehensive guide for testing web application security.",
                    "url": "https://owasp.org/www-project-web-security-testing-guide/"
                },
                {
                    "name": "LinuxCommand.org",
                    "description": "Learn Linux command line and shell scripting.",
                    "url": "https://linuxcommand.org/"
                }
            ]
        }
    }

    career_resources = resources.get(
        career.name,
        {
            "courses": [],
            "books": [],
            "resources": []
        }
    )

    return render_template(
        "learning_path.html",
        student=student,
        career=career,
        level=level,
        learning_path=learning_path_data,
        career_resources=career_resources
    )


# =========================================================
# CAREER DISCOVERY QUIZ
# "I DON'T KNOW MY CAREER"
# =========================================================

@bp.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():

    if current_user.role != "student":

        flash(
            "Access denied.",
            "error"
        )

        return redirect(
            url_for("main.student_dashboard")
        )

    student = Student.query.filter_by(
        user_id=current_user.id
    ).first()

    if not student:

        flash(
            "Student profile not found.",
            "error"
        )

        return redirect(
            url_for("main.student_dashboard")
        )

    # =====================================================
    # 10 CAREER DISCOVERY QUESTIONS
    # =====================================================

    questions = [

        {
            "id": 1,

            "question":
                "Which type of work sounds most interesting to you?",

            "options": {
                "A": "Finding patterns and insights in data",
                "B": "Building websites and web applications",
                "C": "Creating systems that can predict or learn",
                "D": "Protecting computers and networks"
            },

            "career": {
                "A": "Data Analyst",
                "B": "Web Developer",
                "C": "AI/ML Engineer",
                "D": "Cybersecurity"
            }
        },

        {
            "id": 2,

            "question":
                "Which activity would you enjoy the most?",

            "options": {
                "A": "Working with numbers and statistics",
                "B": "Designing how a website looks and works",
                "C": "Writing Python programs and experimenting with models",
                "D": "Investigating suspicious activity on a computer"
            },

            "career": {
                "A": "Data Analyst",
                "B": "Web Developer",
                "C": "AI/ML Engineer",
                "D": "Cybersecurity"
            }
        },

        {
            "id": 3,

            "question":
                "What kind of problem would you prefer solving?",

            "options": {
                "A": "Why are sales decreasing?",
                "B": "How can I make this website interactive?",
                "C": "How can a computer predict future results?",
                "D": "How did someone gain unauthorized access?"
            },

            "career": {
                "A": "Data Analyst",
                "B": "Web Developer",
                "C": "AI/ML Engineer",
                "D": "Cybersecurity"
            }
        },

        {
            "id": 4,

            "question":
                "Which technology sounds most interesting to you?",

            "options": {
                "A": "SQL and data visualization",
                "B": "HTML, CSS and JavaScript",
                "C": "Python and machine learning",
                "D": "Networks and security tools"
            },

            "career": {
                "A": "Data Analyst",
                "B": "Web Developer",
                "C": "AI/ML Engineer",
                "D": "Cybersecurity"
            }
        },

        {
            "id": 5,

            "question":
                "Which type of result would make you feel most satisfied?",

            "options": {
                "A": "A dashboard explaining important business trends",
                "B": "A website that people can actually use",
                "C": "A model that successfully predicts an outcome",
                "D": "A system that is protected from attacks"
            },

            "career": {
                "A": "Data Analyst",
                "B": "Web Developer",
                "C": "AI/ML Engineer",
                "D": "Cybersecurity"
            }
        },

        {
            "id": 6,

            "question":
                "Which subject do you naturally enjoy more?",

            "options": {
                "A": "Statistics and analytical thinking",
                "B": "Programming and creating applications",
                "C": "Mathematics, algorithms and AI",
                "D": "Computer networks and system security"
            },

            "career": {
                "A": "Data Analyst",
                "B": "Web Developer",
                "C": "AI/ML Engineer",
                "D": "Cybersecurity"
            }
        },

        {
            "id": 7,

            "question":
                "Imagine you receive a large dataset. What would you rather do?",

            "options": {
                "A": "Analyze it and find useful patterns",
                "B": "Build a website to display it",
                "C": "Train a model using the data",
                "D": "Check it for security or privacy problems"
            },

            "career": {
                "A": "Data Analyst",
                "B": "Web Developer",
                "C": "AI/ML Engineer",
                "D": "Cybersecurity"
            }
        },

        {
            "id": 8,

            "question":
                "Which challenge sounds most exciting to you?",

            "options": {
                "A": "Understanding why a business metric changed",
                "B": "Creating a complete web application",
                "C": "Teaching a computer to recognize patterns",
                "D": "Finding and fixing a security vulnerability"
            },

            "career": {
                "A": "Data Analyst",
                "B": "Web Developer",
                "C": "AI/ML Engineer",
                "D": "Cybersecurity"
            }
        },

        {
            "id": 9,

            "question":
                "What would you prefer to spend several hours doing?",

            "options": {
                "A": "Analyzing spreadsheets, databases and charts",
                "B": "Coding a website or web application",
                "C": "Experimenting with Python and machine learning",
                "D": "Studying networks and security problems"
            },

            "career": {
                "A": "Data Analyst",
                "B": "Web Developer",
                "C": "AI/ML Engineer",
                "D": "Cybersecurity"
            }
        },

        {
            "id": 10,

            "question":
                "Which statement describes you best?",

            "options": {
                "A": "I like understanding information and making decisions from it",
                "B": "I like creating things that people can interact with",
                "C": "I like solving complex problems using mathematics and programming",
                "D": "I like finding weaknesses and figuring out how to protect systems"
            },

            "career": {
                "A": "Data Analyst",
                "B": "Web Developer",
                "C": "AI/ML Engineer",
                "D": "Cybersecurity"
            }
        }
    ]

    # =====================================================
    # SUBMIT CAREER DISCOVERY QUIZ
    # =====================================================

    if request.method == "POST":

        scores = {
            "Data Analyst": 0,
            "Web Developer": 0,
            "AI/ML Engineer": 0,
            "Cybersecurity": 0
        }

        answered = 0

        # -------------------------------------------------
        # Calculate scores
        # -------------------------------------------------

        for question in questions:

            answer = request.form.get(
                f"question_{question['id']}"
            )

            if not answer:
                continue

            answered += 1

            selected_career = question[
                "career"
            ].get(answer)

            if selected_career:

                scores[
                    selected_career
                ] += 1

        # -------------------------------------------------
        # Require all 10 questions
        # -------------------------------------------------

        if answered < 10:

            flash(
                "Please answer all 10 questions.",
                "error"
            )

            return render_template(
                "career_discovery.html",
                questions=questions
            )

        # -------------------------------------------------
        # Find highest scoring profession
        # -------------------------------------------------

        recommended_career_name = max(
            scores,
            key=scores.get
        )

        highest_score = scores[
            recommended_career_name
        ]

        # -------------------------------------------------
        # Find career in database
        # -------------------------------------------------

        career = CareerPath.query.filter_by(
            name=recommended_career_name
        ).first()

        if not career:

            flash(
                "Recommended career was not found in the database.",
                "error"
            )

            return redirect(
                url_for("main.student_dashboard")
            )

        # -------------------------------------------------
        # Save recommended career
        # -------------------------------------------------

        student.career_id = career.id

        # Career discovery determines interest,
        # not technical skill.
        student.skill_level = "Beginner"

        # -------------------------------------------------
        # Save discovery result
        # -------------------------------------------------

        result = QuizResult(
            student_id=student.id,
            score=highest_score * 10,
            recommended_career_id=career.id,
            attempted_at=datetime.utcnow()
        )

        db.session.add(result)

        db.session.commit()

        # -------------------------------------------------
        # Show recommendation
        # -------------------------------------------------

        return render_template(
            "career_discovery_result.html",
            career=career,
            score=highest_score * 10,
            scores=scores
        )

    # =====================================================
    # SHOW CAREER DISCOVERY QUIZ
    # =====================================================

    return render_template(
        "career_discovery.html",
        questions=questions
    )