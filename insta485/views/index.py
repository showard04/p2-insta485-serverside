"""Insta485 index view."""
import flask
import arrow
import insta485


@insta485.app.route("/")
def show_index():
    """Display / route."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))
    
    logname = "awdeorio"
    # Connect to database
    connection = insta485.model.get_db()
    con1 = connection.execute("""
        SELECT DISTINCT U.username, U.filename
        FROM users U""")
    users = con1.fetchall()

    con2 = connection.execute("""
        SELECT username
        FROM users
        WHERE username = ?""", (logname,))
    logged_user = con2.fetchone()

    con3 = connection.execute("""
        SELECT P.postid, P.filename, P.owner, P.created
        FROM posts P
        JOIN following F ON P.owner = F.followee
        WHERE F.follower = ?
        UNION
        SELECT P2.postid, P2.filename, P2.owner, P2.created
        FROM posts P2
        WHERE P2.owner = ?
        ORDER BY P2.created DESC""", (logname, logname))
    posts = con3.fetchall()

    humantime_dict = {}
    for post in posts:
        time_created = str(post['created'])
        arrow.get(time_created)
        now = arrow.utcnow()
        time_created = now.to('US/Eastern')
        timestamp = time_created.humanize()
        humantime_dict.update({post['postid']: timestamp})

    con4 = connection.execute("""
        SELECT postid, owner, COUNT(likeid) AS like_count
        FROM likes
        GROUP by postid""")
    likes = con4.fetchall()

    con5 = connection.execute("""
        SELECT owner, postid, text
        FROM comments
        ORDER BY created ASC""")
    comments = con5.fetchall()

    # Add database info to context
    context = {
        "users": users,
        "logged_user": logged_user,
        "posts": posts,
        "likes": likes,
        "comments": comments,
        "humantime_dict": humantime_dict
    }
    return flask.render_template("index.html", **context)
