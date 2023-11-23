from flask import Flask
from flask_cors import CORS

from app import database
from app.handlers import auth, todo


def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    app.config.from_pyfile("config.py", silent=True)

    CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    database.init_app(app)

    app.register_blueprint(auth.bp, url_prefix="/auth")
    app.register_blueprint(todo.bp, url_prefix="/todo")

    return app
