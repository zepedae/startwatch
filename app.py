#to activate virtual environment 
#source .venv/bin/activate

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

# create connection object using mysql connector
conn = mysql.connector.connect(host="localhost", database="startwatch", user="root", 
                               password="slamdunk")

# configure application
app = Flask(__name__)

# set up Flask to bypass CORS at the front end
cors = CORS(app)

# ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# landing page
@app.route("/")
def landing():
    return render_template("landing.html")

# Register new user
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # forget user_id
    session.clear()

    # user reached route via POST
    if request.method == "POST":

        # did user provide name
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # check to see if username exists
        username = request.form["username"]
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,) )
        rows = cursor.fetchall()

        # if new username exists display error 
        if len(rows) > 0:
            return apology("username already exists", 400)

        # check for password
        if not request.form.get("password"):
            return apology("must provide password", 400)

        # check that password is matching
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # if new username and correct password then create new user
        else:
            password = generate_password_hash(request.form.get("password"))
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                           (username, password,) )
            conn.commit()
        
        cursor.close()

        # log user in 
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,) )
        new_user = cursor.fetchone()

        session['loggedin'] = True
        session['id'] = new_user[0]
        session['username'] = new_user[1]
        
        return redirect("/create_watch")

    else:
        return render_template("register.html")

# user login
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # forget any user_id
    session.clear()

    # user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        #check if username and password were provided
        if not request.form['username'] or not request.form['password']:
            return apology("enter username and password", 400)


        # check if username and password match registered user
        username = request.form['username']
        password = request.form['password']
        cursor = conn.cursor(dictionary = True, buffered = True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username, ))
        cursor.close()
        user = cursor.fetchone()

        # log in if user exists
        if not user:
            return apology("user does not exist", 400)

        else:
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            return redirect("/watches")
            

    else:
        return render_template("login.html")

# user logout
@app.route("/logout")
def logout():
    """Log user out"""

    # forget any user_id
    session.clear()

    return redirect("/")

# stopwatch to record productivity
@app.route("/stopwatch", methods = ["GET", "POST"])
@login_required
def stopwatch():

    # get project name
    watch_name = session["watch_name"]

    # send productivity time to database
    if request.method == "POST":
        data = request.get_json()

        # get data to store
        time = data.get('time_elapsed')
        user_id = session['id']
        today = date.today()

        cursor = conn.cursor(dictionary = True, buffered = True)
        get_info = "SELECT date FROM times WHERE user_id=%s AND watch_name=%s ORDER BY id DESC LIMIT 1"
        cursor.execute(get_info, (user_id, watch_name, ))
        last_date = cursor.fetchone()
        cursor.close()

        # enter the "time" directly if first entry of the day
        if not last_date or last_date['date'] < today:
            cursor = conn.cursor(dictionary = True, buffered = True)
            insert_time = "INSERT INTO times (user_id, watch_name, time_elapsed) VALUES (%s, %s, %s)"
            cursor.execute(insert_time, (user_id, watch_name, time, ))
            conn.commit()
            cursor.close()
        # add time to existing day's entry if a duplicate entry
        else:
            cursor = conn.cursor(dictionary=True, buffered=True)
            add_time = "UPDATE times SET time_elapsed=%s WHERE user_id=%s AND date=%s AND watch_name=%s"
            cursor.execute(add_time, (time, user_id, today, watch_name, ))
            conn.commit()
            cursor.close()

        return 'OK', 200
   
    else:
        return render_template("stopwatch.html", watch_name = watch_name)

# create a new project
@app.route("/create_watch", methods = ["GET", "POST"])
@login_required
def create_watch():

    if request.method == "POST":
        # require new project name
        if not request.form['watch_name']:
            apology("Enter watch name", 400)

        # enter new project in database
        else:
            username = session['username']
            user_id = session['id']
            new_watch = request.form['watch_name']
            goal = request.form['goal']

            cursor = conn.cursor()
            insert_watch = "INSERT INTO watches (username, user_id, watch_name, goal) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_watch, (username, user_id, new_watch, goal, ))
            conn.commit()
            cursor.close()

            return redirect("/watches")
    else:
        return render_template("create_watch.html")

