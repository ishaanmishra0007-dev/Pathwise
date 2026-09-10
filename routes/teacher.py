from flask import Blueprint, render_template

teacher = Blueprint(
    "teacher",
    __name__,
    url_prefix="/teacher"
)


@teacher.route("/dashboard")
def dashboard():

    return render_template(
        "teacher/dashboard.html"
    )