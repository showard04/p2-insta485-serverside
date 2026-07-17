"""Insta485 explore."""
import flask
import insta485


@insta485.app.route('/explore/')
def show_explore():
    """Display / explore."""
    connection = insta485.model.get_db()

    logname = flask.session["username"]
    con = connection.execute("""
        SELECT username
        FROM users
        WHERE username = ?""", (logname,))
    logged_user = con.fetchone()

    con2 = connection.execute("""
        SELECT DISTINCT U.username, U.filename
        FROM users U""")
    users = con2.fetchall()

    con3 = connection.execute(
        "SELECT U.username "
        "FROM users U "
        "WHERE U.username NOT IN "
        "(SELECT F1.followee "
        "FROM following F1 "
        "WHERE F1.follower = ?) AND U.username != ?", (logname, logname))
    not_following = con3.fetchall()

    context = {
        "users": users,
        "logged_user": logged_user,
        "not_following": not_following
    }
    return flask.render_template("explore.html", **context)
