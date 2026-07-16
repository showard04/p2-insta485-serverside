"""Insta485 package initializer."""

import flask
from flask_wtf.csrf import CSRFProtect

app = flask.Flask(__name__)  # pylint: disable=invalid-name
app.config.from_object("insta485.config")
app.config.from_envvar("INSTA485_SETTINGS", silent=True)
csrf = CSRFProtect(app)

import insta485.views  # noqa: E402  pylint: disable=wrong-import-position
import insta485.model  # noqa: E402  pylint: disable=wrong-import-position