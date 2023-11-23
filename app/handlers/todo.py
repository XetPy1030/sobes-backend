from flask import Blueprint
from flask import request
from flask_cors import cross_origin
from werkzeug.exceptions import abort

from .auth import login_required
from ..database import models
from ..utils.user import validate_create_todo, validate_update_todo_text

bp = Blueprint("blog", __name__)


@bp.route("/", methods=("GET", "POST"))
@cross_origin()
def index():
    if request.method == "POST":
        data = request.get_json()

        error = validate_create_todo(data)
        if error is not None:
            return {"error": error}, 400

        todo = models.ToDo(
            username=data['username'],
            email=data['email'],
            text=data['text'],
        )
        models.db.session.add(todo)
        models.db.session.commit()
        return {"status": "success"}

    else:
        current_page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 3, type=int)

        sort_field = request.args.get("sort_field", "id", type=str)
        a_b = sort_field.startswith("-")
        sort_field = sort_field[1:] if a_b else sort_field
        if sort_field not in ["id", "username", "email", "is_completed"]:
            abort(404, f"Sort field {sort_field} doesn't exist.")

        if a_b:
            todos = models.ToDo.query.order_by(getattr(models.ToDo, sort_field).desc()).paginate(
                page=current_page, per_page=per_page, error_out=False
            )
        else:
            todos = models.ToDo.query.order_by(getattr(models.ToDo, sort_field)).paginate(
                page=current_page, per_page=per_page, error_out=False
            )

        if todos.total == 0:
            return {"todos": [], "total_pages": 0, "current_page": 0}
        if current_page > todos.pages:
            abort(404, f"Page {current_page} doesn't exist.")
        if current_page < 1:
            abort(404, f"Page {current_page} doesn't exist.")

        return {
            "todos": [todo.to_dict() for todo in todos.items],
            "total_pages": todos.pages,
            "current_page": todos.page,
        }


def get_todo_or_404(id):
    todo = models.ToDo.query.get(id)
    if todo is None:
        abort(404, f"Post id {id} doesn't exist.")
    return todo


@bp.route("/<int:id>/", methods=("PUT", "DELETE"))
@login_required
def update_delete(id):
    todo = get_todo_or_404(id)

    if request.method == "PUT":
        data = request.get_json()

        error = validate_update_todo_text(todo, data)
        if error is not None:
            return {"error": error}, 400

        todo.text = data["text"]
        todo.is_edited = True

    elif request.method == "DELETE":
        models.db.session.delete(todo)

    models.db.session.commit()
    return {"status": "success"}


@bp.route("/<int:id>/complete/", methods=("POST",))
@login_required
def complete(id):
    todo = get_todo_or_404(id)
    todo.is_completed = True
    models.db.session.commit()
    return {"status": "success"}
