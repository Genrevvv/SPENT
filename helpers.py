from calendar import monthrange
from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps

# Set SQLite database
db = SQL("sqlite:///spent.db")

# Check category
def check_category(category):
    categories = ["Bills", "Food", "Transportation", "Healthcare", "Education", "Savings or Investments", "Other"]

    if category in categories:
        return True
    
    return False

# Get the day range of a specific month of a year (Assisted with AI)
def check_day(year, month, day):

    month = convert_month(month)
    
    if month == False:
        return False

    # Determine the number of days in the month
    num_days = monthrange(year, month)[1]

    # Validate day
    if day < 1 or day > num_days:
        return False
    
    return True


# Check month
def check_month(month):
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    if month in months:
        return True
    
    return False


# Coonvert month str to int
def convert_month(month):
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    print(f"month passed: {month}")
    try:
        int_month = months.index(month) + 1
    except ValueError:
        print("bruh")
        return False
    
    print(int_month)
    return int_month

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


def format_currency(value):
    # Check for user's currency
    currency = db.execute("SELECT currency FROM users WHERE id = ?", session["user_id"])
    currency = currency[0]["currency"] 
    
    # Format currency
    if currency == "usd":
        return f"${value:,.2f}"
    elif currency == "php":
        return f"₱{value:,.2f}"
