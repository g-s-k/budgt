import numpy as np
import calendar
import datetime as dt
import matplotlib.pyplot as plt

def is_today(day, trans):
    cases = []
    cases.append(trans["frequency"] == "daily")
    cases.append(trans["frequency"] == "weekly" and trans["day"] == day.weekday())
    cases.append(trans["frequency"] == "monthly" and trans["day"] == day.day)
    cases.append(trans["frequency"] == "annual" and trans["day"] == day.timetuple().tm_yday)
    return any(case for case in cases)

def project_balances(n_days, accounts, transactions):
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
                            raise ValueError
                    if trans["dest"] in accts and not accts[trans["dest"]]["positive"] and accts[trans["dest"]]["value"][day] + trans["amount"] > 0:
                            raise ValueError
                    if trans["source"] in accts:
                        accts[trans["source"]]["value"][day:] -= trans["amount"]
                    if trans["dest"] in accts:
                        accts[trans["dest"]]["value"][day:] += trans["amount"]
                except ValueError:
                    pass
    # plot it
    for n, a in accts.items():
        plt.fill_between(date_vec, a["value"], label=n)
    plt.legend()
    plt.show()
