"""Insta485 index (followers) view."""
import flask
import insta485


@insta485.app.route('/users/<user_url_slug>/followers/')
def show_followers(user_url_slug):
    """Display / followers route."""
    logname = "awdeorio"
    connection = insta485.model.get_db()
    target_user = connection.execute(
        "SELECT username FROM users WHERE username = ?",
        (user_url_slug,),
    ).fetchone()

    # if the user doesn't exist
    if target_user is None:
        connection.close()
        flask.abort(404)

    con = connection.execute("""
        SELECT F.follower, U.username, U.filename AS user_img_url
        FROM following F
        JOIN users U ON F.follower = U.username
        WHERE F.followee = ?""", (user_url_slug,))
    followers = con.fetchall()
    print(followers)

    con2 = connection.execute("""
        SELECT F.followee
        FROM following F
        WHERE F.follower = ?""", (logname,))
    logname_following_data = con2.fetchall()
    logname_following_list = []
    for item in logname_following_data:
        logname_following_list.append(item['followee'])
    print(logname_following_list)

    context = {
        "followers": followers,
        "logname": logname,
        "logname_following_list": logname_following_list}
    return flask.render_template("followers.html", **context)
