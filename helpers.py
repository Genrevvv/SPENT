from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps


# Set SQLite database
db = SQL("sqlite:///spent.db")

# Check month
def check_month(month):
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    if month in months:
        return True
    
    return False


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
