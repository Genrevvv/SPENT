# _$₱ENT_
### Video Demo: [CS50x: Final Project - $₱ENT](https://youtu.be/6MlDo6Rgn8s)
### Description:

_$₱ENT_ is a website designed to help us keep track of and manage our expenses over the past and present years, months, and days. The main functionality of the website is created using Python, Jinja, and Flask, which handle the server-side operations. For the front end, HTML, CSS, and JavaScript are used to build the user interface.

## Files
- **`templates/`**: Contains HTML files used to render the program. There are 15 HTML files created for the program, including `layout.html`, which is the template for all the other HTML files. Additionally, there's a `sidebar.html` included in `templates`, this file is a reused sidebar for multiple pages of the website.

- **`static/`**: Contains the CSS file I created to personalize the website. This folder also contains the JS file that provides functionality for closing a flash message and editing the category table. Lastly, this folder has an image of a sad cat that is used on the `farewell.html` page when users delete their account.
    - **`main.js`**: This JS file contains the functionality for the 'x' icon of the flash message. Moreover, this file also has the edit and save functions for the `spent.html` page for the category table.
        - **`remove flash message`**: Function for removing a flash message on the page by clicking the 'x' icon in the upper right corner of the container.
        - **`edit()`**: Changes the inner HTML of a `<td>` into an input box with 'check' and 'x' icons, to save and discard changes.
            - **`x-icon`**: Listens for the 'click' event and reloads the page without saving any changes.
            - **`check-icon`**: Listens for the 'click' event and calls the `save()` function.
        - **`save()`**: Takes the data from the `check-icon` and fetches the `/save` route to save the changes.
    - **`style.css`**: This CSS file stores all the designs for the visualization and aesthetics of the website. For this project, I decided not to use CSS frameworks like Bootstrap because I wanted to learn about CSS and design my website myself.
    - **`sad-cat.png`**: A PNG image of a popular sad cat meme, retrieved from Pinterest.

- **`app.py`**: The main application file that defines multiple routes for the program. This file makes most of the functionality of the website. This `app.py` is the core file of the _$₱ENT_ website.
    - **`/`**: Home page
    - **`/login`**: Login page
    - **`/logout`**: Logout
    - **`/register`**: Registration page
    - **`/set_currency`**: Set user's currency
    - **`/add_year`**: Add year
    - **`/months`**: View months in a year
    - **`/add_month`**: Add month
    - **`/days`**: View days in a month
    - **`/add_day`**: Add day
    - **`/spent`**: View expenses in a day
    - **`/add_category`**: Add category (expense)
    - **`/delete_year`**: Delete year and all of its related child rows.
    - **`/delete_month`**: Delete month and all of its related child rows.
    - **`/delete_day`**: Delete day and all of its related child rows.
    - **`/delete_category`**: Delete row of spent
    - **`/save`**: Receives data from the `save()` function and updates the database.
    - **`/account`**: Account page
    - **`/change_username`**: Change username
    - **`/change_password`**: Change password
    - **`/delete_account`**: Delete user and all of their related child rows.

- **`helpers.py`**: Includes custom-made utility functions that are useful to the main application. These functions help to lessen the amount of code in the main function.
    - **`check_day()`**: Check if the day exists in the database
    - **`check_month_value()`**: Check if the input is a valid month
    - **`check_month()`**: Check if the month exists in the database
    - **`check_year()`**: Check if the year exists in the database
    - **`error_occurred()`**: Accepts an error message and status code, displays error in `error.html` page.
    - **`format_currency()`**: Formats user's input in the table for their currency of choice.
    - **`login_required()`**: Ensures that users are logged in to an account when using the website.
    - **`reset_flash()`**: Remove previous flash message rendered to the page.
    - **`validate_category()`**: Ensures that users input a valid category
    - **`validate_day()`**: Ensures that users input a valid day.
    - **`validate_day_range()`**: Ensures that the day input exists for that month of a year.
    - **`validate_month()`**: Ensures that users input a valid month.
    - **`validate_year()`**: Ensures that users input a valid year (1582 < year <= current year).

- **`queries.py`**: Includes reusable query functions that are used in the main application. These functions query a list of dictionaries from the database, which are used in rendering a page on the website.
    - **`get_categories()`**: Queries the rows of category and amount (spent) for a specific day, month, year, and user.
    - **`get_days()`**: Queries the rows of days for a specific month, year, and user.
    - **`get_months()`**: Queries the rows of months for a specific year and user.
    - **`get_years()`**: Queries the rows of years for a specific user.
    - **`get_expenses()`**: Queries the rows for each category and its total amount per category.
    - **`get_total_expenses()`**: Queries the total amount of expenses for a user.

- **`spent.db`**: The database that stores the data for the users. This file stores the users, username, years, months, month_order, days, and spent tables.
    - **`users`**: Table that stores users and their information such as their username, pass_hash, and currency.
    - **`username`**: Creates a unique index for each user's username.
    - **`years`**: Stores data for years, references user_id.
    - **`months`**: Stores data for months, references year_id.
    - **`month_order`**: Used as a basis for ordering months.
    - **`days`**: Stores data for days, references month_id.
    - **`spent`**: Stores data for users' expenses, including category and amount, references day_id.

- **`README.md`**: A file that describes and explains the functionality of the program.

- **`requirements.txt`**: Provides information about the tools used.
