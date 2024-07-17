-- Create a spent table in the spent database
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    pass_hash TEXT NOT NULL,
    currency TEXT
);

CREATE UNIQUE INDEX username ON users (username);

CREATE TABLE years (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id INTEGER NOT NULL,
    year NOT NULL,
    annual_expenses NUMERIC NOT NULL DEFAULT 0.00,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE months (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    year_id TEXT NOT NULL,
    month TEXT NOT NULL,
    monthly_expenses NUMERIC NOT NULL DEFAULT 0.00,
    FOREIGN KEY (year_id) REFERENCES years (id)
);

CREATE TABLE month_order (
    month_name TEXT PRIMARY KEY NOT NULL,
    month_order INTEGER NOT NULL
);

INSERT INTO month_order (month_name, month_order)
VALUES 
    ('January', 1),
    ('February', 2),
    ('March', 3),
    ('April', 4),
    ('May', 5),
    ('June', 6),
    ('July', 7),
    ('August', 8),
    ('September', 9),
    ('October', 10),
    ('November', 11),
    ('December', 12);

CREATE TABLE days (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    month_id INTEGER NOT NULL,
    day INTEGER NOT NULL,
    daily_expenses NUMERIC NOT NULL DEFAULT 0.00,
    FOREIGN KEY (month_id) REFERENCES months (id)
);

"""Not yet added"""
CREATE TABLE dates (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    year_id INTEGER NOT NULL,
    month INTEGER,
    day INTEGER,
    FOREIGN KEY (year_id) REFERENCES years (id)
);

CREATE TABLE spent (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    day_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    amount NUMERIC NOT NULL DEFAULT 0.00,
    FOREIGN KEY (day_id) REFERENCES days (id)
);

--queries
SELECT days.day, days.daily_expenses
    FROM months
    JOIN days ON  days.month_id = months.id
    JOIN years ON years.id =  months.year_id
    WHERE years.user_id = ?
    AND years.year = ?
    And months.month = ?
    ORDER BY days.day;

SELECT spent.category, spent.amount 
    FROM days
    JOIN spent ON spent.day_id = days.id
    JOIN months ON months.id = days.month_id
    JOIN years ON years.id = months.year_id
    WHERE years.user_id = ?
    AND years.year = ?
    AND months.month = ?
    AND days.day = ?
    ORDER BY spent.amount DESC;