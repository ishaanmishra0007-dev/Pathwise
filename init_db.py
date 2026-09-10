from project import create_app, db
from project import models  # ensures all models are registered

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")
