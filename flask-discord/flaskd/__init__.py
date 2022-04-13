import os

from flask import Flask, render_template, g, session, redirect, url_for
from flask_socketio import SocketIO, send, emit, join_room, leave_room

def create_app(test_config=None):
    # create and configure the app. aka Application Factory
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
            SECRET_KEY='dev',
            DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
            )
    socketio = SocketIO(logger=True,engineio_logger=True)
    socketio.init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure instance folder exists. Where app instance kept. Not tracked by git.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Register db connection with app
    from . import db
    db.init_app(app)


    from . import auth
    app.register_blueprint(auth.bp)

    @app.route("/")
    @auth.login_required
    def index():
        username = g.user["username"] # Grabs username from database fetch stored in g upon user request of the page
                                      # Stored in auth.py
        return render_template('layout.html',username=username)

    #Logout redirects to login page
    @app.route('/logout')
    def logout():
        if request.method=="POST":
            session.clear()
            return redirect(url_for('auth.login'))
    
    # a simple page that prints the view number
    # index page
    @app.route('/count')
    def simple_view():
        sql_db = db.get_db()

        # Check whether views table has any rows. If empty, intialze new siteViews column to 1
        check = sql_db.execute("SELECT views FROM siteViews WHERE rowid=1"
                ).fetchone()
        if check == None:
            sql_db.execute("INSERT INTO siteViews (views) VALUES (1)")
        else:
            sql_db.execute("UPDATE siteViews SET views = views +1 WHERE rowid=1") # Only update 1 row in db


        sql_db.commit()

        num_views = sql_db.execute("SELECT views FROM siteViews WHERE rowid = 1"
                ).fetchone()[0] #Fetchone returns tuple. 1st element contains row value

        return render_template('index_count.html',content=num_views)
    
    #from . import socket
    #app.register_blueprint(socket.bp)

    @socketio.on('join')
    def on_join(data):
        room = data["room"]
        username = data["username"]
        timestamp = data["timestamp"]
        join_room(room)
        data["message"] = username + " has joined " + room
        emit("chat message",data,json=True,to=room)
        
    return app
