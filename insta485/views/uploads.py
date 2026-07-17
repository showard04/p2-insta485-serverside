"""Upload routes."""

import flask
import insta485


@insta485.app.route("/uploads/<filename>")
def show_upload(filename):
    """Serve uploaded files only to logged-in users."""
    if "username" not in flask.session:
        flask.abort(403)
    # If an auth. user attempts to access a file that don't exist: abort(404)

    return flask.send_from_directory(
        insta485.app.config["UPLOAD_FOLDER"],
        filename,
    )
