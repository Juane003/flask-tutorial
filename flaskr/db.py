import sqlite3

import click
from flask import current_app, g

# g es un objeto donde se guarda data que puede ser usada por multiples funciones durante la request
# current_app hace que podamos acceder a __init__.py sin la necesidad de importarla


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        # Row hace que la conexion devuelva filas que se comportan como dictionaries lo que nos permite acceder a las columnas por su nombre
    return g.db
# en lugar de hacer una base nueva cada vez que se llama get_db, se reutiliza la existente gracias al modulo g


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))
        # open_resource abre un archivo de la misma carpeta


@click.command("init-db")
# Define un comando para la consola llamado init-db
def init_db_command():
    # Limpia la data existente y crea nuevas tablas
    init_db()
    click.echo("Initialized the database")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    # teardown_appcontext le dice a flask que llame la funcion close_db luego de devolver la respuesta
    # cli.add_command añade un comando que se puede ejecutar con el comando "flask" (como flask --app flaskr --debug run)
