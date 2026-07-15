"""Insta485 uploads."""
import flask
import insta485


@insta485.app.route('/uploads/<filename>')
def show_upload(filename):
    """Display / uploads."""
    return flask.send_from_directory(
        "sql/uploads", filename, as_attachment=True
    )
