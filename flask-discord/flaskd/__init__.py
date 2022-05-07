import os

from flask import Flask, render_template, g, session, redirect, url_for,request
#
import flask,flask_socketio
from flask_socketio import SocketIO
import flask
import flask_socketio
import datetime
#
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath

def create_app(test_config=None):
    # create and configure the app. aka Application Factory
    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = "TOTALLY_SECURE"
    app.app_context().push() #to use create_app in auth
    #########

    # ### uploading image#####
    UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/images/..')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        
    @app.route('/upload')
    def upload_form():
        return render_template('upload.html')

    @app.route('/upload', methods=['POST'])
    def upload_image():
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename) #principle "never trust user input"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #print('upload_image filename: ' + filename)
            flash('Image successfully uploaded and displayed below')
            return render_template('upload.html', filename=filename)
            # return redirect(url_for('upload_image',filename=filename))
        else:
            flash('Allowed image types are -> png, jpg, jpeg, gif')
            return redirect(request.url)

    @app.route('/display/<filename>')
    def display_image(filename):
        #print('display_image filename: ' + filename)
        return redirect(url_for('static', filename='uploads/' + filename), code=301)
        ### uploading image ending #####

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
    app.config["count"]=0
    # Log
    def log(text_to_log:str, file:str = LOG_LOCATION):
        # print(text_to_log)
        with open (file = LOG_LOCATION, mode = "a") as log_text_file: log_text_file.write(text_to_log + "\n")
    # Get current time (shifted to timezone)
    def get_current_time():
        return (datetime.datetime.utcnow() + datetime.timedelta(hours = UTC_TIMEZONE_OFFSET)).strftime("%m/%d/%Y")
    
    # Chatroom functions ==============================================================================
    # User connection handler
    @socket_io.on("user_connection")
    def user_connect_handler(data:dict):
        users_connected.change(by = 1)
        flask_socketio.send(f"{data['username']} has joined the chatroom! There are now {users_connected.count} users in this chatroom.", broadcast = True)
        # Add to database
        user_database[flask.request.sid] = data["username"]

        log(text_to_log = f"{flask.request.sid}: {data['username']} joined | Database: {user_database} | {get_current_time()}")

    # User disconnection handler
    @socket_io.on("disconnect")
    def user_disconnection_handler():
        # username = user_database[flask.request.sid]
        username = g.user["username"]
        users_connected.change(by = -1)
        flask_socketio.send(f"{username} has left the chatroom! There are now {users_connected.count} users in this chatroom.", broadcast = True)
        # Remove from database
        del user_database[flask.request.sid]

        log(text_to_log = f"{flask.request.sid}: {username} left | Database: {user_database} | {get_current_time()}")

    # Send message handler
    @socket_io.on("send_message")
    def send_message_handler(data:dict):
        messages_sent.change(by = 1)
        flask_socketio.send(f"[#{str(messages_sent.count).zfill(4)}] {user_database[flask.request.sid]}: {data['message']}", broadcast = True)

        log(text_to_log = f"{flask.request.sid}: {user_database[flask.request.sid]} sent message with data: \"{data}\" | Database: {user_database} | {get_current_time()}")

    # Message handler
    @socket_io.on("message")
    def message_handler(message:str):
        # print(f"Message recieved at {datetime.datetime.utcnow()} (GMT): \"{message}\"")
        flask_socketio.send(message, broadcast = True)

        log(text_to_log = f"Sending message to all: {message} | {get_current_time()}")
    # Website navigation =============================================================================

    # Chatroom
    @app.route("/chatroom", methods = ["POST", "GET"])
    def chatroom():
        # Send to chatroom with username
        username = g.user["username"]
        return flask.render_template("chatroom.html", username = username)

    # Run
    if __name__ == "__main__":
        socket_io.run(app)

    ###################


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
        return render_template('layout.html',username=username,passing_token=app.config['TOKEN'])

    #Logout redirects to login page
    @app.route("/logout",methods=("GET","POST"))
    def logout():
        if request.method == "POST":
            session.clear()
            app.config["count"]-=1
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
