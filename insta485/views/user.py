"""Insta485 index (user) view."""

import flask
import insta485


def _get_user(connection, username):
    return connection.execute(
        "SELECT username, fullname "
        "FROM users "
        "WHERE username = ?",
        (username,),
    ).fetchone()


def _get_count(connection, query, username):
    return connection.execute(
        query,
        (username,),
    ).fetchone()


def _get_user_posts(connection, username):
    return connection.execute(
        """
        SELECT postid, filename
        FROM posts
        WHERE owner = ?
        ORDER BY postid DESC
        """,
        (username,),
    ).fetchall()


def _get_follow_status(connection, logname, user_url_slug):
    user_fol = connection.execute(
        """
        SELECT follower, followee
        FROM following
        WHERE follower = ? AND followee = ?
        """,
        (logname, user_url_slug),
    ).fetchall()

    return len(user_fol) != 0


@insta485.app.route("/users/<user_url_slug>/")
def show_user(user_url_slug):
    """Display user page."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))

    connection = insta485.model.get_db()
    logname = flask.session["username"]

    logged_user = _get_user(connection, logname)
    us = _get_user(connection, user_url_slug)

    if us is None:
        flask.abort(404)

    context = {
        "us": us,
        "logged_user": logged_user,
        "t_posts": _get_count(
            connection,
            "SELECT COUNT(postid) AS total_posts "
            "FROM posts "
            "WHERE owner = ?",
            user_url_slug,
        ),
        "t_following": _get_count(
            connection,
            """
            SELECT COUNT(followee) AS total_following
            FROM following
            WHERE follower = ?
            """,
            user_url_slug,
        ),
        "t_followers": _get_count(
            connection,
            """
            SELECT COUNT(follower) AS total_followers
            FROM following
            WHERE followee = ?
            """,
            user_url_slug,
        ),
        "user_posts": _get_user_posts(connection, user_url_slug),
        "logname_follows_username": _get_follow_status(
            connection,
            logname,
            user_url_slug,
        ),
    }
    return flask.render_template("user.html", **context)
