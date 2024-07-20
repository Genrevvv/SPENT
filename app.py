from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

# Custom auxiliary functions
from helpers import check_day, check_month, check_year, error_occured, format_currency, login_required, reset_flash, validate_category, validate_day, validate_month, validate_year

# Custom reusable query functions
from queries import delete_user, get_categories, get_days, get_months, get_years, get_expenses, get_total_expenses

# Configure application
app = Flask(__name__)

# Custom filter from helpers
app.jinja_env.filters["format_currency"] = format_currency


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
    
    # Create a list of years (dict)
    years = get_years(session["user_id"])

    total_expenses= get_total_expenses(session["user_id"]) # Get total expenses
    expenses = get_expenses(session["user_id"]) # Get expenses
    
    return render_template("index.html", years=years, total_expenses=total_expenses, expenses=expenses)

    
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
        session["username"] = request.form.get("username")

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
        session["username"] = request.form.get("username")


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

    return redirect("/") 


@app.route("/months", methods=["GET"])
@login_required
def months():
    """Check months in the year"""

    # Check year in db
    try:
        year = int(request.args.get("year"))
        validator = check_year(year)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("year not found", 404)

    """Load months"""
    months = get_months(session["user_id"], year)

    total_expenses= get_total_expenses(session["user_id"]) # Get total expenses
    expenses = get_expenses(session["user_id"]) # Get expenses

    reset_flash()

    return render_template("months.html", year=year, months=months, total_expenses=total_expenses, expenses=expenses)


@app.route("/add_month", methods=["POST"])
@login_required
def add_month():
    """Add month"""

    total_expenses= get_total_expenses(session["user_id"]) # Get total expenses
    expenses = get_expenses(session["user_id"]) # Get expenses

    # Check year in db
    try:
        year = int(request.form.get("year"))
        validator = check_year(year)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("year not found", 404)
    
    # Create a list of years (dict)
    months = get_months(session["user_id"], year)
    
    # Validate month input
    try:
        month = request.form.get("month")
        validator = validate_month(year, month, months)
        if validator != 0:
            return validator
    except ValueError:
        flash("Invalid month input")
        return render_template("months.html", year=year, months=months, total_expenses=total_expenses, expenses=expenses)
    
    # Update month in database
    db.execute("INSERT INTO months (year_id, month) VALUES ((SELECT id FROM years WHERE user_id = ? AND year = ?), ?)", session["user_id"], year, month)

    # Get the updated list of months (dict)
    months = get_months(session["user_id"], year)

    return render_template("months.html", year=year, months=months, total_expenses=total_expenses, expenses=expenses)


@app.route("/days", methods=["GET"])
@login_required
def days():
    """Check days in the month"""

    # Check year in db
    try:
        year = int(request.args.get("year"))
        validator = check_year(year)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("year not foud year", 404)

    # Check month in db
    try:
        month = request.args.get("month")
        validator = check_month(year, month)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("month not found", 404)
    
    # Create a list of days (dict)
    days = get_days(session["user_id"], year, month)

    total_expenses= get_total_expenses(session["user_id"]) # Get total expenses
    expenses = get_expenses(session["user_id"]) # Get expenses
    
    reset_flash()

    return render_template("days.html", year=year, month=month, days=days, total_expenses=total_expenses, expenses=expenses)


@app.route("/add_day", methods=["POST"])
@login_required
def add_day():
    """Add day"""

    total_expenses= get_total_expenses(session["user_id"]) # Get total expenses
    expenses = get_expenses(session["user_id"]) # Get expenses

    # Check year in db
    try:
        year = int(request.form.get("year"))
        validator = check_year(year)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("year not found", 404)
    
    # Check month in db
    try:
        month = request.form.get("month")
        validator = check_month(year, month)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("month not found", 404)
    
    # Create a list of days (dict)
    days = get_days(session["user_id"], year, month)

    # Validate day input
    try:
        day = int(request.form.get("day"))
        validator = validate_day(year, month, day, days)
        if validator != 0:
            return validator
    except ValueError:
        flash("Invalid day input")
        return render_template("days.html", year=year, month=month, days=days, total_expenses=total_expenses, expenses=expenses)
    
    # Update day in the database
    db.execute("""INSERT INTO days (month_id, day) 
                  VALUES ((SELECT id FROM months WHERE year_id = (
                        SELECT id FROM years WHERE user_id = ? AND year = ?) AND month = ?), ?)""", session["user_id"], year, month, day)
    
    # Get the updated list of days (dict)
    days = get_days(session["user_id"], year, month)
    
    return render_template("days.html", year=year, month=month, days=days, total_expenses=total_expenses, expenses=expenses)


