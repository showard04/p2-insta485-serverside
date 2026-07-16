"""Insta485 index (user) view."""

import flask
import insta485


@insta485.app.route("/users/<user_url_slug>/")
def show_user(user_url_slug):
    """Display user page."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))

    connection = insta485.model.get_db()
    logname = flask.session["username"]

    logged_user = connection.execute(
        "SELECT username, fullname "
        "FROM users "
        "WHERE username = ?",
        (logname,),
    ).fetchone()

    us = connection.execute(
        "SELECT username, fullname "
        "FROM users "
        "WHERE username = ?",
        (user_url_slug,),
    ).fetchone()

    if us is None:
        flask.abort(404)

    t_posts = connection.execute(
        "SELECT COUNT(postid) AS total_posts "
        "FROM posts "
        "WHERE owner = ?",
        (user_url_slug,),
    ).fetchone()

    t_following = connection.execute(
        """
        SELECT COUNT(followee) AS total_following
        FROM following
        WHERE follower = ?
        """,
        (user_url_slug,),
    ).fetchone()

    con5 = connection.execute(
        """
        SELECT COUNT(follower) AS total_followers
        FROM following
        WHERE followee = ?
        """,
        (user_url_slug,),
    )
    t_followers = con5.fetchone()

    con6 = connection.execute(
        """
        SELECT postid, filename
        FROM posts
        WHERE owner = ?
        ORDER BY postid DESC
        """,
        (user_url_slug,),
    )
    user_posts = con6.fetchall()

    con7 = connection.execute(
        """
        SELECT follower, followee
        FROM following
        WHERE follower = ? AND followee = ?
        """,
        (logname, user_url_slug),
    )
    user_fol = con7.fetchall()

    logname_follows_username = len(user_fol) != 0

    context = {
        "us": us,
        "logged_user": logged_user,
        "t_posts": t_posts,
        "t_following": t_following,
        "t_followers": t_followers,
        "user_posts": user_posts,
        "logname_follows_username": logname_follows_username,
    }
    return flask.render_template("user.html", **context)
