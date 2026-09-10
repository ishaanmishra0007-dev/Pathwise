from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import User, QuizQuestion, QuizOption, CareerPath


bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'error')
            return redirect(url_for('main.register'))

        new_user = User(name=name, email=email, role=role)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully. Please login.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')

            if user.role == 'student':
                return redirect(url_for('main.student_dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('main.teacher_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('main.login'))

    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('main.index'))


@bp.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))

    materials = []
    if current_user.career_path:
        materials = sorted(current_user.career_path.materials, key=lambda m: m.order)

    return render_template('student_dashboard.html', materials=materials)



@bp.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    if current_user.role != 'student':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        from collections import Counter

        votes = []
        questions = QuizQuestion.query.all()

        for question in questions:
            selected_option_id = request.form.get(f'question_{question.id}')
            if selected_option_id:
                option = QuizOption.query.get(int(selected_option_id))
                if option:
                    votes.append(option.career_path_id)

        if votes:
            most_common_path_id = Counter(votes).most_common(1)[0][0]
            current_user.career_path_id = most_common_path_id
            db.session.commit()
            flash('Quiz completed! Your recommended career path has been set.', 'success')
        else:
            flash('Please answer at least one question.', 'error')
            return redirect(url_for('main.quiz'))

        return redirect(url_for('main.student_dashboard'))

    questions = QuizQuestion.query.all()
    return render_template('quiz.html', questions=questions)



@bp.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    return render_template('teacher_dashboard.html')


@bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    return render_template('admin_dashboard.html')
