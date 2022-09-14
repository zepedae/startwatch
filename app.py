#to activate virtual environment 
#python3 -m venv .venv
#source .venv/bin/activate

#install flask
#pip install flask

#install mysql connector
#pip install mysql-connector-python

# mysql -p then enter to connect to sql database

import os
import mysql.connector
import time
import json

from flask import Flask, render_template, request, session, redirect, jsonify
#from flask_session.__init__ import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date

from helpers import apology, login_required

#Create object using mysql connector
conn = mysql.connector.connect(host="localhost", database="startwatch", user="root", password="Redd!tisl13fe")

#Configure application
app = Flask(__name__)

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
            return render_template("watches.html")
            

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/watches", methods = ["GET", "POST"])
@login_required
def watches():
    if request.method == "POST":
        time = request.args.get("time")
        time_elapsed = time['time']

        return render_template("watches.html", bloop = time_elapsed)

        user_id = session['id']
        watch_name = "project 1"

        date = date.today()

        cursor = conn.cursor(dictionary = True, buffered = True)
        cursor.execute("SELECT date FROM watches WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id, ))
        last_date = cursor.fetchone()

        cursor.close()
        
        if not last_date or last_date['date'] < date:
            cursor = conn.cursor(dictionary = True, buffered = True)
            cursor.execute("INSERT INTO watches (user_id, watch_name, date, time_elapsed VALUES (%s, %s, %s, %s)", (user_id, watch_name, date, time_elapsed, ))
            conn.commit()
            cursor.close()

        else:
            cursor = conn.cursor(dictionary = True, buffered = True)
            cursor.execute("UPDATE watches SET time = ADDTIME(time + %s) WHERE id = %s AND date = %s", (time_elapsed, user_id, date, ))
            conn.commit()
            cursor.close()

    return render_template("watches.html")


