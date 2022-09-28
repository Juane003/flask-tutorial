from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from werkzeug.exceptions import abort

from flaskr.auth import login_requiered 
from flaskr.db import get_db

bp = Blueprint("blog", __name__, url_prefix="/blog")

@bp.route("/")
def index():
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()

    return render_template('blog/index.html', posts=posts)

@bp.route("/create", methods=("GET", "POST"))
@login_requiered
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required"

        if error is not None:
            flash(error)
        else:
            db = db.get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id)"
                " VALUES (?, ?, ?)",
                (title, body, g.user["id"])
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")

def get_post(id, check_author=True):
    