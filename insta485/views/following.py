# Following routes

import sqlite3
import flask
import insta485
from insta485.views.accounts import login_required

@insta485.app.route("/users/<user_url_slug>/following/")
def show_following(user_url_slug):
    """get the users that user slug is following"""
    redirect_response = login_required() # if the user isnt logged in, send them to login page
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

    logname = flask.session["username"] # retrieve who user is
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
    ).fetchall() # retrieve all the query matches

    connection.close()

    context = {
        "logname": logname,
        "following": following,
    }
    return flask.render_template("following.html", **context)


@insta485.app.route("/following/", methods=["POST"])
def update_following():
    redirect_response = login_required()
    if redirect_response is not None:
        return redirect_response

    logname = flask.session["username"]
    operation = flask.request.form["operation"]
    username = flask.request.form["username"]

    connection = sqlite3.connect(insta485.app.config["DATABASE_FILENAME"])
    connection.row_factory = sqlite3.Row

    existing = connection.execute(
        "SELECT 1 FROM following WHERE follower = ? AND followee = ?",
        (logname, username),
    ).fetchone()

    if operation == "follow":
        if existing is not None:
            connection.close()
            flask.abort(409)
        connection.execute(
            "INSERT INTO following (follower, followee) VALUES (?, ?)",
            (logname, username),
        )
    elif operation == "unfollow":
        if existing is None:
            connection.close()
            flask.abort(409)
        connection.execute(
            "DELETE FROM following WHERE follower = ? AND followee = ?",
            (logname, username),
        )
    else:
        connection.close()
        flask.abort(400)

    connection.commit()
    connection.close()

    target = flask.request.args.get("target", "/")
    return flask.redirect(target)