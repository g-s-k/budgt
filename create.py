 #!/usr/bin/env python3

import sqlite3

# data file
db_file = 'budget.db'

if __name__ == '__main__':
    # see what's going on in the file
    with sqlite3.connect(db_file) as conn:
        # prepare cursor
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # make tables if they don't already exist
        c.execute('CREATE TABLE IF NOT EXISTS accounts (name text PRIMARY KEY, balance numeric, holds numeric, positive integer);')
        c.execute('CREATE TABLE IF NOT EXISTS transactions (name text PRIMARY KEY, amount numeric NOT NULL, frequency text NOT NULL, day integer, account text NOT NULL, FOREIGN KEY (account) REFERENCES accounts(name));')
        # commit all changes to the database
        conn.commit()
