import os

from flask import Flask, render_template, g, session, redirect, url_for
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import flask,flask_socketio
from flask_socketio import SocketIO
import flask
import flask_socketio
import datetime

def create_app(test_config=None):
    # create and configure the app. aka Application Factory
    app = Flask(__name__, instance_relative_config=True)
    
    # Counter class for user number
    class Counter:
        def __init__(self, initial_value:int = 0): self.count = initial_value
        def change(self, by:int = 1): self.count += by
            
    # Setup
    # app = flask.Flask(__name__, template_folder = "template")
    app.config["SECRET_KEY"] = "TOTALLY_SECURE"
    socket_io = flask_socketio.SocketIO(app)
    user_database = {} #dict file to sotre msgs
    users_connected = Counter() 
    messages_sent = Counter()
    LOG_LOCATION = "log.txt"
    UTC_TIMEZONE_OFFSET = -4 # EDT
    
    # Log
    def log(text_to_log:str, file:str = LOG_LOCATION):
        # print(text_to_log)
        with open (file = LOG_LOCATION, mode = "a") as log_text_file: log_text_file.write(text_to_log + "\n")
            
    # Get current time (shifted to timezone)
    def get_current_time():
        return (datetime.datetime.utcnow() + datetime.timedelta(hours = UTC_TIMEZONE_OFFSET)).strftime("%m/%d/%Y")
    
    app.config.from_mapping(
            SECRET_KEY='dev',
            DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
            )   
    
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
    
    return app
