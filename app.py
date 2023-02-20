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
        
        cursor.close()
        
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
        cursor.close()
        user = cursor.fetchone()

        # Log in if user exists
        if not user:
            return apology("user does not exist", 400)

        else:
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            return redirect("/")
            

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/stopwatch", methods = ["GET", "POST"])
@login_required
def stopwatch():
    if request.method == "POST":
        data = request.get_json()

        time = data.get('time_elapsed')
        project = data.get('project_name')
        user_id = session['id']
        today = date.today()

        cursor = conn.cursor(dictionary = True, buffered = True)
        cursor.execute("SELECT date FROM times WHERE user_id=%s AND watch_name=%s ORDER BY id DESC LIMIT 1", (user_id, project, ))
        last_date = cursor.fetchone()
        cursor.close()

        if not last_date or last_date['date'] < today:
            cursor = conn.cursor(dictionary = True, buffered = True)
            cursor.execute("INSERT INTO times (user_id, watch_name, time_elapsed) VALUES (%s, %s, %s)", (user_id, project, time, ) )
            conn.commit()
            cursor.close()
        else:
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute("UPDATE times SET time_elapsed=%s WHERE user_id=%s AND date=%s AND watch_name=%s", (time, user_id, today, project, ))
            conn.commit()
            cursor.close()

        return 'OK', 200
   
    else:
        return render_template("stopwatch.html")


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
            cursor.close()

            added = "{} watch has been added!".format(watch_name)

            return render_template("create_watch.html", added=added)
    else:
        return render_template("create_watch.html")


@app.route("/projects", methods = ["GET", "POST"])
@login_required
def projects():
    if request.method == "GET":
        user_id = session['id']

        cursor = conn.cursor(buffered=True)
        cursor.execute("SELECT watch_name FROM watches WHERE user_id = %s", (user_id, ))
        names = cursor.fetchall()
        cursor.close()
        

        return render_template("projects.html", names = names)

    else:
        if "stopwatch" in request.form:
            session["project"] = request.form.get("stopwatch","")
            return render_template("stopwatch.html", project_name = request.form['stopwatch'])
        elif "visualize" in request.form:
            session["project"] = request.form.get("visualize","")
            return redirect("/visualize")
        else: # "edit" in request.form:
            session["project"] = request.form.get("edit","")
            return redirect("/edit_watch")

@app.route("/visualize", methods = ["GET", "POST"])
@login_required
def visualize():
    project_name = session["project"]
    user_id = session["id"]
    if request.method == "GET":
        cursor = conn.cursor(buffered=True)
        cursor.execute("SELECT date, time_elapsed FROM times WHERE user_id = %s AND watch_name = %s", (user_id, project_name))
        times = cursor.fetchall()
        cursor.close()

        timesArr = []
        for i in times:
            timesStr = json.dumps(i, default = str)
            timesArr.append(timesStr)

        return render_template("visualize.html", times = timesArr, project_name = project_name)

@app.route("/edit_watch", methods = ["GET", "POST"])
@login_required
def edit_watch():
    project_name = session["project"]
    if request.method == "GET":
        return render_template("edit_watch.html", project_name = project_name)

if __name__ == "__main__": 
   app.run(debug=True)