@app.route("/spent", methods=["GET"])
@login_required
def spent():
    """Check expenses in a day"""

    # Check year in db
    try:
        year = int(request.args.get("year"))
        validator = check_year(year)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("year not found", 404)
    
    # check month in db
    try:
        month = request.args.get("month")
        validator = check_month(year, month)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("month not found", 404)
    
    # check day in db
    try:
        day = int(request.args.get("day"))
        validator = check_day(year, month, day)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("day not found", 404)

    # Create a list of categories (dict)
    categories = get_categories(session["user_id"], year, month, day)

    total_expenses= get_total_expenses(session["user_id"]) # Get total expenses
    expenses = get_expenses(session["user_id"]) # Get expenses

    reset_flash()

    return render_template("spent.html", year=year, month=month, day=day, categories=categories, total_expenses=total_expenses, expenses=expenses)


@app.route("/add_category", methods=["POST"])
@login_required
def add_category():
    """Add category"""

    total_expenses= get_total_expenses(session["user_id"]) # Get total expenses
    expenses = get_expenses(session["user_id"]) # Get expenses

    # Check year in db
    try:
        year = int(request.form.get("year"))
        validator = check_year(year)
        if validator != 0:
            return validator(year)
    except ValueError:
        return error_occured("year not found", 404)
    
    # Check month in db
    try:
        month = request.form.get("month")
        validator = check_month(year, month)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("month not found", 404)
    
    # Check day in db
    try:
        day = int(request.form.get("day"))
        validator = check_day(year, month, day)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("day not found", 404)
    
    # Create a list of categories (dict)
    categories = get_categories(session["user_id"], year, month, day)
    
    # Validate amount input
    try:
        amount = float(request.form.get("amount"))
        if amount < 1:
            flash("Invalid amount input")
            return render_template("spent.html", year=year, month=month, day=day, categories=categories, total_expenses=total_expenses, expenses=expenses)
    except ValueError:
        flash("Invalid amount input")
        return render_template("spent.html", year=year, month=month, day=day, categories=categories, total_expenses=total_expenses, expenses=expenses)

    # Validate category input
    try:
        category = request.form.get("category")
        validator = validate_category(year, month, day, category, categories)
        if validator != 0:
            return validator
    except ValueError:
        flash("Invalid amount input")
        return render_template("spent.html", year=year, month=month, day=day, categories=categories, total_expenses=total_expenses, expenses=expenses)

    db.execute("""INSERT INTO spent (day_id, category, amount)
                    VALUES ((SELECT days.id
                                FROM days 
                                JOIN months ON months.id = days.month_id
                                JOIN years ON years.id = months.year_id
                                WHERE years.user_id = ?
                                AND years.year = ?
                                AND months.month = ?
                                AND days.day = ?), ?, ?)""", session["user_id"], year, month, day, category, amount)
    
    # Get the updated list of categories (dict)
    categories = get_categories(session["user_id"], year, month, day)

    total_expenses= get_total_expenses(session["user_id"]) # Get total expenses
    expenses = get_expenses(session["user_id"]) # Get expenses
    
    return render_template("spent.html", year=year, month=month, day=day, categories=categories, total_expenses=total_expenses, expenses=expenses)


