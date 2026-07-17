"""Insta485 index view."""

import arrow
import flask
import insta485


def _get_users(connection):
    return connection.execute(
        """
        SELECT DISTINCT U.username, U.filename
        FROM users U
        """
    ).fetchall()


def _get_logged_user(connection, logname):
    return connection.execute(
        """
        SELECT username
        FROM users
        WHERE username = ?
        """,
        (logname,),
    ).fetchone()


def _get_posts(connection, logname):
    return connection.execute(
        """
        SELECT P.postid, P.filename, P.owner, P.created
        FROM posts P
        JOIN following F ON P.owner = F.followee
        WHERE F.follower = ?
        UNION
        SELECT P2.postid, P2.filename, P2.owner, P2.created
        FROM posts P2
        WHERE P2.owner = ?
        ORDER BY created DESC
        """,
        (logname, logname),
    ).fetchall()


def _get_humantime_dict(posts):
    humantime_dict = {}

    for post in posts:
        time_created = str(post['created'])
        arrow.get(time_created)
        now = arrow.utcnow()
        time_created = now.to('US/Eastern')
        timestamp = time_created.humanize()
        humantime_dict.update({post["postid"]: timestamp})

    return humantime_dict


def _get_likes(connection):
    return connection.execute(
        """
        SELECT postid, owner, COUNT(likeid) AS like_count
        FROM likes
        GROUP BY postid
        """
    ).fetchall()


def _get_comments(connection):
    return connection.execute(
        """
        SELECT owner, postid, text
        FROM comments
        ORDER BY created ASC
        """
    ).fetchall()


@insta485.app.route("/")
def show_index():
    """Display / route."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))

    logname = flask.session["username"]
    # Connect to database
    connection = insta485.model.get_db()
    posts = _get_posts(connection, logname)

    # Add database info to context
    context = {
        "users": _get_users(connection),
        "logged_user": _get_logged_user(connection, logname),
        "posts": posts,
        "likes": _get_likes(connection),
        "comments": _get_comments(connection),
        "humantime_dict": _get_humantime_dict(posts),
    }
    return flask.render_template("index.html", **context)
