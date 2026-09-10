from project import create_app, db
from project.models import CareerPath, QuizQuestion, QuizOption, LearningMaterial

app = create_app()

with app.app_context():
    # --- Career Paths ---
    web_dev = CareerPath(name="Web Development", description="Build websites and web apps using HTML, CSS, JavaScript, and backend frameworks.")
    data_science = CareerPath(name="Data Science", description="Analyze data, build models, and extract insights using Python, statistics, and ML.")
    design = CareerPath(name="UI/UX Design", description="Design user-friendly interfaces and experiences for apps and websites.")

    db.session.add_all([web_dev, data_science, design])
    db.session.commit()

    # --- Quiz Questions ---
    q1 = QuizQuestion(text="Which activity do you enjoy the most?")
    q2 = QuizQuestion(text="Which subject did you like best in school?")
    q3 = QuizQuestion(text="What kind of problems excite you?")

    db.session.add_all([q1, q2, q3])
    db.session.commit()

    # --- Quiz Options (linked to career paths) ---
    options = [
        QuizOption(question_id=q1.id, text="Building websites/apps", career_path_id=web_dev.id),
        QuizOption(question_id=q1.id, text="Analyzing numbers and data", career_path_id=data_science.id),
        QuizOption(question_id=q1.id, text="Sketching and designing layouts", career_path_id=design.id),

        QuizOption(question_id=q2.id, text="Computer Science / Coding", career_path_id=web_dev.id),
        QuizOption(question_id=q2.id, text="Mathematics / Statistics", career_path_id=data_science.id),
        QuizOption(question_id=q2.id, text="Art / Visual Design", career_path_id=design.id),

        QuizOption(question_id=q3.id, text="Making things work (functionality)", career_path_id=web_dev.id),
        QuizOption(question_id=q3.id, text="Finding patterns and predictions", career_path_id=data_science.id),
        QuizOption(question_id=q3.id, text="Making things look and feel good", career_path_id=design.id),
    ]
    db.session.add_all(options)
    db.session.commit()

    # --- Learning Materials ---
    materials = [
        LearningMaterial(career_path_id=web_dev.id, title="Introduction to HTML & CSS", content_url="https://developer.mozilla.org/en-US/docs/Web/HTML", order=1),
        LearningMaterial(career_path_id=web_dev.id, title="JavaScript Basics", content_url="https://developer.mozilla.org/en-US/docs/Web/JavaScript", order=2),
        LearningMaterial(career_path_id=web_dev.id, title="Intro to Flask (Backend)", content_url="https://flask.palletsprojects.com/", order=3),

        LearningMaterial(career_path_id=data_science.id, title="Python for Data Science", content_url="https://www.python.org/", order=1),
        LearningMaterial(career_path_id=data_science.id, title="Intro to Pandas & NumPy", content_url="https://pandas.pydata.org/", order=2),
        LearningMaterial(career_path_id=data_science.id, title="Basics of Machine Learning", content_url="https://scikit-learn.org/", order=3),

        LearningMaterial(career_path_id=design.id, title="Design Principles 101", content_url="https://www.interaction-design.org/", order=1),
        LearningMaterial(career_path_id=design.id, title="Figma Basics", content_url="https://www.figma.com/", order=2),
        LearningMaterial(career_path_id=design.id, title="User Research Fundamentals", content_url="https://www.nngroup.com/", order=3),
    ]
    db.session.add_all(materials)
    db.session.commit()

    print("✅ Sample data seeded successfully!")
