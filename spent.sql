-- Create a spent table in the spent database
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    pass_hash TEXT NOT NULL,
    spent_total NUMERIC NOT NULL DEFAULT 0.00
);

CREATE UNIQUE INDEX username  ON users (username);

CREATE TABLE spent (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id INTEGER NOT NULL,
    amount NUMERIC NOT NULL,
    spent_date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users_id
);