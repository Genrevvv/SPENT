from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set SQLite database
db = SQL("sqlite:///spent.db")


# Disable caching for responses (code from finance pset)
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
    return render_template("index.html")


# Login user (references finance pset)
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""    

    # Forgot any user_id
    session.clear()

    if request.method == "POST":

        # Ensure user inputted something
        if not request.form.get("username"):
            flash("Please input a username")
            return render_template("login.html")
        
        elif not request.form.get("password"):
            flash("Please input a password")
            return render_template("login.html")
        
        # Check if user exists in the database
        user = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(user) != 1 or not check_password_hash(user[0]["pass_hash"], request.form.get("password")):
            flash("Invalid username and/or password")
            return render_template("login.html")
        
        # Remember which user has logged in
        session["user_id"] = user[0]["id"]

        # Redierect to home page
        return redirect("/")
    
    else:
        # Return a login form to the user
        return render_template("login.html")
    

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Validate user input
        if not request.form.get("username"):
            flash("Please input a username")
            return render_template("register.html")
        
        elif not request.form.get("password"):
            flash("Please input a password")
            return render_template("register.html")
        
        elif request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords do not match")
            return render_template("register.html")
        
        username = request.form.get("username")
        hashed_pass =generate_password_hash(request.form.get("password"))

        try:
            # Add user to the database
            db.execute("INSERT INTO users (username, pass_hash) VALUES (?, ?)", username, hashed_pass)
        except ValueError:
            flash("Username already taken")
            return render_template("register.html")

        """Log user in"""
        # Check if user exists in the database
        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(user) != 1 or not check_password_hash(user[0]["pass_hash"], request.form.get("password")):
            flash("Invalid username and/or password")
            return render_template("login.html")
        
        # Remember which user has logged in
        session["user_id"] = user[0]["id"]

        # Redierect to home page
        return redirect("/")
    
    else:
        # Return a register form to the user
        return render_template("register.html")

