"""Insta485 index (user) view."""
import flask
import insta485


@insta485.app.route('/users/<user_url_slug>/',)
def show_user(user_url_slug):
    """Display / users."""
    # Connect to database
    connection = insta485.model.get_db()
    logname = flask.session["username"]

    con = connection.execute(
        "SELECT username, fullname  "
        "FROM users "
        "WHERE username = ?", (logname, ))
    logged_user = con.fetchone()

    con2 = connection.execute(
        "SELECT username, fullname  "
        "FROM users "
        "WHERE username = ?", (user_url_slug, ))
    us = con2.fetchone()

    con3 = connection.execute(
        "SELECT COUNT(postid) AS total_posts "
        "FROM posts "
        "WHERE owner = ? "
        "GROUP BY owner ", (user_url_slug, ))
    t_posts = con3.fetchone()

    con4 = connection.execute("""
        SELECT COUNT(follower) AS total_following
        FROM following
        WHERE follower = ?
        GROUP BY follower""", (user_url_slug, ))
    t_following = con4.fetchone()

    con5 = connection.execute("""
        SELECT COUNT(followee) AS total_followers
        FROM following
        WHERE followee = ?
        GROUP BY followee""", (user_url_slug, ))
    t_followers = con5.fetchone()

    con6 = connection.execute("""
        SELECT postid, filename
        FROM posts
        WHERE owner = ?""", (user_url_slug, ))
    user_posts = con6.fetchall()

    con7 = connection.execute("""
        SELECT follower, followee
        FROM following
        WHERE follower = ? AND followee = ? """, (logname, user_url_slug, ))
    user_fol = con7.fetchall()

    if len(user_fol) != 0:
        logname_follows_username = True
    else:
        logname_follows_username = False

    context = {
        "us": us,
        "logged_user": logged_user,
        "t_posts": t_posts,
        "t_following": t_following,
        "t_followers": t_followers,
        "user_posts": user_posts,
        "logname_follows_username": logname_follows_username
    }
    return flask.render_template("user.html", **context)
