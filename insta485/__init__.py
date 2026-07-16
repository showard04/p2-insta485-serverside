"""Insta485 package initializer."""

import flask
from flask_wtf.csrf import CSRFProtect
import insta485.views
import insta485.model

app = flask.Flask(__name__)  # pylint: disable=invalid-name
app.config.from_object("insta485.config")
app.config.from_envvar("INSTA485_SETTINGS", silent=True)
csrf = CSRFProtect(app)

csrf = CSRFProtect(app)
