"""Insta485 index view."""

import flask
import insta485


@insta485.app.route("/")
def show_index():
    """Display / route."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))

    context = {}
    return flask.render_template("index.html", **context)