import numpy as np
import calendar
import datetime as dt
import matplotlib.pyplot as plt

def is_today(day, trans):
    cases = []
    cases.append(trans["frequency"] == "daily")
    cases.append(trans["frequency"] == "weekly" and trans["day"] == day.weekday())
    cases.append(trans["frequency"] == "monthly" and trans["day"] == day.day)
    cases.append(trans["frequency"] == "monthly" and trans["day"] == (day.day - calendar.monthrange(day.year, day.month)[1] - 1))
    cases.append(trans["frequency"] == "annual" and trans["day"] == day.timetuple().tm_yday)
    return any(case for case in cases)

def project_balances(n_days, accounts, transactions, verbosity=0):
    # figure out initial state
    accts = {a["name"]: dict(a) for a in accounts}
    for a in accts.keys():
        accts[a]["value"] = np.zeros(n_days) + (-1)**(accts[a]["positive"] + 1) * accts[a]["balance"] - accts[a]["holds"]
    if verbosity:
        print("")
        fmt_str = "{0:15s} {1:15s} {2:>9s}   {3:15s}"
        if verbosity > 1:
            fmt_str += " {4:>9s} {5:15s} {6:>9s}"
            if verbosity > 2:
                fmt_str += " {7:s}"
        else:
            fmt_str +=  " {5:15s}"
        print(fmt_str.format("Date", "Name", "Amount", "Source", "Balance", "Destination", "Balance", "Success"))
        print(fmt_str.format("----", "----", "------", "------", "-------", "-----------", "-------", "-------"))
    # iterate through days
    date_vec = np.arange(n_days) * dt.timedelta(days=1) + dt.date.today()
    for day in range(n_days):
        for trans in transactions:
            if is_today(date_vec[day], trans):
                try:
                    if trans["source"] in accts and accts[trans["source"]]["positive"] and accts[trans["source"]]["value"][day] - trans["amount"] < accts[trans["source"]]["min_balance"]:
                            raise ValueError("insufficient funds in account {0}".format(trans["source"]))
                    if trans["dest"] in accts and not accts[trans["dest"]]["positive"] and accts[trans["dest"]]["value"][day] + trans["amount"] > 0:
                            raise ValueError("credit account {0} cannot have positive balance".format(trans["dest"]))
                    in_acct = []
                    if trans["source"] in accts:
                        in_acct.append("s")
                        accts[trans["source"]]["value"][day:] -= trans["amount"]
                    if trans["dest"] in accts:
                        in_acct.append("d")
                        accts[trans["dest"]]["value"][day:] += trans["amount"]
                    if verbosity:
                        print_hist(date_vec[day], trans, {"source": 0, "dest": 0}, verbosity=verbosity)
                except ValueError as ve:
                    if verbosity > 2:
                        print_hist(date_vec[day], trans, {"source": 0, "dest": 0}, success=False, verbosity=verbosity)
                    pass
    # plot it
    pos_accts = {k: v for k, v in accts.items() if v["positive"]}
    plot_stacked(date_vec, pos_accts)
    neg_accts = {k: v for k, v in accts.items() if not v["positive"]}
    plot_stacked(date_vec, neg_accts)
    plt.legend()
    plt.show()
    return


def plot_stacked(date_vec, accts):
    old_vals = np.zeros(date_vec.shape)
    for n, a in accts.items():
        plt.fill_between(date_vec, a["value"] + old_vals, old_vals, label=n, alpha=0.75)
        old_vals = a["value"]
    return


def print_hist(day, trsct, bals, success=True, verbosity=1):
    # build format string
    fmt_str = "{0:15s} {1:15s} {2:9.02f}   {3:15s}"
    if verbosity > 1:
        fmt_str += " {4:9.02f} {5:15s} {6:9.02f}"
        if verbosity > 2:
            fmt_str += " {7:s}"
    else:
        fmt_str += " {5:15s}"
    # fill it in and print it out
    print(fmt_str.format(day.strftime("%a, %b %d"), trsct["name"],
                         trsct["amount"], trsct["source"], bals["source"],
                         trsct["dest"], bals["dest"], repr(success)))
