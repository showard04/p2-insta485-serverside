"""Insta485 index view."""

import flask
import insta485


@insta485.app.route("/")
def show_index():
    """Display / route."""
    context = {}
    return flask.render_template("index.html", **context)