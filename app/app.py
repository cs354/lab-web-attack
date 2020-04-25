import sqlite3
import os
import random
import hashlib
import string


from flask import Flask, session, redirect, url_for, request, render_template, g
from __init__ import create_app

app = create_app()

@app.before_request
def setup_db():
    init = not os.path.exists("app.db")
    if 'db' not in g:
        g.db = sqlite3.connect("app.db")
        g.db.row_factory = sqlite3.Row
    if init:
        app.logger.info("Setting up database first time")
        conn = g.db
        conn.execute("CREATE TABLE  IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR(50), password VARCHAR(50));")
        conn.execute("INSERT INTO users (id, username, password ) VALUES (1,'admin', ?);  ", (randomString(),))
        conn.execute("INSERT INTO users (id, username, password ) VALUES (2,'joe', ?);  ", (hashlib.md5("12345".encode('utf-8')).hexdigest(),))
        conn.execute("INSERT INTO users (id, username, password ) VALUES (3,'schmoe', ?);  ", (randomString(),))
        conn.execute("INSERT INTO users (id, username, password ) VALUES (4,'ychen', ?);  ", (hashlib.md5("msit458".encode('utf-8')).hexdigest(),))
        conn.execute("INSERT INTO users (id, username, password ) VALUES (5,'guest', ?);  ", (hashlib.md5("msit458".encode('utf-8')).hexdigest(),))
        conn.execute("CREATE TABLE  IF NOT EXISTS posts (id INTEGER PRIMARY KEY, user_id VARCHAR(50), title VARCHAR(50), content TEXT);")
        conn.execute("INSERT INTO posts (id, user_id, title, content ) VALUES (1,1,'Welcome to the forum','Welcome to the first day of the forum, please be respectful of your fellow forumites.')")
        conn.execute("INSERT INTO posts (id, user_id, title, content ) VALUES (2,2,'HTTPS on the forum?','Hi admin is there any chance we will see https support for the forum?' );")
        conn.execute("INSERT INTO posts (id, user_id, title, content ) VALUES (3,3,'Crazy new video leaked!','You guys have to check this out https://tinyurl.com/2fcpre6 let me know what you think (;' );")
        conn.commit()


@app.after_request
def after_request(response):
    if 'db' in g and g.db is not None:
        g.db.commit()
        g.db.close()
    return response


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route("/contact",methods=['GET'])
def contact_form():
    if 'user_id' not in session:
        return redirect('/')
    return render_template("contact.html",username=session['username'])

@app.route("/contact",methods=['POST'])
def post_contact_form():
    if 'user_id' not in session:
        return redirect('/')
    msg = request.form['message']

    cmd = "echo "+msg+" >> /usr/src/app/admin_log"
    os.system(cmd)
    return render_template("contact.html", username=session['username'], alert="Executed: "+cmd)


@app.route("/forum/<post_id>/destroy",methods=['POST'])
def remove(post_id):
    if 'user_id' not in session:
        return redirect('/')
    g.db.execute("DELETE FROM posts where id=? and user_id=?",(int(post_id),session['user_id']))

    return redirect("/forum")
@app.route('/forum', methods=['POST'])
def post():
    if 'user_id' not in session:
        return redirect('/')
    title = request.form['title']
    content = request.form['content']
    error = None
    if len(title) < 5 or len(content) < 5:
        app.logger.info("Error content too short")
        error = "Title and content must be at least 10 characters"
    else:
        user_id = session['user_id']
        g.db.execute("INSERT INTO posts (user_id, title, content) VALUES (?,?,?);",(user_id, title, content))
        g.db.commit()

    return render_template('forum.html', posts=get_posts(), username=session['username'], error=error)


@app.route('/forum', methods=['GET'])
def forum():
    if 'user_id' not in session:
        return redirect('/')
    else:
        posts = get_posts()
        return render_template("forum.html", posts=posts, username=session['username'])


@app.route('/', methods=['GET', 'POST'])
def login():
    conn = sqlite3.connect('app.db')
    msg = None
    if request.method == "POST":
        username = request.form['username']
        password = hashlib.md5(request.form['password'].encode('utf-8')).hexdigest()
        query = "SELECT id,username FROM users where password='" + password + "' and username='" + username + "' LIMIT 1;"
        res = conn.execute(query)
        data = res.fetchall()
        if len(data) != 0:
            user_id = data[0][0]
            username = data[0][1]
            session['user_id'] = user_id
            session['username'] = username
            app.logger.info("--- User id: {}".format(user_id))
            return redirect('/forum')
        app.logger.info("Result of query: {}".format(data))
        msg = query

    conn.close()
    return render_template('login.html', msg=msg)

def get_posts():
    res = g.db.execute(
        "SELECT posts.id,posts.user_id,posts.title,posts.content,users.username FROM posts INNER JOIN users on posts.user_id = users.id ORDER BY posts.id DESC;")
    return res

def randomString(stringLength=50):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))
