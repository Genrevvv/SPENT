from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import check_day, check_month, check_year, error_occured, format_currency, login_required, validate_category, validate_day, validate_month, validate_year


# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["check_day"] = check_day
app.jinja_env.filters["check_month"] = check_month
app.jinja_env.filters["check_year"] = check_year
app.jinja_env.filters["error_occured"] = error_occured
app.jinja_env.filters["format_currency"] = format_currency
app.jinja_env.filters["validate_category"] = validate_category
app.jinja_env.filters["validate_day"] = validate_day
app.jinja_env.filters["validate_month"] = validate_month
app.jinja_env.filters["validate_year"] = validate_year

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
        return error_occured("Invalid currency", 400)
    
    # Set currency
    db.execute("UPDATE users SET currency = ? WHERE id = ?", currency, session["user_id"])

    flash("Welcome to $₱ENT")
    return redirect("/")


@app.route("/add_year", methods=["POST"])
@login_required
def add_year():
    """Add year"""

    # Validate year input
    try:
        year = int(request.form.get("year"))
        validator = validate_year(year) 
        if validator != 0:
            return validator
    except ValueError:
        flash("Invalid year input")
        return redirect("/")

    # Update year in database
    db.execute("INSERT INTO years (user_id, year) VALUES (?, ?)", session["user_id"], year)

    flash("Year added succesfully")
    return redirect("/") 


@app.route("/months", methods=["POST"])
@login_required
def months():
    """Check months in the year"""

    # Check year in db
    try:
        year = int(request.form.get("year"))
        validator = check_year(year)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("year not found", 404)

    """Load months"""
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

    # Check year in db
    try:
        year = int(request.form.get("year"))
        validator = check_year(year)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("year not found", 404)
    
    # Get list of months
    list_of_months= []
    months = db.execute("""SELECT month, monthly_expenses 
                                FROM months
                                JOIN years ON years.id = months.year_id
                                JOIN month_order ON months.month = month_order.month_name
                                WHERE years.user_id = ?
                                AND years.year = ?
                                ORDER BY month_order.month_order""", session["user_id"], year)
    for month_value in months:
        list_of_months.append(month_value)
    
    # Validate month input
    try:
        month = request.form.get("month")
        validator = validate_month(year, month, list_of_months)
        if validator != 0:
            return validator
    except ValueError:
        flash("Invalid month input")
        return render_template("months.html", year=year, months=list_of_months)
    
    # Update month in database
    db.execute("INSERT INTO months (year_id, month) VALUES ((SELECT id FROM years WHERE user_id = ? AND year = ?), ?)", session["user_id"], year, month)

    list_of_months = []
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

    # Check year in db
    try:
        year = int(request.form.get("year"))
        validator = check_year(year)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("year not foud year", 404)

    # check month in db
    try:
        month = request.form.get("month")
        validator = check_month(year, month)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("month not found", 404)
    
    # Create a list of days
    list_of_days = []
    days = db.execute("""SELECT days.day, days.daily_expenses
                        FROM months
                        JOIN days ON  days.month_id = months.id
                        JOIN years ON years.id =  months.year_id
                        WHERE years.user_id = ?
                        AND years.year = ?
                        AND months.month = ?
                        ORDER BY days.day""", session['user_id'], year, month)
    for day_value in days:
        list_of_days.append(day_value)
    
    return render_template("days.html", year=year, month=month, days=list_of_days)


