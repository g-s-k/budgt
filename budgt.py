 #!/usr/bin/env python3

import sqlite3
import argparse
import calendar
import math
import datetime

# data file
db_file = 'budget.db'

# show accounts from list of rows
def show_accts(accts):
    print("\nAccount\t\t Balance\t   Holds")
    print("-------\t\t -------\t   -----")
    for row in sorted(accts, key=lambda x: x['name']):
        name_pad = row['name'] + ' ' * (8 - len(row['name']))
        factor = 1 if row['positive'] else -1
        print("{0}\t{1:8.02f}\t{2:8.02f}".format(name_pad, row['balance'] * factor, -row['holds']))
    print("")

# show transactions from list of rows
def show_trsct(trsct):
    print("\nTransaction\t  Amount   Source      Frequency")
    print("-----------\t  ------   ------      ---------")
    for row in sorted(trsct, key=lambda x: x['name']):
        print("{0:8s}\t{1:8.02f}   {2:10s}  {3}".format(row['name'], row['amount'], row['account'], print_date(row['frequency'], row['day'])))
    print("")

# pretty-print dates
def print_date(freq, day):
    if freq.lower() == "daily":
        return "Every day"
    elif freq.lower() == "weekly":
        return "Every " + calendar.day_name[day]
    elif freq.lower() == "monthly":
        return "Every " + ordinal(day) + " of the month"
    else:
        d = datetime.date.fromordinal(day)
        return "Every " + d.strftime("%B ") + ordinal(d.day)

# get ordinal numbers from cardinal ones
def ordinal(n):
    return "{:d}{:s}".format(n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])

# get account data
def get_db_data(cursor, table="accounts"):
    cursor.execute("SELECT * FROM " + table)
    return cursor.fetchall()

if __name__ == '__main__':
    # find out what the user wants
    parser = argparse.ArgumentParser(
        description="create or modify a budget database",
        epilog="edits are manual unless a file is passed as an argument")
    parser.add_argument("-c", "--clear", action="store_true", help="clear all entries before processing")
    edit_g = parser.add_mutually_exclusive_group()
    # edit_g.add_argument("-e", "--edit", action="store_true", help="edit, add, or remove entries")
    edit_g.add_argument("-u", "--update", action="store_true", help="update account balances")
    # parser.add_argument("-f", "--file", help="input data from file")
    args = parser.parse_args()
    # see what's going on in the file
    with sqlite3.connect(db_file) as conn:
        # prepare cursor
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # clear data if prompted
        if args.clear:
            c.execute("DROP TABLE IF EXISTS accounts")
            c.execute("DROP TABLE IF EXISTS transactions")
        # make tables if they don't already exist
        c.execute('CREATE TABLE IF NOT EXISTS accounts (name text PRIMARY KEY, balance numeric, holds numeric, positive integer)')
        c.execute('CREATE TABLE IF NOT EXISTS transactions (name text PRIMARY KEY, amount numeric NOT NULL, frequency text NOT NULL, day integer, account text NOT NULL, FOREIGN KEY (account) REFERENCES accounts(name))')
        # editing
        if args.edit:
            pass
        elif args.update:
            # show accounts
            accts = get_db_data(c, "accounts")
            show_accts(accts)
            # update accounts until break
            while True:
                acct = input("Enter account to update (leave blank to exit): ")
                if not acct: break
                if acct in [a['name'] for a in accts]:
                    # start sql command
                    cmd_str = "UPDATE accounts SET "
                    # get input(s)
                    bal = input("Enter balance: ")
                    hol = input("Enter holds:   ")
                    # minimal units
                    bal_str = "balance={:.02f}".format(float(bal)) if bal else ""
                    hol_str = "holds={:.02f}".format(float(hol)) if hol else ""
                    # change balance?
                    if bal:
                        cmd_str += bal_str
                        if hol:
                            cmd_str += ", " + hol_str
                    elif hol:
                        cmd_str += hol_str
                    else:
                        print("No values entered.")
                        continue
                    # add account name
                    cmd_str += " WHERE name='{0}'".format(acct)
                    print(cmd_str)
                    # actually execute it
                    c.execute(cmd_str)
                else:
                    print("Account '{0}' not in database.".format(acct))
                print("")
        else:
            # show accounts
            show_accts(get_db_data(c, "accounts"))
            # show transactions
            show_trsct(get_db_data(c, "transactions"))
        # commit all changes to the database
        conn.commit()
