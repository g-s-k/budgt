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
    # accumulate transactions
    date_vec = np.arange(n_days) * dt.timedelta(days=1) + dt.date.today()
    vect_is_today = np.vectorize(is_today)
    # handle income first - this is nonflexible
    income_only = lambda x: x["dest"] and not x["source"]
    for trans in filter(income_only, transactions):
        accts[trans["dest"]]["value"] += np.cumsum(trans["amount"] * vect_is_today(date_vec, dict(trans)))
    # spending is (for planning purposes) regular and nonflexible
    spend_only = lambda x: x["source"] and not x["dest"]
    for trans in filter(spend_only, transactions):
        accts[trans["source"]]["value"] -= np.cumsum(trans["amount"] * vect_is_today(date_vec, dict(trans)))
    # transfers are much more complex
    trnsfr_only = lambda x: x["source"] and x["dest"]
    for day in range(n_days):
        for trans in filter(trnsfr_only, transactions):
            if is_today(date_vec[day], trans):
                try:
                    # check pre-transaction balances
                    pre_trsct = safe_get_balances(accts, trans, day)
                    # ensure they are sufficient
                    if accts[trans["source"]]["positive"] and \
                            np.any(accts[trans["source"]]["value"][day:] - trans["amount"] < accts[trans["source"]]["min_balance"]):
                                raise ValueError("insufficient funds in account {0}".format(trans["source"]))
                    if pre_trsct["dest"] is not None and \
                            not accts[trans["dest"]]["positive"] and \
                            pre_trsct["dest"] + trans["amount"] > 0:
                        if pre_trsct["dest"] < -accts[trans["dest"]]["min_balance"]:
                            trans_amt = -pre_trsct["dest"]
                        else:
                            raise ValueError("credit account {0} balance "
                                             "should not exceed threshhold "
                                             "unless being paid off".format(trans["dest"]))
                    else:
                        trans_amt = trans["amount"]
                    in_acct = []
                    if trans["source"] in accts:
                        in_acct.append("s")
                        accts[trans["source"]]["value"][day:] -= trans_amt
                    if trans["dest"] in accts:
                        in_acct.append("d")
                        accts[trans["dest"]]["value"][day:] += trans_amt
                    if verbosity:
                        print_hist(date_vec[day], trans, trans_amt, safe_get_balances(accts, trans, day), verbosity=verbosity)
                except ValueError as ve:
                    if verbosity > 2:
                        print_hist(date_vec[day], trans, trans["amount"], safe_get_balances(accts, trans, day), success=False, verbosity=verbosity)
                    # pass
    # plot it
    pos_accts = {k: v for k, v in accts.items() if v["positive"]}
    gross_pos = plot_stacked(date_vec, pos_accts)
    neg_accts = {k: v for k, v in accts.items() if not v["positive"]}
    gross_neg = plot_stacked(date_vec, neg_accts)
    # plot net worth and show it
    plt.plot(date_vec, gross_pos + gross_neg, linestyle="-.", color="black", label="Net worth")
    plt.legend()
    plt.show()
    return


def plot_stacked(date_vec, accts):
    old_vals = np.zeros(date_vec.shape)
    for n, a in accts.items():
        plt.fill_between(date_vec, a["value"] + old_vals, old_vals, label=n, alpha=0.75)
        old_vals += a["value"]
    return old_vals


def safe_get_balances(accts, trans, day):
    names = ("source", "dest")
    return {name: accts.get(trans[name], {}).get("value", [None] * (day + 1))[day] for name in names}


def strf_bal(bal):
    return "" if bal is None else "{0:.02f}".format(bal)


def print_hist(day, trsct_meta, trsct_amt, bals, success=True, verbosity=1):
    # build format string
    fmt_str = "{0:15s} {1:15s} {2:9.02f}   {3:15s}"
    if verbosity > 1:
        fmt_str += " {4:>9s} {5:15s} {6:>9s}"
        if verbosity > 2:
            fmt_str += " {7:s}"
    else:
        fmt_str += " {5:15s}"
    # fill it in and print it out
    print(fmt_str.format(day.strftime("%a, %b %d"), trsct_meta["name"],
                         trsct_amt, trsct_meta["source"],
                         strf_bal(bals["source"]), trsct_meta["dest"],
                         strf_bal(bals["dest"]), repr(success)))
    return

