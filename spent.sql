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

CREATE TABLE dates (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    year_id INTEGER NOT NULL,
    month INTEGER,
    day INTEGER,
    FOREIGN KEY (year_id) REFERENCES years (id)
);

CREATE TABLE spent (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    year_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    amount NUMERIC NOT NULL DEFAULT 0.00,
    FOREIGN KEY (date_id) REFERENCES years (id)
);


--queries
SELECT years.year, SUM(spent.amount) 
    FROM years 
    JOIN dates ON years.id = dates.year_id
    JOIN spent ON dates.id = spent.date_id
    WHERE years.user_id = 
    GROUP BY years.year
    ORDER BY years.year DESC;