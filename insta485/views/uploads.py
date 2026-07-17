"""Upload routes."""
import sqlite3
import flask
import insta485


@insta485.app.route("/uploads/<filename>")
def show_upload(filename):
    """Serve uploaded files only to logged-in users."""
    if "username" not in flask.session:
        flask.abort(403)
    # If an auth. user attempts to access a file that don't exist: abort(404)
    connection = sqlite3.connect(insta485.app.config["DATABASE_FILENAME"])
    connection.row_factory = sqlite3.Row
    picture = connection.execute(
        "SELECT filename FROM users WHERE filename = ?",
        (filename,),
    ).fetchall()

    filee = connection.execute(
        "SELECT filename FROM posts WHERE filename = ?",
        (filename,),
    ).fetchall()

    if picture is None:
        flask.abort(404)
    if filee is None:
        flask.abort(404)

    return flask.send_from_directory(
        insta485.app.config["UPLOAD_FOLDER"],
        filename,
    )
