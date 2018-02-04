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
            edit_cat = {"accounts": {"display": show_accts,
                                     "get": get_acct_input},
                        "transactions": {"display": show_trsct,
                                         "get": get_trsct_input}}
            print_edit_opts()
            while True:
                edit_tbl = input("Choose category to edit: ")
                if not edit_tbl:
                    break
                # go to the table that was picked
                elif is_letter_opt(edit_tbl, "a"):
                    edit_typ = "accounts"
                elif is_letter_opt(edit_tbl, "t"):
                    edit_typ = "transactions"
                else:
                    print_edit_opts()
                    continue
                # show existing data available to edit
                existing_data = get_db_data(c, edit_typ)
                edit_cat[edit_typ]["display"](existing_data)
                # decide what to do
                a_r_m = input("Choose operation to perform: ")
                if not a_r_m:
                    continue
                elif is_letter_opt(a_r_m, "a"):
                    add_data = edit_cat[edit_typ]["get"]()
                    insert_record(c, edit_typ, add_data, formats)
                elif is_letter_opt(a_r_m, "r"):
                    rem_data = edit_cat[edit_typ]["get"](name_only=True)
                    delete_record(c, edit_typ, {"name": rem_data['name']})
                elif is_letter_opt(a_r_m, "m"):
                    mod_data = edit_cat[edit_typ]["get"]()
                    name_tmp = mod_data.pop("name")
                    update_record(c, edit_typ, mod_data, {"name": name_tmp})
                else:
                    print_edit_oper()
        elif args.update:
            # show accounts
            accts = get_db_data(c, "accounts")
            show_accts(accts)
            # update accounts until break
            while True:
                acct_info = get_acct_input(positive=False, min_balance=False)
                if not acct_info['name']:
                    break
                else:
                    acct_info["positive"] = None
                    acct_info["min_balance"] = None
                    name_tmp = acct_info.pop('name')
                    update_record(c, 'accounts', acct_info, {"name": name_tmp})
        # show accounts
        show_accts(get_db_data(c, "accounts"))
        # show transactions
        show_trsct(get_db_data(c, "transactions"))
        # commit all changes to the database
        conn.commit()
