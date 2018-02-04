# find partial option matches
def is_letter_opt(strn, letr, cs_sen=False):
    if not cs_sen:
        strn = strn.lower()
        letr = letr.lower()
    return strn in (letr, "'" + letr + "'", '"' + letr + '"', "(" + letr + ")",
                    "[" + letr + "]")

# show edit options
def print_edit_opts():
    print("\nEditing options:\n")
    print("    H        help")
    print("    A        accounts")
    print("    T        transactions")
    print("    (blank)  exit")
    print("")

# show editing operations
def print_edit_oper():
    print("\nEntry operations:\n")
    print("    A        add")
    print("    M        modify existing")
    print("    R        remove")
    print("    (blank)  exit")
    print("")

# get kb input for account
def get_acct_input(name=None, balance=None, holds=None, positive=None, min_balance=None, name_only=False):
    if name is None:
        name = input("Enter account name: ")
    if name and not name_only:
        if balance is None:
            balance = input("Enter account balance: ")
            balance = float(balance) if balance else 0.
        if holds is None:
            holds = input("Enter account holds: ")
            holds = float(holds) if holds else 0.
        if positive is None:
            positive = input("Enter 1 if this account holds positive value, or 0 "
                             "for negative value: ")
            positive = int(positive) if positive else 1
        if positive and min_balance is None:
            min_balance = input("Enter minimum balance: ")
        min_balance = float(min_balance) if min_balance else 0
    return dict(name=name, balance=balance, holds=holds,
                min_balance=min_balance, positive=positive, color=None)

# get kb input for transaction
def get_trsct_input(name=None, amount=None, source=None, dest=None,
                    frequency=None, day=None, name_only=False):
    name = input("Enter transaction name: ")
    if name and not name_only:
        amount = input("Enter transaction amount: ")
        amount = float(amount) if amount else 0.
        source = input("Enter source account: ")
        dest = input("Enter destination account: ")
        frequency = input("Enter transaction frequency: ")
        day = input("Enter transaction day: ")
        day = int(day) if day else 0
    return dict(name=name, amount=amount, source=source, dest=dest,
                frequency=frequency, day=day)

def build_update_query(acct_info):
    cmd_str = "UPDATE accounts SET "
    # minimal units
    bal_str = "balance={:.02f}".format(float(acct_info['balance'])) if acct_info['balance'] else ""
    hol_str = "holds={:.02f}".format(float(acct_info['holds'])) if acct_info['holds'] else ""
    # change balance?
    if acct_info['balance']:
        cmd_str += bal_str
        if acct_info['holds']:
            cmd_str += ", " + hol_str
    elif acct_info['holds']:
        cmd_str += hol_str
    else:
        return
    # add account name
    cmd_str += " WHERE name='{0}'".format(acct_info['name'])
    return cmd_str
