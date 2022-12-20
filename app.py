#to activate virtual environment 
#source .venv/bin/activate

#install flask
#pip3 install flask

#install mysql connector
#pip3 install mysql-connector-python

# mysql -p (esc) then enter to connect to sql database

import os
import mysql.connector
import time
import json

from flask import Flask, render_template, request, session, redirect, jsonify
from flask_session.__init__ import Session
from flask_cors import CORS
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date

from helpers import apology, login_required

#Create object using mysql connector
conn = mysql.connector.connect(host="localhost", database="startwatch", user="root", password="slamdunk")

#Configure application
app = Flask(__name__)

#Set up Flask to bypass CORS at the front end
cors = CORS(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # forget user_id
    session.clear()

    # User reached route via POST
    if request.method == "POST":

        # did user provide name
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # check to see if there is already that username
        username = request.form["username"]
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,) )
        rows = cursor.fetchall()

        if len(rows) > 0:
            return apology("username already exists", 400)

        if not request.form.get("password"):
            return apology("must provide password", 400)

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        else:
            password = generate_password_hash(request.form.get("password"))
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password,) )
            conn.commit()
        
        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
    
        if not request.form['username'] or not request.form['password']:
            return apology("enter username and password", 400)


        # Check if username and password match registered user
        username = request.form['username']
        password = request.form['password']
        cursor = conn.cursor(dictionary = True, buffered = True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username, ))
        user = cursor.fetchone()

        # Log in if user exists
        if not user:
            return apology("user does not exist", 400)

        else:
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            return render_template("stopwatch.html")
            

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/stopwatch", methods = ["POST", "GET"])
@login_required
def stopwatch():
    if request.method == "POST":
        data = request.form['display']
        # bloop = jsonify(data)
        # print(bloop)

        return render_template("stopwatch.html", time = data)

    else:
        return render_template("stopwatch.html", time = "bloop")


@app.route("/create_watch", methods = ["GET", "POST"])
@login_required
def create_watch():
    if request.method == "POST":
        if not request.form['watch_name']:
            apology("Enter watch name", 400)
        else:
            username = session['username']
            user_id = session['id']
            watch_name = request.form['watch_name']

            cursor = conn.cursor()
            cursor.execute("INSERT INTO watches (username, user_id, watch_name) VALUES (%s, %s, %s)", (username, user_id, watch_name, ) )
            conn.commit()

            added = "{} watch has been added!".format(watch_name)

            return render_template("create_watch.html", added=added)
    else:
        return render_template("create_watch.html")


if __name__ == "__main__": 
   app.run(debug=True)