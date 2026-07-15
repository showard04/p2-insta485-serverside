"""
Insta485 uploads.

URLs include:
/uploads/<filename>
"""
import flask
import insta485

@insta485.app.route('/uploads/<filename>')
def show_upload(filename):
    return flask.send_from_directory(
        "sql/uploads", filename, as_attachment=True
    )