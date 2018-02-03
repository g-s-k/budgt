#!/usr/bin/env python3

import sqlite3
import math
import json

from edit_utils import *
from program_utils import *
from db_utils import *

# data file
db_file = "budget.db"
struct_file = "structure.json"

if __name__ == '__main__':
    # find out what the user wants
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
            clear_db(c, formats.keys())
        # make tables if they don't already exist
        init_db(c, formats)
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
                acct_info = get_acct_input(positive=False, min_balance=False)
                if not acct_info['name']: break
                if acct_info['name'] in [a['name'] for a in accts]:
                    # turn dict into query and execute it
                    cmd_str = build_update_query(acct_info)
                    if cmd_str is not None:
                        c.execute(cmd_str)
                else:
                    print("Account '{0}' not in database.".format(acct_info['name']))
                print("")
        # show accounts
        show_accts(get_db_data(c, "accounts"))
        # show transactions
        show_trsct(get_db_data(c, "transactions"))
        # commit all changes to the database
        conn.commit()