@app.route("/add_day", methods=["POST"])
@login_required
def add_day():
    """Add day"""

    # Check year in db
    try:
        year = int(request.form.get("year"))
        validator = check_year(year)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("year not found", 404)
    
    # check month in db
    try:
        month = request.form.get("month")
        print(f"The month is {month}")
        validator = check_month(year, month)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("month not found", 404)
    
    list_of_days = []
    days = db.execute("""SELECT days.day, days.daily_expenses
                        FROM months
                        JOIN days ON  days.month_id = months.id
                        JOIN years ON years.id =  months.year_id
                        WHERE years.user_id = ?
                        AND years.year = ?
                        AND months.month = ?
                        ORDER BY days.day""", session['user_id'], year, month)
    
    for day_value in days:
        list_of_days.append(day_value)

    # Validate day input
    try:
        day = int(request.form.get("day"))
        validator = validate_day(year, month, day, list_of_days)
        if validator != 0:
            return validator
    except ValueError:
        flash("Invalid day input")
        return render_template("days.html", year=year, month=month, days=list_of_days)
    
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
                        AND months.month = ?
                        ORDER BY days.day""", session['user_id'], year, month)
    
    for day_value in days:
        list_of_days.append(day_value)
    
    return render_template("days.html", year=year, month=month, days=list_of_days)


@app.route("/spent", methods=["POST"])
@login_required
def spent():
    """Check expenses in a day"""

    # Check year in db
    try:
        year = int(request.form.get("year"))
        validator = check_year(year)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("year not found", 404)
    
    # check month in db
    try:
        month = request.form.get("month")
        print(f"The month is {month}")
        validator = check_month(year, month)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("month not found", 404)
    
    # check day in db
    try:
        day = int(request.form.get("day"))
        validator = check_day(year, month, day)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("day not found", 404)

    # Create a list of categories
    list_of_categories = []
    categories = db.execute("""SELECT spent.category, spent.amount 
                                    FROM days
                                    JOIN spent ON spent.day_id = days.id
                                    JOIN months ON months.id = days.month_id
                                    JOIN years ON years.id = months.year_id
                                    WHERE years.user_id = ?
                                    AND years.year = ?
                                    AND months.month = ?
                                    AND days.day = ?
                                    ORDER BY spent.amount DESC;""", session["user_id"], year, month, day)
    
    for category in categories:
        list_of_categories.append(category)

    return render_template("spent.html", year=year, month=month, day=day, categories=list_of_categories)


@app.route("/add_category", methods=["POST"])
@login_required
def add_category():
    # Check year in db
    try:
        year = int(request.form.get("year"))
        validator = check_year(year)
        if validator != 0:
            return validator(year)
    except ValueError:
        return error_occured("year not found", 404)
    
    # check month in db
    try:
        month = request.form.get("month")
        print(f"The month is {month}")
        validator = check_month(year, month)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("month not found", 404)
    
    # check day in db
    try:
        day = int(request.form.get("day"))
        validator = check_day(year, month, day)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("day not found", 404)
    
    # Create a list of categories
    list_of_categories = []
    categories = db.execute("""SELECT spent.category, spent.amount 
                                    FROM spent
                                    JOIN days ON days.id = spent.day_id
                                    JOIN months ON months.id = days.month_id
                                    JOIN years ON years.id = months.year_id
                                    WHERE years.user_id = ?
                                    AND years.year = ?
                                    AND months.month = ?
                                    AND days.day = ?
                                    ORDER BY spent.amount DESC""", session["user_id"], year, month, day)
    for category in categories:
        list_of_categories.append(category)
    
    # Validate amount input
    try:
        amount = request.form.get("amount")
    except ValueError:
        flash("Invalid amount input")
        return render_template("spent.html", year=year, month=month, day=day, categories=list_of_categories)

    # Validate category input
    try:
        category = request.form.get("category")
        validator = validate_category(category)
        if validator != 0:
            flash("Invalid category option")
            return render_template("spent.html", year=year, month=month, day=day, categories=list_of_categories)
    except ValueError:
        flash("Invalid amount input")
        return render_template("spent.html", year=year, month=month, day=day, categories=list_of_categories)

    db.execute("""INSERT INTO spent (day_id, category, amount)
                    VALUES ((SELECT days.id
                                FROM days 
                                JOIN months ON months.id = days.month_id
                                JOIN years ON years.id = months.year_id
                                WHERE years.user_id = ?
                                AND years.year = ?
                                AND months.month = ?
                                AND days.day = ?), ?, ?)""", session["user_id"], year, month, day, category, amount)
    
    # Create a new list of categories (dict)
    list_of_categories.clear()
    categories = db.execute("""SELECT spent.category, spent.amount 
                                    FROM spent
                                    JOIN days ON days.id = spent.day_id
                                    JOIN months ON months.id = days.month_id
                                    JOIN years ON years.id = months.year_id
                                    WHERE years.user_id = ?
                                    AND years.year = ?
                                    AND months.month = ?
                                    AND days.day = ?
                                    ORDER BY spent.amount DESC""", session["user_id"], year, month, day)
    for category in categories:
        list_of_categories.append(category)
        
    print(list_of_categories)

    return render_template("spent.html", year=year, month=month, day=day, categories=list_of_categories)
