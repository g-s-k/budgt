import argparse
import calendar
import datetime

# find out what the user wants
parser = argparse.ArgumentParser(prog="budgt.py",
    description="create or modify a budget database",
    epilog="edits are manual unless a file is passed as an argument")
parser.add_argument("-c", "--clear", action="store_true",
                    help="clear all entries before processing")
edit_g = parser.add_mutually_exclusive_group()
edit_g.add_argument("-e", "--edit", action="store_true",
                    help="edit, add, or remove entries")
edit_g.add_argument("-u", "--update", action="store_true",
                    help="update account balances")
parser.add_argument("-f", "--file", help="input data from file")

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
    if n < 0:
        if n == -1:
            return "last"
        else:
            return ordinal(-n) + " to last"
    else:
        suffix = "tsnrhtdd"[((n // 10) % 10 != 1) * (n % 10 < 4) * n % 10::4]
        return "{:d}{:s}".format(n, suffix)

# show accounts from list of rows
def show_accts(accts):
    print("\nAccount\t\t Balance\t   Holds")
    print("-------\t\t -------\t   -----")
    for row in sorted(accts, key=lambda x: x['name']):
        name_pad = row['name'] + ' ' * (8 - len(row['name']))
        factor = 1 if row['positive'] else -1
        print("{0}\t{1:8.02f}\t{2:8.02f}".format(name_pad,
            row['balance'] * factor, -row['holds']))
    print("")

# show transactions from list of rows
def show_trsct(trsct):
    fmt_str = "{0:15s}  {1:>9s}  {2:15s}  {3:15s}  {4:s}"
    fmt_num = "{0:15s}  {1:9.02f}  {2:15s}  {3:15s}  {4:s}"
    print("")
    print(fmt_str.format("Transaction", "Amount", "Source", "Destination", "Frequency"))
    print(fmt_str.format("-----------", "------", "------", "-----------", "---------"))
    for row in sorted(trsct, key=lambda x: x['name']):
        print(fmt_num.format(row['name'], row['amount'], row['source'],
            row['dest'], print_date(row['frequency'], row['day'])))
    print("")
