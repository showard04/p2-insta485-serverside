"""Account routes."""

import hashlib
import sqlite3

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
    else:
        flask.abort(400)

    return flask.redirect(target)

@insta485.app.route("/accounts/logout/", methods=["POST"])
def logout():
    """Log out user."""
    flask.session.clear()
    return flask.redirect(flask.url_for("show_login"))