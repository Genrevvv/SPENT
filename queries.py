from cs50 import SQL
from operator import itemgetter

# Set SQLite database
db = SQL("sqlite:///spent.db")


"""This file contains reusable query functions for app.py"""

def get_categories(user_id, year, month, day):
    """Create a list of categories (dict)"""

    return db.execute("""SELECT spent.id AS id, spent.category, spent.amount 
                                    FROM spent
                                    JOIN days ON days.id = spent.day_id
                                    JOIN months ON months.id = days.month_id
                                    JOIN years ON years.id = months.year_id
                                    WHERE years.user_id = :user_id
                                    AND years.year = :year
                                    AND months.month = :month
                                    AND days.day = :day
                                    GROUP BY spent.category
                                    ORDER BY spent.amount DESC""", user_id=user_id, year=year, month=month, day=day)


def get_days(user_id, year, month):
    """Create a list of days (dict)"""

    return  db.execute("""SELECT days.id AS id, days.day AS day, SUM(spent.amount) AS expenses
                            FROM months
                            LEFT JOIN years ON years.id =  months.year_id
                            LEFT JOIN days ON  days.month_id = months.id
                            LEFT JOIN spent ON spent.day_id = days.id
                            WHERE years.user_id = :user_id
                            AND years.year = :year
                            AND months.month = :month
                            GROUP BY days.day
                            ORDER BY days.day""", user_id=user_id, year=year, month=month)


def get_months(user_id, year):
    """Create a list of years (dict)"""

    return db.execute("""SELECT months.id AS id, months.month AS month, SUM(spent.amount) AS expenses
                                FROM months
                                LEFT JOIN years ON years.id = months.year_id
                                LEFT JOIN month_order ON months.month = month_order.month_name
                                LEFT JOIN days ON days.month_id = months.id
                                LEFT JOIN spent ON spent.day_id = days.id
                                WHERE years.user_id = :user_id
                                AND years.year = :year
                                GROUP BY months.month
                                ORDER BY month_order.month_order""", user_id=user_id, year=year)


def get_years(user_id):
    """Create a list of years (dict)"""
    
    return db.execute("""SELECT years.id AS id, years.year AS year, SUM(spent.amount) AS expenses
                                FROM years
                                LEFT JOIN months ON months.year_id = years.id
                                LEFT JOIN days ON days.month_id = months.id
                                LEFT JOIN spent ON spent.day_id = days.id
                                WHERE years.user_id = :user_id
                                GROUP BY years.year
                                ORDER BY years.year DESC
                                """, user_id=user_id) # Idea by chatGPT (LEFT JOIN)


def get_expenses(user_id):
    """Get total expenses"""

    # Create an expenses list of dict
    expenses = []

    categories = ["Bills", "Food", "Transportation", "Healthcare", "Education", "Savings or Investments", "Other"]
    
    for category in categories:
        expense = db.execute("""SELECT SUM(spent.amount) AS expense
                                FROM spent
                                JOIN days ON days.id = spent.day_id
                                JOIN months ON months.id = days.month_id
                                JOIN years ON years.id = months.year_id
                                WHERE years.user_id = :user_id
                                AND spent.category = :category
                                """, user_id=user_id, category=category)
        expense = {'name': category, 'amount': 0 if expense[0]["expense"] == None else expense[0]["expense"]}
        expenses.append(expense)

    # Sort list based on expense amount
    expenses = sorted(expenses, key=itemgetter('amount'), reverse=True) # Assisted by chatGPT
    
    return expenses


def get_total_expenses(user_id):
    total_expenses = db.execute("""SELECT SUM(spent.amount) AS total_expenses
                            FROM spent
                            JOIN days ON days.id = spent.day_id
                            JOIN months ON months.id = days.month_id
                            JOIN years ON years.id = months.year_id
                            WHERE years.user_id = :user_id
                            """, user_id=user_id)
    total_expenses = 0 if total_expenses[0]["total_expenses"] == None else total_expenses[0]["total_expenses"]
    return total_expenses


def delete_user(user_id):
    """Delete user and everything related to them"""

    # Delete row/s of spent related to user
    db.execute("""DELETE FROM spent 
                    WHERE day_id IN (
                        SELECT id FROM days WHERE month_id IN (
                            SELECT id FROM months WHERE year_id IN (
                                SELECT id FROM years WHERE user_id = :user_id)))""", user_id=user_id)
    
    # Delete row/s of days related to user
    db.execute("""DELETE FROM days 
                    WHERE month_id IN (
                        SELECT id FROM months WHERE year_id IN (
                            SELECT id FROM years WHERE user_id = :user_id))""", user_id=user_id)
    
    # Delete row/s of months related to user
    db.execute("""DELETE FROM months 
                    WHERE year_id IN (
                        SELECT id FROM years WHERE user_id = :user_id)""", user_id=user_id)
    
    # Delete row/s of years related to user
    db.execute("DELETE FROM years WHERE user_id = :user_id ", user_id=user_id)

    # Delete user in the db
    db.execute("DELETE FROM users WHERE id = :user_id", user_id=user_id)