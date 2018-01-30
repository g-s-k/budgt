 #!/usr/bin/env python3

import sqlite3
import argparse

# data file - The Palm - 250 W 50 St - 8th Ave on South side
db_file = 'budget.db'

if __name__ == '__main__':
    # find out what the user wants
    parser = argparse.ArgumentParser(description="Create and/or modify a budget database.")
    subs = parser.add_subparsers()
    # list what's there
    parser_list = subs.add_parser("show", help="Display data already in database")
    # change entries
    parser_edit = subs.add_parser("edit", help="Add or remove entries from database")
    # update accounts
    parser_update = subs.add_parser("update", help="Update balances")
    # arg_group = parser.add_mutually_exclusive_group()
    # arg_group.add_argument("-l", "--list", action="store_true",
    #                        help="Display all account and transaction data")
    # arg_group.add_argument("-c", "--clear", action="store_true",
    #                        help="Clear existing data")
    # arg_group.add_argument("-a", "--account", action="store_true",
    #                        help="Add, change or remove accounts")
    # arg_group.add_argument("-t", "--transaction", action="store_true",
    #                        help="Add, change or remove transactions")
    args = parser.parse_args()
    # see what's going on in the file
    # with sqlite3.connect(db_file) as conn:
    #     # prepare cursor
    #     conn.row_factory = sqlite3.Row
    #     c = conn.cursor()
    #     # clear data if prompted
    #     if args.clear:
    #         c.execute("DROP TABLE IF EXISTS accounts;")
    #         c.execute("DROP TABLE IF EXISTS transactions;")
    #     # make tables if they don't already exist
    #     c.execute('CREATE TABLE IF NOT EXISTS accounts (name text PRIMARY KEY, balance numeric, holds numeric, positive integer);')
    #     c.execute('CREATE TABLE IF NOT EXISTS transactions (name text PRIMARY KEY, amount numeric NOT NULL, frequency text NOT NULL, day integer, account text NOT NULL, FOREIGN KEY (account) REFERENCES accounts(name));')
    #     # commit all changes to the database
    #     conn.commit()
