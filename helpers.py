from calendar import monthrange
from cs50 import SQL
from datetime import datetime
from flask import flash, redirect, render_template, request, session
from functools import wraps

# Custom reusable query functions
from queries import get_categories, get_days, get_months, get_years, get_expenses, get_total_expenses

# Set SQLite database
db = SQL("sqlite:///spent.db")

# check if day exist
def check_day(year, month, day):
    days = db.execute("""SELECT days.day
                        FROM months
                        JOIN days ON  days.month_id = months.id
                        JOIN years ON years.id =  months.year_id
                        WHERE years.user_id = ?
                        AND years.year = ?
                        AND months.month = ?
                        ORDER BY days.day""", session['user_id'], year, month)
    
    for day_value in days:
        if day_value["day"] == day:
            break
    else:
        return error_occured("day not found", 404)

    return 0


# Check month value
def check_month_value(month):
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    if month in months:
        return True
    
    return False


# Check if month exist
def check_month(year, month):
    months = db.execute("""SELECT month 
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
        return error_occured("month not found", 404)
    
    return 0


# Check if year exist
def check_year(year):
    years = db.execute("SELECT year FROM years WHERE user_id = ? ORDER BY year DESC", session["user_id"])

    # Check if year exist
    for year_value in years:
        if year_value["year"] == year:
            break
    else:
        flash("Invalid year")
        return redirect("/")
    
    return 0


# Coonvert month str to int
def convert_month(month):
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    print(f"month passed: {month}")
    try:
        int_month = months.index(month) + 1
    except ValueError:
        print("bruh")
        return False
    
    return int_month


def error_occured(error_message, status_code):
    return render_template("error.html", error=error_message, code=status_code)

def format_currency(value):
    # Check for user's currency
    currency = db.execute("SELECT currency FROM users WHERE id = ?", session["user_id"])
    currency = currency[0]["currency"] 
    
    # Format currency
    if currency == "usd":
        return f"${value:,.2f}"
    elif currency == "php":
        return f"₱{value:,.2f}"
    

# Confirm login (from finance pset)
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def reset_flash():
    # Remove previous flash message rendered to the page
    if '_flashes' in session:
        session.pop('_flashes', None)

# Validate category
def validate_category(year, month, day, category, categories):

    total_expenses= get_total_expenses(session["user_id"]) # Get total expenses
    expenses = get_expenses(session["user_id"]) # Get expenses

    category_values = ["Bills", "Food", "Transportation", "Healthcare", "Education", "Savings or Investments", "Other"]

    for category_value in category_values:
        if category_value == category:
            break
    else:
        return error_occured("Invalid category option", 400)
    
    # Check if category already exists
    for category_value in categories:
        if category_value["category"] == category:
                flash("Category already exist")
                return render_template("spent.html", year=year, month=month, day=day, categories=categories, total_expenses=total_expenses, expenses=expenses)
    
    return 0


# Validate day input
def validate_day(year, month, day, days):

    total_expenses= get_total_expenses(session["user_id"]) # Get total expenses
    expenses = get_expenses(session["user_id"]) # Get expenses

    if not validate_day_range(year, month, day):
        flash("Invalid day input")
        return render_template("days.html", year=year, month=month, days=days, total_expenses=total_expenses, expenses=expenses)
    
    day_exist = False

    for day_value in days:
        if day_value["day"] == day:
            day_exist = True

    # Check if day already exist
    if day_exist:
        flash("Day already exist")
        return render_template("days.html", year=year,month=month, days=days, total_expenses=total_expenses, expenses=expenses)

    return 0


# Get the day range of a specific month of a year (Assisted with chatGPT)
def validate_day_range(year, month, day):
    month = convert_month(month)
    
    if month == False:
        return False

    # Determine the number of days in the month
    num_days = monthrange(year, month)[1]

    # Validate day
    if day < 1 or day > num_days:
        return False
    
    return True


# Validate month input
def validate_month(year, month, months):
    total_expenses= get_total_expenses(session["user_id"]) # Get total expenses
    expenses = get_expenses(session["user_id"]) # Get expenses

    # Validate input
    if not month or not check_month_value(month):
        flash("Invalid month input")
        return render_template("months.html", year=year, months=months, total_expenses=total_expenses, expenses=expenses)

    # Check if month of the year of the user already exist
    for month_value in months:
        if month_value["month"] == month:
            flash("Month already exist")
            return render_template("months.html", year=year, months=months, total_expenses=total_expenses, expenses=expenses)

    return 0

# Valdidate year input
def validate_year(year):
    if year < 1582 or year > datetime.now().year:
        flash(f"Year must be between 1582 and {datetime.now().year}, inclusive.")
        return redirect("/")

    # Check if year for the user already exist
    years = db.execute("SELECT year FROM years WHERE user_id = ? ORDER BY year DESC", session["user_id"])
    for year_value in years:
        if year_value["year"] == year:
            flash("Year already exist")
            return redirect("/")
        
    return 0