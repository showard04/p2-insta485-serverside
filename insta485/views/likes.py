"""Like routes."""

import sqlite3

import flask
import insta485
from insta485.views.accounts import login_required


@insta485.app.route("/likes/", methods=["POST"])
def update_likes():
    """Handle like and unlike operations."""
    redirect_response = login_required()  # regular login check
    if redirect_response is not None:
        return redirect_response

    logname = flask.session["username"]
    operation = flask.request.form["operation"]
    postid = flask.request.form["postid"]

    conn = sqlite3.connect(insta485.app.config["DATABASE_FILENAME"])
    conn.row_factory = sqlite3.Row

    # check if a like already exists on this post
    existing = conn.execute(
        "SELECT 1 FROM likes WHERE owner = ? AND postid = ?",
        (logname, postid),
    ).fetchone()
    # update likes on a post if the user likes it
    if operation == "like":
        if existing is not None:  # check if post already liked by this user
            conn.close()
            flask.abort(409)
        conn.execute(
            "INSERT INTO likes (owner, postid) VALUES (?, ?)",
            (logname, postid),
        )
    # update post for when a user unlikes it
    elif operation == "unlike":
        if existing is None:  # check if post already liked
            conn.close()
            flask.abort(409)
        conn.execute(
            "DELETE FROM likes WHERE owner = ? AND postid = ?",
            (logname, postid),)
    else:
        conn.close()
        flask.abort(400)

    conn.commit()
    conn.close()

    target = flask.request.args.get("target", "/")
    return flask.redirect(target)
