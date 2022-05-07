import email
import functools

from flask import ( 
        Blueprint, flash, g, redirect, render_template, request, session, url_for
        )

from werkzeug.security import check_password_hash, generate_password_hash

from flaskd.db import get_db
# imports for PyJWT authentication
import jwt
import datetime
from functools import wraps
from flask import Flask, request, jsonify, make_response, current_app

#imports for image upload
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
import os   

# from flask_wtf.file import FileField
# from wtforms import SubmitField
# from flask_wtf import Form


bp = Blueprint('auth',__name__,url_prefix='/auth')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        # jwt is passed in the request header
        if 'x_access_token' in request.headers:
            token = request.headers['x-access-token']

        # return 401 if token is not passed
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
  
        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(current_app.config['TOKEN'], current_app.config['SECRET_KEY'])
            # print(data)
        except:
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        # returns the current logged in users contex to the routes
        return  f(*args, **kwargs)
  
    return decorated

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))  
        return view(**kwargs)
    return wrapped_view

@bp.route("/settings",methods=("GET","POST"))
@login_required
@token_required
def change_username():
    if request.method == "POST":
        new_username=request.form["uname"]
        email=request.form['email']
        # print(new_username)
        db = get_db()
        db.execute("UPDATE user SET username =? WHERE email=?",(new_username,email))
        db.commit()
        return redirect(url_for("index"))
    return render_template("settings.html",passing_token=current_app.config['TOKEN'])

@bp.route("/login",methods=("GET","POST"))
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute("SELECT * FROM user WHERE email = ?", (email,)
                ).fetchone()
        
        if user == None: 
            error = "Incorrect Email Provided!" 
            
        elif not check_password_hash(user["password"],password):
            error = "Incorrect password!"
            
        if error == None:
            session.clear()
            session["user_id"] = user["id"]
            payload={
                "user_email":user["email"],
                "user_ID":user["id"],
                "user_password":user["password"]
                }
            current_app.config['TOKEN']=jwt.encode({'data':payload, 'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=30)},current_app.config['SECRET_KEY'])
            print(current_app.config['TOKEN'])
            make_response(jsonify({'token':current_app.config['TOKEN'].decode('UTF-8')}),201)
            current_app.config["count"]+=1
            return redirect(url_for("index"))
        flash(error)

    return render_template("login.html")

@bp.route("/register", methods=("GET", "POST"))
def register():
    """ Registers user from regiseter.html form submission"""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conifrm_password=request.form["Confirm Password"]
        db = get_db()
        error = None

        if not email: # Checking where email and password are empty values. 
            error = "Email is Required!"
        elif not password:
            error = "Password is Required!"
        elif password!=conifrm_password:
            error="Password Didn't Match, Try Again"

        if error == None:
            try:
                db.execute("INSERT INTO user (email,password) VALUES (?, ?)", (email, generate_password_hash(password)))

                db.commit()
            
            except db.IntegrityError:
                error = "Email {} is already registered.".format(email)

            else:
                error="Successfuly Registerd"
                flash(error)
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("register.html")

@bp.before_app_request
def load_logged_in_user():
    """ Load logged in user information by identifying if session contains the user id. 
        If user logged in, queries database and grabs information"""
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
                ).fetchone() # Grabs all columns in the user table where user_id is found. Load this in the session
                
