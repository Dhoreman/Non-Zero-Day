import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """homepage"""
    # Check current date
    db.execute("UPDATE datecheck SET current_day = current_date")

    # Collect data to compare
    today = db.execute("SELECT current_day FROM datecheck")
    non_zero_day = db.execute("SELECT last_activity_date FROM users WHERE id=?", session["user_id"])
    yesterday = db.execute("SELECT DATE(current_day,'-1 days') AS yesterday FROM datecheck")

    # Check if user did anything yesterday, if not reset streak
    if non_zero_day[0]['last_activity_date'] < yesterday[0]['yesterday']:
        db.execute("UPDATE users SET days = 0 WHERE id=?", session["user_id"])

    return render_template("index.html", today=today[0]['current_day'], non_zero_day=non_zero_day[0]['last_activity_date'])


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        """Register user"""
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        used_name = db.execute("SELECT username FROM users WHERE username=?", username)

        # Return errors if necessary
        if not username:
            return apology("must provide username", 400)
        elif len(used_name) > 0:
            return apology("Username already taken", 400)
        elif not password or not confirmation:
            return apology("must provide password", 400)
        elif len(password) < 8:
            return apology("password needs at least 8 characters", 400)
        if password.isalpha() or password.isnumeric() or password.isalnum():
            return apology("password needs at least 1 letter, number and symbol", 400)
        elif password != confirmation:
            return apology("Passwords don't match", 400)

        # Hash password and add userdata to the database, also set initial activity date to yesterday to avoid conflicts on the first date_check
        hashword = generate_password_hash(password)
        yesterday = db.execute("SELECT DATE(current_day,'-1 days') AS yesterday FROM datecheck")
        initial_date = yesterday[0]['yesterday']
        db.execute("INSERT INTO users (username, hash, last_activity_date) VALUES(?, ?, ?)", username, hashword, initial_date)
        return redirect("/")

    else:
        return render_template("/register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/philosophy")
@login_required
def philosophy():
    """Show philosophy"""
    return render_template("philosophy.html")


@app.route("/forgive", methods=["GET", "POST"])
@login_required
def forgive():
    """Reassure the user"""
    if request.method == "POST":
        return render_template("/forgive.html")

    else:
        return redirect("/")


@app.route("/activate", methods=["GET", "POST"])
@login_required
def activate():
    """Redirect user to add an activity"""
    if request.method == "POST":
        return render_template("/activity.html")

    else:
        return redirect("/")


@app.route("/activity", methods=["GET", "POST"])
@login_required
def activity():
    """Add an activity and keep track of current streak."""
    if request.method == "POST":
        activity = request.form.get("activity")

        db.execute("INSERT INTO activities (user_id, activity) VALUES(?, ?)", session["user_id"], activity)
        db.execute("UPDATE users SET days = days + 1, last_activity_date = CURRENT_DATE WHERE id=?", session["user_id"])

        flash("Activity Registered!")

    return redirect("/")


@app.route("/goals", methods=["GET", "POST"])
@login_required
def goals():
    """Show or alter active goals"""
    if request.method == "POST":
        # Set goal to completed
        if request.form.get("complete"):
            db.execute("UPDATE goals SET status=?, date_completed=CURRENT_DATE WHERE id=?",
                       "completed", request.form.get("complete"))
            flash("Goal Completed!")

        # Delete the selected table row
        elif request.form.get("delete"):
            db.execute("DELETE FROM goals WHERE id=?", request.form.get("delete"))
            flash("Goal Deleted!")

    goals = db.execute("SELECT * FROM goals WHERE user_id=? AND status=?", session["user_id"], "active")
    return render_template("goals.html", goals=goals)


@app.route("/addgoal", methods=["GET", "POST"])
@login_required
def addgoal():
    """Add a goal for the user"""
    if request.method == "POST":
        added_goal = request.form.get("addgoal")
        db.execute("INSERT INTO goals (user_id, goal, status) VALUES(?, ?, ?)", session["user_id"], added_goal, "active")

        flash("Goal added!")

        return redirect("/goals")

    else:
        return redirect("/goals")


@app.route("/progress", methods=["GET", "POST"])
@login_required
def progress():
    """Show progress"""

    if request.method == "POST":
        # Set goal to reactivated
        if request.form.get("reactivate"):
            db.execute("UPDATE goals SET status=?, date_added=CURRENT_DATE WHERE id=?", "active", request.form.get("reactivate"))
            flash("Goal Reactivated!")

        # Delete goal
        if request.form.get("delete"):
            db.execute("DELETE FROM goals WHERE id=?", request.form.get("delete"))
            flash("Goal Deleted!")

    # Adjust personal record if applicable
    user = db.execute("SELECT * FROM users WHERE id=?", session["user_id"])

    if user[0]['days'] > user[0]['record']:
        db.execute("UPDATE users SET record=? WHERE id=?", user[0]['days'], session["user_id"])
        user = db.execute("SELECT * FROM users WHERE id=?", session["user_id"])

    # Display completed goals
    completed_goals = db.execute(
        "SELECT * FROM goals WHERE user_id=? AND status=? ORDER BY date_completed DESC", session["user_id"], "completed")

    activities = db.execute("SELECT * FROM activities WHERE user_id=? ORDER BY date DESC LIMIT 7", session["user_id"])

    return render_template("progress.html", user=user, completed_goals=completed_goals, activities=activities)