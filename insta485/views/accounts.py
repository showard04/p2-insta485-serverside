"""Account routes."""

import hashlib
import sqlite3
import uuid

import flask
import insta485


def get_user(username):
    """Return one user row from the database."""
    connection = sqlite3.connect(insta485.app.config["DATABASE_FILENAME"])
    connection.row_factory = sqlite3.Row

    user = connection.execute(
        "SELECT username, fullname, email, filename, password "
        "FROM users "
        "WHERE username = ?",
        (username,),
    ).fetchone()

    connection.close()
    return user


def login_required():
    """Redirect to login page if user is not logged in."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))
    return None


def verify_password(input_password, stored_password):
    """Verify a plaintext password against the stored salted hash."""
    algorithm, salt, password_hash = stored_password.split("$")

    hash_obj = hashlib.new(algorithm)
    salted_password = salt + input_password
    hash_obj.update(salted_password.encode("utf-8"))

    return hash_obj.hexdigest() == password_hash


def hash_password(password):
    """Hash a password with a random salt."""
    algorithm = "sha512"
    salt = uuid.uuid4().hex

    hash_obj = hashlib.new(algorithm)
    salted_password = salt + password
    hash_obj.update(salted_password.encode("utf-8"))

    password_hash = hash_obj.hexdigest()
    return "$".join([algorithm, salt, password_hash])


def save_upload(fileobj):
    """Save an uploaded file and return the new filename."""
    suffix = fileobj.filename[fileobj.filename.rfind("."):]
    filename = f"{uuid.uuid4().hex}{suffix}"

    upload_folder = insta485.app.config["UPLOAD_FOLDER"]
    upload_folder.mkdir(parents=True, exist_ok=True)

    fileobj.save(upload_folder / filename)
    return filename


def remove_upload(filename):
    """Remove an uploaded file if it exists."""
    if not filename:
        return

    path = insta485.app.config["UPLOAD_FOLDER"] / filename
    if path.exists():
        path.unlink()


def handle_login():
    """Handle login operation."""
    username = flask.request.form.get("username")
    password = flask.request.form.get("password")

    if not username or not password:
        flask.abort(400)

    user = get_user(username)

    if user is None:
        flask.abort(403)

    if not verify_password(password, user["password"]):
        flask.abort(403)

    flask.session["username"] = username


def handle_logout():
    """Handle logout operation."""
    flask.session.clear()


def handle_create():
    """Handle account creation."""
    username = flask.request.form.get("username")
    fullname = flask.request.form.get("fullname")
    email = flask.request.form.get("email")
    password = flask.request.form.get("password")
    fileobj = flask.request.files.get("file")

    if not username or not fullname or not email or not password or not fileobj:
        flask.abort(400)

    connection = sqlite3.connect(insta485.app.config["DATABASE_FILENAME"])
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    existing_user = connection.execute(
        "SELECT username FROM users WHERE username = ?",
        (username,),
    ).fetchone()

    if existing_user is not None:
        connection.close()
        flask.abort(409)

    filename = save_upload(fileobj)

    connection.execute(
        "INSERT INTO users(username, fullname, email, filename, password) "
        "VALUES (?, ?, ?, ?, ?)",
        (username, fullname, email, filename, hash_password(password)),
    )
    connection.commit()
    connection.close()

    flask.session["username"] = username


def handle_edit_account():
    """Handle account edit operation."""
    if "username" not in flask.session:
        flask.abort(403)

    fullname = flask.request.form.get("fullname")
    email = flask.request.form.get("email")
    fileobj = flask.request.files.get("file")

    if not fullname or not email:
        flask.abort(400)

    username = flask.session["username"]
    user = get_user(username)

    connection = sqlite3.connect(insta485.app.config["DATABASE_FILENAME"])
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    if fileobj and fileobj.filename:
        new_filename = save_upload(fileobj)
        remove_upload(user["filename"])

        connection.execute(
            "UPDATE users "
            "SET fullname = ?, email = ?, filename = ? "
            "WHERE username = ?",
            (fullname, email, new_filename, username),
        )
    else:
        connection.execute(
            "UPDATE users "
            "SET fullname = ?, email = ? "
            "WHERE username = ?",
            (fullname, email, username),
        )

    connection.commit()
    connection.close()


def handle_update_password():
    """Handle password update operation."""
    if "username" not in flask.session:
        flask.abort(403)

    password = flask.request.form.get("password")
    new_password1 = flask.request.form.get("new_password1")
    new_password2 = flask.request.form.get("new_password2")

    if not password or not new_password1 or not new_password2:
        flask.abort(400)

    if new_password1 != new_password2:
        flask.abort(401)

    username = flask.session["username"]
    user = get_user(username)

    if not verify_password(password, user["password"]):
        flask.abort(403)

    connection = sqlite3.connect(insta485.app.config["DATABASE_FILENAME"])
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    connection.execute(
        "UPDATE users SET password = ? WHERE username = ?",
        (hash_password(new_password1), username),
    )
    connection.commit()
    connection.close()


def handle_delete():
    """Handle account deletion."""
    if "username" not in flask.session:
        flask.abort(403)

    username = flask.session["username"]

    connection = sqlite3.connect(insta485.app.config["DATABASE_FILENAME"])
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    user = connection.execute(
        "SELECT filename FROM users WHERE username = ?",
        (username,),
    ).fetchone()

    posts = connection.execute(
        "SELECT filename FROM posts WHERE owner = ?",
        (username,),
    ).fetchall()

    if user is not None:
        remove_upload(user["filename"])

    for post in posts:
        remove_upload(post["filename"])

    connection.execute(
        "DELETE FROM users WHERE username = ?",
        (username,),
    )
    connection.commit()
    connection.close()

    flask.session.clear()


@insta485.app.route("/accounts/login/")
def show_login():
    """Display login page."""
    if "username" in flask.session:
        return flask.redirect(flask.url_for("show_index"))

    return flask.render_template("accounts_login.html")


@insta485.app.route("/accounts/create/")
def show_create():
    """Display account creation page."""
    if "username" in flask.session:
        return flask.redirect(flask.url_for("show_edit"))

    return flask.render_template("accounts_create.html")


@insta485.app.route("/accounts/delete/")
def show_delete():
    """Display account deletion confirmation page."""
    redirect_response = login_required()
    if redirect_response is not None:
        return redirect_response

    context = {
        "username": flask.session["username"],
    }
    return flask.render_template("accounts_delete.html", **context)


@insta485.app.route("/accounts/edit/")
def show_edit():
    """Display account edit page."""
    redirect_response = login_required()
    if redirect_response is not None:
        return redirect_response

    user = get_user(flask.session["username"])

    context = {
        "user": user,
    }
    return flask.render_template("accounts_edit.html", **context)


@insta485.app.route("/accounts/password/")
def show_password():
    """Display password update page."""
    redirect_response = login_required()
    if redirect_response is not None:
        return redirect_response

    return flask.render_template("accounts_password.html")


@insta485.app.route("/accounts/auth/")
def show_auth():
    """Return auth status."""
    if "username" not in flask.session:
        flask.abort(403)

    return "", 200


@insta485.app.route("/accounts/", methods=["POST"])
def update_accounts():
    """Handle account operations."""
    operation = flask.request.form.get("operation")
    target = flask.request.args.get("target", "/")

    if operation == "login":
        handle_login()
    elif operation == "logout":
        handle_logout()
    elif operation == "create":
        handle_create()
    elif operation == "edit_account":
        handle_edit_account()
    elif operation == "update_password":
        handle_update_password()
    elif operation == "delete":
        handle_delete()
    else:
        flask.abort(400)

    return flask.redirect(target)


@insta485.app.route("/accounts/logout/", methods=["POST"])
def logout():
    """Log out user."""
    flask.session.clear()
    return flask.redirect(flask.url_for("show_login"))