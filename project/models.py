from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(10), nullable=False)
    career_path_id = db.Column(db.Integer, db.ForeignKey('career_path.id'), nullable=True)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
class CareerPath(db.Model):
    __tablename__ = 'career_path'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    users = db.relationship('User', backref='career_path', lazy=True)
    materials = db.relationship('LearningMaterial', backref='career_path', lazy=True)


class QuizQuestion(db.Model):
    __tablename__ = 'quiz_question'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)

    options = db.relationship('QuizOption', backref='question', lazy=True)


class QuizOption(db.Model):
    __tablename__ = 'quiz_option'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_question.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    career_path_id = db.Column(db.Integer, db.ForeignKey('career_path.id'), nullable=False)


class LearningMaterial(db.Model):
    __tablename__ = 'learning_material'
    id = db.Column(db.Integer, primary_key=True)
    career_path_id = db.Column(db.Integer, db.ForeignKey('career_path.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content_url = db.Column(db.String(300), nullable=True)
    order = db.Column(db.Integer, default=0)

    progress_entries = db.relationship('Progress', backref='material', lazy=True)


class Progress(db.Model):
    __tablename__ = 'progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('learning_material.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