@app.route("/delete_year", methods=["POST"])
@login_required
def delete_year():
    # Validate id
    try:
        year_id = int(request.form.get("year_id"))
    except ValueError:
        return error_occured("Invalid year id", 400)

    # Delete year and everything related to it
    db.execute("DELETE FROM spent WHERE day_id IN (SELECT id FROM days WHERE month_id IN (SELECT id FROM months WHERE year_id = :year_id))", year_id=year_id)
    db.execute("DELETE FROM days WHERE month_id IN (SELECT id FROM months WHERE year_id = :year_id)", year_id=year_id)
    db.execute("DELETE FROM months WHERE year_id = :year_id", year_id=year_id)
    db.execute("DELETE FROM years WHERE id = :year_id", year_id=year_id)

    reset_flash()

    return redirect("/")


@app.route("/delete_month", methods=["POST"])
@login_required
def delete_month():

    # Check year in db
    try:
        year = int(request.form.get("year"))
        validator = check_year(year)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("year not found", 404)
    
    # Validate id
    try:
        month_id = int(request.form.get("month_id"))
    except ValueError:
        return error_occured("Invalid month id", 400)

    # Delete month and everything related to it
    db.execute("DELETE FROM spent WHERE day_id IN (SELECT id FROM days WHERE month_id = :month_id)", month_id=month_id)
    db.execute("DELETE FROM days WHERE month_id = :month_id", month_id=month_id)
    db.execute("DELETE FROM months WHERE id = :month_id", month_id=month_id)

    # Get the updated list of months (dict)
    months = get_months(session["user_id"], year)

    total_expenses= get_total_expenses(session["user_id"]) # Get total expenses
    expenses = get_expenses(session["user_id"]) # Get expenses

    reset_flash()

    return render_template("months.html", year=year, months=months, total_expenses=total_expenses, expenses=expenses)


@app.route("/delete_day", methods=["POST"])
@login_required
def delete_day():
    # Validate id
    try:
        day_id = int(request.form.get("day_id"))
    except ValueError:
        return error_occured("Invalid day id", 400)
    
    # Check year in db
    try:
        year = int(request.form.get("year"))
        validator = check_year(year)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("year not foud year", 404)

    # Check month in db
    try:
        month = request.form.get("month")
        validator = check_month(year, month)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("month not found", 404)

    # Delete day and everything related to it
    db.execute("DELETE FROM spent WHERE day_id = :day_id", day_id=day_id)
    db.execute("DELETE FROM days WHERE id = :day_id", day_id=day_id)

    # Get the updated list of days (dict)
    days = get_days(session["user_id"], year, month)
    
    total_expenses= get_total_expenses(session["user_id"]) # Get total expenses
    expenses = get_expenses(session["user_id"]) # Get expenses

    reset_flash()

    return render_template("days.html", year=year, month=month, days=days, total_expenses=total_expenses, expenses=expenses)


@app.route("/delete_category", methods=["POST"])
@login_required
def delete_category():
    # Validate id
    try:
        spent_id = int(request.form.get("spent_id"))
    except ValueError:
        return error_occured("Invalid category id", 400)
    
    # Check year in db
    try:
        year = int(request.form.get("year"))
        validator = check_year(year)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("year not foud year", 404)

    # Check month in db
    try:
        month = request.form.get("month")
        validator = check_month(year, month)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("month not found", 404)
    
    # Check day in db
    try:
        day = int(request.form.get("day"))
        validator = check_day(year, month, day)
        if validator != 0:
            return validator
    except ValueError:
        return error_occured("day not found", 404)

    # Delete day and everything related to it
    db.execute("DELETE FROM spent WHERE id = :spent_id", spent_id=spent_id)

    # Get the updated list of categories (dict)
    categories = get_categories(session["user_id"], year, month, day)

    total_expenses= get_total_expenses(session["user_id"]) # Get total expenses
    expenses = get_expenses(session["user_id"]) # Get expenses

    reset_flash()

    return render_template("spent.html", year=year, month=month, day=day, categories=categories, total_expenses=total_expenses, expenses=expenses)


