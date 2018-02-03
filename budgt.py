#!/usr/bin/env python3

import sqlite3
import argparse
import calendar
import math
import datetime
import json

from edit_utils import *

# data file
db_file = "budget.db"
struct_file = "structure.json"

# pretty-print dates
def print_date(freq, day):
    if freq.lower() == "daily":
        return "Daily"
    elif freq.lower() == "weekly":
        return "Every " + calendar.day_name[day]
    elif freq.lower() == "monthly":
        return "Every " + ordinal(day) + " of the month"
    else:
        d = datetime.date.fromordinal(day)
        return "Every " + d.strftime("%B ") + ordinal(d.day)

# get ordinal numbers from cardinal ones
def ordinal(n):
    suffix = "tsnrhtdd"[((n // 10) % 10 != 1) * (n % 10 < 4) * n % 10::4]
    return "{:d}{:s}".format(n, suffix)

# get account data from db
def get_db_data(cursor, table="accounts"):
    cursor.execute("SELECT * FROM " + table)
    return cursor.fetchall()

def add_to_table(c, tbl, data):
    data_str = []
    for col in formats[tbl]:
        el_str = "'{0}'" if col[1] == "text" else "{0}"
        data_str.append(el_str.format(data[col[0]]))
    c.execute("INSERT INTO {0} VALUES ({1})".format(tbl, ", ".join(data_str)))
    return

if __name__ == '__main__':
    # find out what the user wants
    parser = argparse.ArgumentParser(
        description="create or modify a budget database",
        epilog="edits are manual unless a file is passed as an argument")
    parser.add_argument("-c", "--clear", action="store_true",
                        help="clear all entries before processing")
    edit_g = parser.add_mutually_exclusive_group()
    edit_g.add_argument("-e", "--edit", action="store_true",
                        help="edit, add, or remove entries")
    edit_g.add_argument("-u", "--update", action="store_true",
                        help="update account balances")
    # parser.add_argument("-f", "--file", help="input data from file")
    args = parser.parse_args()
    # get definition of data structures
    with open(struct_file, "r") as f:
        formats = json.load(f)
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
        for k, v in formats.items():
            fmt_str = ", ".join([" ".join(a) for a in v])
            c.execute('CREATE TABLE IF NOT EXISTS {0} ({1})'.format(k, fmt_str))
        # editing
        if args.edit:
            print_edit_opts()
            while True:
                edit_tbl = input("Choose category to edit: ")
                if not edit_tbl: break
                # go to the table that was picked
                if is_letter_opt(edit_tbl, "a"):
                    # show accounts
                    accts = get_db_data(c, "accounts")
                    show_accts(accts)
                    # decide what to do
                    a_r_m = input("Choose operation to perform: ")
                    if not a_r_m:
                        continue
                    elif is_letter_opt(a_r_m, "a"):
                        acct_info = get_acct_input()
                        add_to_table(c, "accounts", acct_info)
                    elif is_letter_opt(a_r_m, "r"):
                        acct = input("Enter account to remove: ")
                        if acct in [a['name'] for a in accts]:
                            c.execute("DELETE FROM accounts WHERE name='{0}'".format(acct))
                        else:
                            print("{0} not found in list of accounts.".format(acct))
                    elif is_letter_opt(a_r_m, "m"):
                        pass
                    else:
                        print_edit_oper()
                elif is_letter_opt(edit_tbl, "t"):
                    # show transactions
                    trscts = get_db_data(c, "transactions")
                    show_trsct(trscts)
                    # decide what to do
                    a_r_m = input("Choose operation to perform: ")
                    if not a_r_m: continue
                elif is_letter_opt(edit_tbl, "h"):
                    print_edit_opts()
                else:
                    print("Unrecognized option. Enter 'H' for help.")
                    continue
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
        # show accounts
        show_accts(get_db_data(c, "accounts"))
        # show transactions
        show_trsct(get_db_data(c, "transactions"))
        # commit all changes to the database
        conn.commit()
