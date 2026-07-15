"""Insta485 model."""

import sqlite3

import flask
import insta485


def dict_factory(cursor, row):
    """Convert database row objects to dictionaries."""
    return {
        col[0]: row[idx]
        for idx, col in enumerate(cursor.description)
    }


def get_db():
    """Open a new database connection."""
    if "sqlite_db" not in flask.g:
        flask.g.sqlite_db = sqlite3.connect(
            insta485.app.config["DATABASE_FILENAME"]
        )
        flask.g.sqlite_db.row_factory = dict_factory
        flask.g.sqlite_db.execute("PRAGMA foreign_keys = ON")

    return flask.g.sqlite_db


@insta485.app.teardown_appcontext
def close_db(error):
    """Close the database at the end of a request."""
    assert error or not error
    sqlite_db = flask.g.pop("sqlite_db", None)

    if sqlite_db is not None:
        sqlite_db.commit()
        sqlite_db.close()