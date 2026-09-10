from flask import Flask

from routes.teacher import teacher


app = Flask(__name__)

app.secret_key = "pathwise-secret-key"

app.register_blueprint(teacher)


@app.route("/")
def home():
    return "PathWise is running!"


if __name__ == "__main__":
    app.run(debug=True)