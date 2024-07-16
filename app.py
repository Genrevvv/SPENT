from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import check_day, check_month, login_required, format_currency


# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["format_currency"] = format_currency
app.jinja_env.filters["check_month"] = check_month
app.jinja_env.filters["check_day"] = check_day

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

    # Check for user's currency
    currency = db.execute("SELECT currency FROM users WHERE id = ?", session["user_id"])
    currency = currency[0]["currency"]

    if currency not in ["usd", "php"]:
        return render_template("set-currency.html")
    
    # Create a list of years
    list_of_years = []
    years = db.execute("SELECT year, annual_expenses FROM years WHERE user_id = ? ORDER BY year DESC", session["user_id"])
    for year in years:
        list_of_years.append(year)
    
    return render_template("index.html", years=list_of_years)


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
    

@app.route("/setcurrency", methods=["POST"])
@login_required
def setcurrency():
    """Set user's currency"""

    currency = request.form.get("currency")

    # Validate user response
    if currency not in ["usd", "php"]:
        flash("Invalid currency")
        return render_template("/")
    
    # Set currency
    db.execute("UPDATE users SET currency = ? WHERE id = ?", currency, session["user_id"])

    flash("Welcome to $₱ENT")
    return redirect("/")


@app.route("/add_year", methods=["POST"])
@login_required
def add_year():
    """Add year"""

    # Validate year
    try:
        year = int(request.form.get("year"))
        if year < 1582 or year > datetime.now().year:
            flash(f"Year must be between 1582 and {datetime.now().year}, inclusive.")
            return redirect("/")
    except ValueError:
        flash("Invalid year input")
        return redirect("/")
    
    # Check if year for the user already exist
    years = db.execute("SELECT year FROM years WHERE user_id = ? ORDER BY year DESC", session["user_id"])
    for year_value in years:
        if year_value["year"] == year:
            flash("Year already exist")
            return redirect("/")
    
    # Update year in database
    db.execute("INSERT INTO years (user_id, year) VALUES (?, ?)", session["user_id"], year)

    flash("Year added succesfully")
    return redirect("/") 


@app.route("/months", methods=["POST"])
@login_required
def months():
    """Check months in the year"""

    # Validate year
    year = int(request.form.get("year"))
    years = db.execute("SELECT year FROM years WHERE user_id = ? ORDER BY year DESC", session["user_id"])

    # Check if year exist
    for year_value in years:
        if year_value["year"] == year:
            break
    else:
        flash("Invalid year")
        return redirect("/")

    # Create a list of years
    list_of_months = []
    months = db.execute("""SELECT month, monthly_expenses 
                                FROM months
                                JOIN years ON years.id = months.year_id
                                JOIN month_order ON months.month = month_order.month_name
                                WHERE years.user_id = ?
                                AND years.year = ?
                                ORDER BY month_order.month_order""", session["user_id"], year)
    
    for month in months:
        list_of_months.append(month)

    return render_template("months.html", year=year, months=list_of_months)


@app.route("/add_month", methods=["POST"])
@login_required
def add_month():
    """Add month"""

    year = int(request.form.get("year"))

    list_of_months= []
    months = db.execute("""SELECT month, monthly_expenses 
                                FROM months
                                JOIN years ON years.id = months.year_id
                                JOIN month_order ON months.month = month_order.month_name
                                WHERE years.user_id = ?
                                AND years.year = ?
                                ORDER BY month_order.month_order""", session["user_id"], year)
    
    # Validate month
    try:
        month = request.form.get("month")
        month_exist = False
        for month_value in months:
            list_of_months.append(month_value)
            if month_value["month"] == month:
                month_exist = True
        if not month or check_month(month) == False:
            flash("Invalid month input")
            return render_template("months.html", year=year, months=list_of_months)

    except ValueError:
            flash(f"Invalid month input")
            return render_template("months.html", year=year, months=list_of_months)

    # Check if month of the year of the user already exist
    if month_exist:
        flash("Month already exist")
        return render_template("months.html", year=year, months=list_of_months)
    
    # Update month in database
    db.execute("INSERT INTO months (year_id, month) VALUES ((SELECT id FROM years WHERE user_id = ? AND year = ?), ?)", session["user_id"], year, month)

    months = db.execute("""SELECT month, monthly_expenses 
                                FROM months
                                JOIN years ON years.id = months.year_id
                                JOIN month_order ON months.month = month_order.month_name
                                WHERE years.user_id = ?
                                AND years.year = ?
                                ORDER BY month_order.month_order""", session["user_id"], year)
    
    # Create a new list of months (dict)
    list_of_months.clear()
    for month_value in months:
        list_of_months.append(month_value)

    return render_template("months.html", year=year, months=list_of_months)


