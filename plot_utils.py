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
                        fmt_str = "Transaction '{0}' "
                        if "s" in in_acct and "d" in in_acct:
                            fmt_str += "transferred ${1:.02f} from account '{2}' to account '{3}'"
                        elif "s" in in_acct:
                            fmt_str += "decreased account '{2}' balance by ${1:.02f}"
                        elif "d" in in_acct:
                            fmt_str += "increased account '{3}' balance by ${1:.02f}"
                        fmt_str += " on day {4} of {5}"
                        print(fmt_str.format(trans["name"], trans["amount"], trans["source"], trans["dest"], day, n_days))
                except ValueError as ve:
                    if verbosity > 1:
                        print("Transaction '{0}' failed on day {1} of {2} because {3}".format(trans["name"], day, n_days, str(ve)))
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
        plt.fill_between(date_vec, a["value"] + old_vals, old_vals, label=n, alpha=0.8)
        old_vals = a["value"]
    return
