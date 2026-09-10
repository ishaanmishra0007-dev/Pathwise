-- PATHWISE DATABASE

-- USERS
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL
        CHECK (role IN ('student', 'teacher', 'admin'))
);


-- CAREERS
CREATE TABLE careers (
    career_id SERIAL PRIMARY KEY,
    career_name VARCHAR(100) NOT NULL,
    description TEXT
);


-- STUDENTS
CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    career_id INT,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id),

    FOREIGN KEY (career_id)
        REFERENCES careers(career_id)
);


-- TEACHERS
CREATE TABLE teachers (
    teacher_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
);


-- COURSES
CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    career_id INT NOT NULL,
    course_name VARCHAR(100) NOT NULL,

    FOREIGN KEY (career_id)
        REFERENCES careers(career_id)
);


-- TOPICS
CREATE TABLE topics (
    topic_id SERIAL PRIMARY KEY,
    course_id INT NOT NULL,
    topic_name VARCHAR(100) NOT NULL,
    topic_order INT DEFAULT 1,

    FOREIGN KEY (course_id)
        REFERENCES courses(course_id)
);


-- MATERIALS
CREATE TABLE materials (
    material_id SERIAL PRIMARY KEY,
    topic_id INT NOT NULL,
    teacher_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    file_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (topic_id)
        REFERENCES topics(topic_id),

    FOREIGN KEY (teacher_id)
        REFERENCES teachers(teacher_id)
);


-- TESTS
CREATE TABLE tests (
    test_id SERIAL PRIMARY KEY,
    topic_id INT NOT NULL,
    teacher_id INT NOT NULL,
    test_name VARCHAR(150) NOT NULL,

    FOREIGN KEY (topic_id)
        REFERENCES topics(topic_id),

    FOREIGN KEY (teacher_id)
        REFERENCES teachers(teacher_id)
);


-- QUESTIONS
CREATE TABLE questions (
    question_id SERIAL PRIMARY KEY,
    test_id INT NOT NULL,
    question_text TEXT NOT NULL,

    option_a VARCHAR(255),
    option_b VARCHAR(255),
    option_c VARCHAR(255),
    option_d VARCHAR(255),

    correct_answer CHAR(1),

    FOREIGN KEY (test_id)
        REFERENCES tests(test_id)
);


-- QUIZ RESULTS
CREATE TABLE quiz_results (
    quiz_result_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    score INT NOT NULL,
    recommended_career_id INT,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id)
        REFERENCES students(student_id),

    FOREIGN KEY (recommended_career_id)
        REFERENCES careers(career_id)
);


-- TEST RESULTS
CREATE TABLE test_results (
    result_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    test_id INT NOT NULL,
    score INT NOT NULL,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id)
        REFERENCES students(student_id),

    FOREIGN KEY (test_id)
        REFERENCES tests(test_id)
);


-- STUDENT PROGRESS
CREATE TABLE student_progress (
    progress_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    topic_id INT NOT NULL,

    status VARCHAR(20) DEFAULT 'Not Started'
        CHECK (
            status IN
            ('Not Started', 'In Progress', 'Completed')
        ),

    FOREIGN KEY (student_id)
        REFERENCES students(student_id),

    FOREIGN KEY (topic_id)
        REFERENCES topics(topic_id)
);


-- CERTIFICATES
CREATE TABLE certificates (
    certificate_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    certificate_type VARCHAR(100) NOT NULL,
    issue_date DATE DEFAULT CURRENT_DATE,
    certificate_path VARCHAR(255),

    FOREIGN KEY (student_id)
        REFERENCES students(student_id)
);