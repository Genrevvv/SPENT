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
    year INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE months (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    year_id INTEGER NOT NULL,
    month INTEGER NOT NULL,
    FOREIGN KEY (year_id) REFERENCES years (id)
);

CREATE TABLE spent (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    month_id INTEGER NOT NULL,
    day INTEGER NOT NULL,
    amount NUMERIC NOT NULL,
    FOREIGN KEY (month_id) REFERENCES months (id)
);