# display user's projects
@app.route("/watches", methods = ["GET", "POST"])
@login_required
def watches():
    if request.method == "GET":
        user_id = session['id']

        # get project names
        cursor = conn.cursor(buffered=True)
        cursor.execute("SELECT watch_name FROM watches WHERE user_id = %s", (user_id, ))
        watches = cursor.fetchall()
        cursor.close()
        
        # display names and user options
        return render_template("watches.html", watches = watches)

    # redirect to selected watch function
    else:
        if "stopwatch" in request.form:
            session["watch_name"] = request.form.get("stopwatch","")
            return redirect("/stopwatch")
        elif "visualize" in request.form:
            session["watch_name"] = request.form.get("visualize","")
            return redirect("/visualize")
        else: 
            session["watch_name"] = request.form.get("edit","")
            return redirect("/edit_watch")

# visualize productivity data
@app.route("/visualize", methods = ["GET"])
@login_required
def visualize():

    watch_name = session["watch_name"]
    user_id = session["id"]

    # get productivity data and goal
    if request.method == "GET":
        cursor = conn.cursor(buffered=True)
        cursor.execute("SELECT date, time_elapsed FROM times WHERE user_id = %s AND watch_name = %s", (user_id, watch_name, ))
        times = cursor.fetchall()
        cursor.close()

        # seralize data to JSON
        timesArr = []
        for i in times:
            timesStr = json.dumps(i, default = str)
            timesArr.append(timesStr)
        
        cursor = conn.cursor(buffered=True)
        cursor.execute("SELECT goal FROM watches WHERE user_id = %s AND watch_name = %s", (user_id, watch_name, ))
        goal = cursor.fetchone()[0]
        cursor.close()

        # send data for visualization
        return render_template("visualize.html", times = timesArr, watch_name = watch_name, goal = goal)

# delete project or edit name
@app.route("/edit_watch", methods = ["GET", "POST"])
@login_required
def edit_watch():

    watch_name = session["watch_name"]
    user_id = session["id"]
    if request.method == "GET":
        return render_template("edit_watch.html", watch_name = watch_name)
    
    if request.method == "POST":
        
        # change project name
        if "change-name-submit" in request.form:
            new_name = request.form.get("new-name")
            cursor = conn.cursor()
            cursor.execute("UPDATE watches SET watch_name = %s WHERE watch_name = %s AND user_id = %s", (new_name, watch_name, user_id, ))
            conn.commit()
            cursor.close()
            cursor = conn.cursor()
            cursor.execute("UPDATE times SET watch_name = %s WHERE watch_name = %s AND user_id = %s", (new_name, watch_name, user_id, ))
            conn.commit()
            cursor.close()
            session["watch_name"] = new_name
            return render_template("edit_watch.html", watch_name = new_name)
        
        # change project goal
        if "change-goal-submit" in request.form:
            new_goal = request.form.get("new-goal")
            cursor = conn.cursor()
            cursor.execute("UPDATE watches SET goal = %s WHERE watch_name = %s AND user_id = %s", (new_goal, watch_name, user_id, ))
            conn.commit()
            cursor.close()
            return render_template("edit_watch.html", watch_name = watch_name)
        
        # delete project from database
        if "delete-submit" in request.form:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM watches WHERE watch_name = %s AND user_id = %s", 
                           (watch_name, user_id, ))
            conn.commit()
            cursor.close()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM times WHERE watch_name = %s AND user_id = %s", 
                           (watch_name, user_id, ))
            conn.commit()
            cursor.close()
            session.pop("watch_name")
            return redirect("/watches")
        if "cancel-submit" in request.form:
            return render_template("edit_watch.html", watch_name = watch_name)

if __name__ == "__main__": 
   app.run(debug=True)