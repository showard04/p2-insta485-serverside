# Posts routes

import sqlite3

import flask
import insta485
import pathlib
import uuid
from insta485.views.accounts import login_required

@insta485.app.route("/posts/", methods=["POST"])
def update_posts():

    response = login_required() # login check
    if response:
        return response

    username = flask.session["username"]

    operation = flask.request.form["operation"] # check if user is creating or deleting

    conn = sqlite3.connect(insta485.app.config["DATABASE_FILENAME"])
   
    conn.row_factory = sqlite3.Row

    if operation == "create":

        
        fileobj = flask.request.files["file"] # get the image

       
        filename = fileobj.filename

        if filename == "": # make sure the file was valid
            conn.close()
            flask.abort(400)   # Bad Request

        
        stem = uuid.uuid4().hex # generate a unique file name
        suffix = pathlib.Path(filename).suffix.lower() 
        uuid_basename = f"{stem}{suffix}"

        
        path = insta485.app.config["UPLOAD_FOLDER"] / uuid_basename # image path
        fileobj.save(path)

        # Update data base with this new post
        conn.execute(
            """
            INSERT INTO posts(filename, owner)
            VALUES (?, ?)
            """,
            (uuid_basename, username),
        )

        conn.commit()
        conn.close()

        redirect_url = flask.request.args.get(
            "target",
            f"/users/{username}/"
        )

        return flask.redirect(redirect_url)

    # If the user decides to delete a post
    elif operation == "delete":

       
        postid = flask.request.form["postid"]
        result = conn.execute(
            """
            SELECT owner, filename
            FROM posts
            WHERE postid = ?
            """,
            (postid,),
        ).fetchone()

        # make sure the post exists and is owned by the user
        if result is None:
            conn.close()
            flask.abort(404)   

       
        if result["owner"] != username:
            conn.close()
            flask.abort(403)

       # get the image path and then unlink it (delete it)
        path = (
            insta485.app.config["UPLOAD_FOLDER"]
            / result["filename"]
        )

        
        path.unlink(missing_ok=True) 

        # removing the post from the data base
        conn.execute(
            """
            DELETE FROM posts
            WHERE postid = ?
            """,
            (postid,),
        )

        # remove data associated with deleted post as well
        conn.execute(
            """
            DELETE FROM comments
            WHERE postid = ?
            """,
            (postid,),
        )
        conn.execute(
            """
            DELETE FROM likes
            WHERE postid = ?
            """,
            (postid,),
        )
        conn.execute(
            """
            DELETE FROM posts
            WHERE postid = ?
            """,
            (postid,),
        )
 
        conn.commit()
        conn.close()

        redirect_url = flask.request.args.get(
            "target",
            f"/users/{username}/"
        )

        return flask.redirect(redirect_url)

    else:
        conn.close()
        flask.abort(400)