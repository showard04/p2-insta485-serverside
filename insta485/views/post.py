"""Post route."""

import flask
import insta485


@insta485.app.route("/posts/<int:postid>/")
def show_post(postid):
    """Display one post."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))

    logname = flask.session["username"]
    connection = insta485.model.get_db()

    post = connection.execute(
        """
        SELECT posts.postid, posts.filename, posts.owner, posts.created,
               users.filename AS owner_img_url
        FROM posts
        JOIN users ON posts.owner = users.username
        WHERE posts.postid = ?
        """,
        (postid,),
    ).fetchone()

    if post is None:
        flask.abort(404)

    comments = connection.execute(
        """
        SELECT commentid, owner, text
        FROM comments
        WHERE postid = ?
        ORDER BY commentid
        """,
        (postid,),
    ).fetchall()

    likes = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM likes
        WHERE postid = ?
        """,
        (postid,),
    ).fetchone()["count"]

    liked = connection.execute(
        """
        SELECT 1
        FROM likes
        WHERE postid = ? AND owner = ?
        """,
        (postid, logname),
    ).fetchone() is not None

    context = {
        "logname": logname,
        "post": post,
        "comments": comments,
        "likes": likes,
        "liked": liked,
    }
    return flask.render_template("post.html", **context)
