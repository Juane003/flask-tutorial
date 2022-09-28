import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from flaskr.db import get_db

# Los blueprints o planos son una coleccion de rutas y otras funciones relacionadas con la app
# Sirven para definir funciones sin la necesidad de ya tener la aplicacion.

bp = Blueprint("auth", __name__, url_prefix="/auth")

# Acepta tres parametros, el nombre ("auth"), el donde esta definido (__name__) y la ruta con la que se la va a asociar ("/auth")


def login_requiered(view):
    @functools.wraps(view)
    # El decorador retorna una nueva funcion view que envuelve a la original
    # La nueva funcion chequea si el usuario esta cargado y sino lo redirije a la pagina de logeo
    def wrapped_view(**kwargs):
        # Kwargs es una sintaxis para pasar listas de palabras claves de largo variable.
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
# before_app_request registra la funcion que se ejecuta antes de la funcion de que return render_template sin importar que url es requesteada
# load_logged_in_user chequea si un user_id existe en la session y obtiene la data del usuario de la base de datos. guardanndolo en g.user
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?",
            (user_id),
        ).fetchone()

@bp.route("/register", methods=("GET", "POST"))
def register():
    # si el usuario envia el formulario, request.method va a ser "POST" y va a empezar a validar el input
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        # Valida que el usuario y la contraseña no sean nulos

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

            # Si la validacion es correcta se inserta un nuevo usuario en la base de datos

        if error is None:
            try:
                # execute toma una sentencia de SQL y usa los comodines "?" para mostrar donde iran ubicados los parametros
                # por razones de seguridad nunca se guarda la contraseña en la base de datos, por eso se hashea y luego se guarda
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                # se llama commit para guardar los cambios hechos
                db.commit()
            except db.IntegrityError:
                # integrityError sucedera si el usuario ya existe
                error = f"user {username} is already registered."
            else:
                # Luego de guardar al usuario, se redirige a la url "auth/login"
                # es preferible usar url_for porque es mas sencillo de cambiar luego
                return redirect(url_for("auth.login"))

                # flash guarda un mensaje y lo muestra al usuario en caso de que no se haya podido registrar
        flash(error)

        # render_template muestra una pagina HTML
    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
            # fetchone devuelve una fila de la base de datos, si la base no devuelve resultados, devuelve None
        ).fetchone()

        if user is None:
            error = "Incorrect username"
        # check_password_hash hashea el password que puso el usuario y lo lo compara, si son iguales, el password es valido
        elif not check_password_hash(user["password"], password):
            error = "incorrect password"

        if error is None:
            # session es un dictionary que guarda data entre requests
            # cuando la validacion sucede, el id se guarda en una nueva sesion, la data se guarda en una Cookie que se envia al buscador
            session.clear()
            session["user"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
