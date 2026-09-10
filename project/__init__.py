from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    login_manager.init_app(app)

    from . import routes, models

    app.register_blueprint(routes.bp)

    login_manager.login_view = 'main.login'

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    return app
