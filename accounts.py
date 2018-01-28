#!/usr/bin/env python3

import sys
import sqlite3

# data file
db_file = 'budget.db'

if __name__ == '__main__':
    # fetch data
    with sqlite3.connect(db_file) as conn:
        # connect to database
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # get account info
        c.execute("SELECT * FROM ACCOUNTS")
        accounts = c.fetchall()
        # display the data
        print("\nAccount\t\t Balance\t   Holds")
        print("-------\t\t -------\t   -----")
        for row in sorted(accounts, key=lambda x: x['name']):
            name_pad = row['name'] + ' ' * (8 - len(row['name']))
            factor = 1 if row['positive'] else -1
            print("{0}\t{1:8.02f}\t{2:8.02f}".format(name_pad, row['balance'] * factor, -row['holds']))
        print("")
        # update if flagged
        if len(sys.argv) > 1:
            while True:
                acct = input("Enter account to modify (leave blank to exit): ")
                if not acct: break
                if acct in [a['name'] for a in accounts]:
                    bal = float(input("Enter balance: "))
                    hol = float(input("Enter holds:   "))
                    c.execute("UPDATE ACCOUNTS SET balance={0:.02f}, "
                              "holds={1:.02f} WHERE name=\'{2}\'".format(bal, hol, acct))
                else:
                    print("Account \'{}\' not recognized.".format(acct))
                print("")
            print("")