@app.route("/save", methods=["POST"])
@login_required
def save():
    # ChatGPT's idea

    # Get the data from the request
    data = request.json  # Parse data

    # Validate data
    try:
        year = int(data.get('year'))
        validator = check_year(year)
        if validator != 0:
            return jsonify({"error": "Invalid year"}), 400
    except ValueError:
        return jsonify({"error": "Year not found"}), 404
    
    try:
        month = data.get('month')
        validator = check_month(year, month)
        if validator != 0:
            return jsonify({"error": "Invalid month"}), 400
    except ValueError:
        return jsonify({"error": "Month not found"}), 404
    
    try:
        day = int(data.get('day'))
        validator = check_day(year, month, day)
        if validator != 0:
            return jsonify({"error": "Invalid day"}), 400
    except ValueError:
        return jsonify({"error": "Day not found"}), 404
    
    try:
        amount = float(data.get('amount'))
        if amount < 1:
            return jsonify({"error": "Invalid amount input"}), 400
    except ValueError:
        return jsonify({"error": "Invalid amount input"}), 400
    
    try:
        id = int(data.get('id'))
    except ValueError:
        return jsonify({"error": "Invalid category id"}), 400

    # Update amount of a category with that 'id' in the db
    db.execute("UPDATE spent SET amount = :amount WHERE id = :id", amount=amount, id=id)
    
    categories = get_categories(session["user_id"], year, month, day)
    total_expenses = get_total_expenses(session["user_id"])  # Get total expenses
    expenses = get_expenses(session["user_id"])  # Get expenses

    reset_flash()

    # Return JSON response with updated data
    return jsonify({
        "success": True,
        "categories": categories,
        "total_expenses": total_expenses,
        "expenses": expenses
    })

@app.route('/account', methods=["GET"])
@login_required
def account():

    total_expenses = get_total_expenses(session["user_id"])  # Get total expenses
    expenses = get_expenses(session["user_id"])  # Get expenses

    reset_flash()
    return render_template("account.html", username=session["username"], total_expenses=total_expenses, expenses=expenses)


@app.route('/change_username', methods=["GET", "POST"])
@login_required
def change_username():
    if request.method == "POST":
        old_username = request.form.get("old_username")
        new_username = request.form.get("new_username")

        # Validate user input

        if not old_username or not new_username:
            flash("Please input a valid username")
            return render_template("change-username.html")
        elif old_username != session["username"]:
            flash("Incorrect old username")
            return render_template("change-username.html")
        
        # Update username
        try:
            db.execute("UPDATE users SET username = :new_username WHERE username = :old_username", new_username=new_username, old_username=old_username)
        except ValueError:
            flash("Username already taken")
            return render_template("change-username.html")
        
        total_expenses = get_total_expenses(session["user_id"])  # Get total expenses
        expenses = get_expenses(session["user_id"])  # Get expenses

        # Update session
        session["username"] = new_username

        flash("Succesfully changed username")
        return render_template("account.html", username=session["username"], total_expenses=total_expenses, expenses=expenses)
         
    else:
        return render_template("change-username.html")
    

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == "POST":
        current_password = db.execute("SELECT pass_hash FROM users WHERE id = ?", session["user_id"])

        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")

        # Validate old password
        if not old_password or not new_password:
            flash("Incorrect old pasword")
            return render_template("change-password.html")
        elif not check_password_hash(current_password[0]["pass_hash"], old_password):
            flash("Incorrect old password")
            return render_template("change-password.html")

        new_password = generate_password_hash(new_password)

        # Update password
        db.execute("UPDATE users SET pass_hash = :new_password", new_password=new_password)

        total_expenses = get_total_expenses(session["user_id"])  # Get total expenses
        expenses = get_expenses(session["user_id"])  # Get expenses

        flash("Succesfully changed password")
        return render_template("account.html", username=session["username"], total_expenses=total_expenses, expenses=expenses)
    else:
        return render_template("change-password.html")


@app.route("/delete_account", methods=["GET", "POST"])
@login_required
def delete_account():
    if request.method == "POST":
        delete_user(session["user_id"])

        session.clear()

        return render_template("farewell.html")

    else:
        return render_template("delete-account.html")
    