import click
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


@click.command("init-db")
def create_db():
    db.drop_all()
    db.create_all()
    from .models import User
    user = User(username='admin', password=generate_password_hash('123'))
    db.session.add(user)
    db.session.commit()
    click.echo("Initialized the database.")


def init_app(app):
    app.cli.add_command(create_db)
    db.init_app(app)

    from . import models
