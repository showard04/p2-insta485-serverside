"""
Insta485 explore.

URLs include:
/explore/
"""
import flask
import insta485

@insta485.app.route('/explore/')
def show_explore():
    connection = insta485.model.get_db()

    logname = "awdeorio"
    con = connection.execute("""
        SELECT username
        FROM users
        WHERE username = ?""", 
        (logname,))
    logged_user = con.fetchone()

    con2 = connection.execute(""" 
        SELECT DISTINCT U.username, U.filename
        FROM users U""")
    users = con2.fetchall()

    con3 = connection.execute(
        "SELECT DISTINCT F.followee "
        "FROM following F "
        "WHERE F.followee NOT IN "
        "(SELECT DISTINCT F1.followee "
        "FROM following F1 "
        "WHERE F1.follower = ?) AND F.followee != ?", 
        (logname, logname))
    not_following = con3.fetchall()

    context = {
        "users": users,
        "logged_user": logged_user,
        "not_following": not_following
    }
    return flask.render_template("explore.html", **context)