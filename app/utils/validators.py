import re

from app.database.models import ToDo


def validate_create_todo(data: dict):
    error = None
    username = data.get("username")
    email = data.get("email")
    text = data.get("text")

    if not username:
        error = "Username is required."
    elif not email:
        error = "Email is required."
    elif not text:
        error = "Text is required."

    if re.search(r"[^@]+@[^@]+\.[^@]+", email) is None:
        error = "Email is invalid."

    return error


def validate_update_todo_text(todo: ToDo, data: dict):
    error = None
    text = data.get("text")

    if not text:
        error = "Text is required."

    if todo.text == text:
        error = "Text is the same."

    return error



