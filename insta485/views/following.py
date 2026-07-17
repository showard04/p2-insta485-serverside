"""Following routes."""

import sqlite3
import flask
import insta485
from insta485.views.accounts import login_required


@insta485.app.route("/users/<user_url_slug>/following/")
def show_following(user_url_slug):
    """Display following page."""
    redirect_response = login_required()  # send to login page if not
    if redirect_response is not None:
        return redirect_response

    # connect to database
    connection = sqlite3.connect(insta485.app.config["DATABASE_FILENAME"])
    connection.row_factory = sqlite3.Row

    target_user = connection.execute(
        "SELECT username FROM users WHERE username = ?",
        (user_url_slug,),
    ).fetchone()

    # if the user doesn't exist
    if target_user is None:
        connection.close()
        flask.abort(404)

    logname = flask.session["username"]  # retrieve who user is
    # sql string (query)
    following = connection.execute(
        """
        SELECT users.username, users.filename AS user_img_url,
               EXISTS(
                   SELECT 1 FROM following
                   WHERE follower = ? AND followee = users.username
               ) AS logname_follows_username
        FROM following
        JOIN users ON following.followee = users.username
        WHERE following.follower = ?
        """,
        (logname, user_url_slug),
    ).fetchall()  # retrieve all the query matches

    connection.close()

    context = {
        "logname": logname,
        "following": following,
    }
    return flask.render_template("following.html", **context)


@insta485.app.route("/following/", methods=["POST"])
def update_following():
    """Handle follow and unfollow operations."""
    redirect_res = login_required()
    if redirect_res is not None:
        return redirect_res

    log_name = flask.session["username"]
    oper = flask.request.form["operation"]
    username = flask.request.form["username"]

    sql_conn = sqlite3.connect(insta485.app.config["DATABASE_FILENAME"])
    sql_conn.row_factory = sqlite3.Row

    existing = sql_conn.execute(
        "SELECT 1 FROM following WHERE follower = ? AND followee = ?",
        (log_name, username),
    ).fetchone()

    if oper == "follow":
        if existing is not None:
            sql_conn.close()
            flask.abort(409)
        sql_conn.execute(
            "INSERT INTO following (follower, followee) VALUES (?, ?)",
            (log_name, username),
        )
    elif oper == "unfollow":
        if existing is None:
            sql_conn.close()
            flask.abort(409)
        sql_conn.execute(
            "DELETE FROM following WHERE follower = ? AND followee = ?",
            (log_name, username),
        )
    else:
        sql_conn.close()
        flask.abort(400)

    sql_conn.commit()
    sql_conn.close()

    target = flask.request.args.get("target", "/")
    return flask.redirect(target)