@app.route("/days", methods=["POST"])
@login_required
def days():
    """Check days in the month"""

    year = int(request.form.get("year"))

    # Validate month
    month = request.form.get("month")
    months = db.execute("""SELECT month, monthly_expenses 
                                FROM months
                                JOIN years ON years.id = months.year_id
                                JOIN month_order ON months.month = month_order.month_name
                                WHERE years.user_id = ?
                                AND years.year = ?
                                ORDER BY month_order.month_order""", session["user_id"], year)
    
    # Check if month exist
    for month_value in months:
        if month_value["month"] == month:
            break
    else:
        return render_template("error.html", error="month not found")
    
    # Create a list of days
    list_of_days = []
    days = db.execute("""SELECT days.day, days.daily_expenses
                            FROM months
                            JOIN days ON  days.month_id = months.id
                            JOIN years ON years.id =  months.year_id
                            WHERE years.user_id = ?
                            AND years.year = ?
                            ORDER BY days.day""", session['user_id'], year)
    for day_value in days:
        list_of_days.append(day_value)

    print(f"list of days = {list_of_days}")
    
    # Create a list of years
    return render_template("days.html", year=year, month=month, days=list_of_days)


@app.route("/add_day", methods=["POST"])
@login_required
def add_day():
    """Add day"""

    month = request.form.get("month")
    year = int(request.form.get("year"))

    list_of_days = []
    days = db.execute("""SELECT days.day, days.daily_expenses
                            FROM months
                            JOIN days ON  days.month_id = months.id
                            JOIN years ON years.id =  months.year_id
                            WHERE years.user_id = ?
                            AND years.year = ?
                            ORDER BY days.day""", session['user_id'], year)
    # Validate day
    try:
        day = int(request.form.get("day"))
        day_exist = False
        for day_value in days:
            list_of_days.append(day_value)
            if day_value["day"] == day:
                day_exist = True
        if not check_day(year, month, day):
            flash("Invalid day input")
            return render_template("days.html", year=year, months=list_of_days)
    except ValueError:
        flash(f"Invalid day input")
        return render_template("days.html", year=year, month=month, days=list_of_days)

    # Check if day already exist
    if day_exist:
        flash("Day already exist")
        return render_template("days.html", year=year,month=month, days=list_of_days)
    
    # Update day in the database
    db.execute("""INSERT INTO days (month_id, day) 
                    VALUES ((SELECT id FROM months WHERE year_id = (
                        SELECT id FROM years WHERE user_id = ? AND year = ?) AND month = ?), ?)""", session["user_id"], year, month, day)
    
    # Create a new list of days (dict)
    list_of_days.clear()
    days = db.execute("""SELECT days.day, days.daily_expenses
                        FROM months
                        JOIN days ON  days.month_id = months.id
                        JOIN years ON years.id =  months.year_id
                        WHERE years.user_id = ?
                        AND years.year = ?
                        ORDER BY days.day""", session['user_id'], year)
    
    for day_value in days:
        list_of_days.append(day_value)
    
    return render_template("days.html", year=year, month=month, days=list_of_days)