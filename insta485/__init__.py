"""Insta485 package initializer."""

import importlib

import flask
import flask_wtf.csrf

app = flask.Flask(__name__)
app.config.from_object("insta485.config")
app.config.from_envvar("INSTA485_SETTINGS", silent=True)

flask_wtf.csrf.CSRFProtect(app)

importlib.import_module("insta485.views")
importlib.import_module("insta485.model")
