import functools
import secrets

from flask import Blueprint
from flask import g
from flask import request
from flask_cors import cross_origin
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from app.database import models

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return {"error": "Unauthorized"}, 401

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    token = get_auth_header()

    if not token:
        g.user = None
        return

    session_ = models.Session.query.filter_by(session_id=token).first()
    if not session_:
        g.user = None
        return

    user = models.User.query.filter_by(id=session_.user_id).first()
    g.user = user


def get_auth_header():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ")[1]


def generate_random_token():
    return secrets.token_hex(16)


@bp.route("/register", methods=("POST",))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    error = None

    if not username:
        error = "Username is required."
    elif not password:
        error = "Password is required."

    if error is None:
        try:
            user = models.User(username=username, password=generate_password_hash(password))
            models.db.session.add(user)
            models.db.session.commit()
            return {"status": "success"}
        except Exception as e:
            error = str(e)

    return {"error": error}, 400


@bp.route("/login/", methods=("POST",))
@cross_origin()
def login():
    """Log in a registered user by adding the user id to the session."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    error = None
    user = models.User.query.filter_by(username=username).first()

    if user is None:
        error = "Incorrect username."
    elif not check_password_hash(user.password, password):
        error = "Incorrect password."

    if error is None:
        session_ = models.Session.query.filter_by(user_id=user.id).first()
        if not session_:
            session_ = models.Session(user_id=user.id)
            models.db.session.add(session_)
        session_.session_id = generate_random_token()
        models.db.session.commit()
        return {"token": session_.session_id}

    return {"error": error}, 400


@bp.route("/logout/", methods=("POST",))
@cross_origin()
@login_required
def logout():
    """Clear the current session, including the stored user id."""
    token = get_auth_header()
    session_ = models.Session.query.filter_by(session_id=token).first()
    models.db.session.delete(session_)
    return {"status": "success"}
