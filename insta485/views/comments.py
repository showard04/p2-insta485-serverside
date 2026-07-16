"""Comment routes."""

import sqlite3

import flask
import insta485
from insta485.views.accounts import login_required


@insta485.app.route("/comments/", methods=["POST"])
def update_comments():
    """Handle comment create and delete operations."""
    redirect_response = login_required()  # regular login check
    if redirect_response is not None:
        return redirect_response

    username = flask.session["username"]
    operation = flask.request.form["operation"]

    connection = sqlite3.connect(insta485.app.config["DATABASE_FILENAME"])
    connection.row_factory = sqlite3.Row

    if operation == "create":
        postid = flask.request.form["postid"]
        text = flask.request.form["text"]

        if not text:  # dont allow blank comments
            connection.close()
            flask.abort(400)

        connection.execute(
            "INSERT INTO comments (owner, postid, text) VALUES (?, ?, ?)",
            (username, postid, text),
        )

    elif operation == "delete":
        commentid = flask.request.form["commentid"]

        comment = connection.execute(
            "SELECT owner FROM comments WHERE commentid = ?",
            (commentid,),
        ).fetchone()

        # if the comment doesn't exist
        if comment is None:
            connection.close()
            flask.abort(404)

        if comment["owner"] != username:  # if comment not owned by the user
            connection.close()
            flask.abort(403)

        connection.execute(
            "DELETE FROM comments WHERE commentid = ?",
            (commentid,),
        )

    else:
        connection.close()
        flask.abort(400)

    connection.commit()
    connection.close()

    target = flask.request.args.get("target", "/")
    return flask.redirect(target)
