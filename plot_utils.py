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
    # prepare table
    print_hist_header(verbosity)
    # figure out initial state
    accts = {a["name"]: dict(a) for a in accounts}
    for a in accts.keys():
        accts[a]["value"] = np.zeros(n_days) + (-1)**(accts[a]["positive"] + 1) * accts[a]["balance"] - accts[a]["holds"]
    # accumulate transactions
    date_vec = np.arange(n_days) * dt.timedelta(days=1) + dt.date.today()
    vect_is_today = np.vectorize(is_today)
    accum_trsct = lambda t: np.cumsum(t["amount"] * vect_is_today(date_vec, dict(t)))
    # handle income first - this is nonflexible
    income_only = lambda x: x["dest"] and not x["source"]
    for trans in filter(income_only, transactions):
        accts[trans["dest"]]["value"] += accum_trsct(trans)
    # spending is (for planning purposes) regular and nonflexible
    spend_only = lambda x: x["source"] and not x["dest"]
    for trans in filter(spend_only, transactions):
        accts[trans["source"]]["value"] -= accum_trsct(trans)
    # transfers are much more complex
    trnsfr_only = lambda x: x["source"] and x["dest"]
    for day in range(n_days):
        for trans in filter(lambda t: is_today(date_vec[day], t),
                            filter(trnsfr_only, transactions)):
            # defaults
            trans_amt = trans["amount"]
            success = True
            try:
                # check pre-transaction balances
                pre_trsct = safe_get_balances(accts, trans, day)
                # calculate optimal amount to move (if required)
                if not trans_amt:
                    trans_amt = np.min(np.abs(np.concatenate([[pre_trsct["dest"]], accts[trans["source"]]["value"][day:] - accts[trans["source"]]["min_balance"] if accts[trans["source"]]["positive"] else 0])))
                # avoid overdrafts, even into the future
                if accts[trans["source"]]["positive"] and \
                    np.any(accts[trans["source"]]["value"][day:] - trans_amt < accts[trans["source"]]["min_balance"]):
                        raise ValueError("insufficient funds "
                                         "in account {0}".format(trans["source"]))
                # avoid positive balances in negative accounts
                # TODO: simplify this with some vectorized numpy magic
                if not accts[trans["dest"]]["positive"] and \
                        pre_trsct["dest"] + trans_amt > 0:
                    if pre_trsct["dest"] < -accts[trans["dest"]]["min_balance"]:
                        trans_amt = -pre_trsct["dest"]
                    else:
                        raise ValueError("credit account {0} balance "
                                         "should not exceed threshhold "
                                         "unless being paid off".format(trans["dest"]))
                # actually move the money
                accts[trans["source"]]["value"][day:] -= trans_amt
                accts[trans["dest"]]["value"][day:] += trans_amt
            # if the user wants to see what was attempted, show them
            except ValueError:
                success = False
            # log the transactions in their table
            finally:
                print_hist(date_vec[day], trans, trans_amt,
                           safe_get_balances(accts, trans, day),
                           success=success, verbosity=verbosity)
    plot_accts(date_vec, accts)
    return


def plot_accts(date_vec, accts):
    # plot it
    pos_accts = {k: v for k, v in accts.items() if v["positive"]}
    gross_pos = plot_stacked(date_vec, pos_accts)
    neg_accts = {k: v for k, v in accts.items() if not v["positive"]}
    gross_neg = plot_stacked(date_vec, neg_accts)
    # plot net worth and show it
    plt.plot(date_vec, gross_pos + gross_neg,
             linestyle="-.", color="black", label="Net worth")
    plt.legend()
    plt.show()
    return


def plot_stacked(date_vec, accts):
    old_vals = np.zeros(date_vec.shape)
    for n, a in accts.items():
        plt.fill_between(date_vec, a["value"] + old_vals, old_vals,
                         label=n, alpha=0.75)
        old_vals += a["value"]
    return old_vals


def safe_get_balances(accts, trans, day):
    names = ("source", "dest")
    return {name: accts.get(trans[name], {}).get("value", \
            [None] * (day + 1))[day] for name in names}


def strf_bal(bal):
    return "" if bal is None else "{0:.02f}".format(bal)


def print_hist_header(verbosity):
    if verbosity:
        print("")
        fmt_str = "{0:15s} {1:15s} {2:>9s}   {3:15s}"
        if verbosity > 1:
            fmt_str += " {4:>9s} {5:15s} {6:>9s}"
            if verbosity > 2:
                fmt_str += " {7:s}"
        else:
            fmt_str +=  " {5:15s}"
        print(fmt_str.format("Date", "Name", "Amount", "Source", "Balance",
                             "Destination", "Balance", "Success"))
        print(fmt_str.format("----", "----", "------", "------", "-------",
                             "-----------", "-------", "-------"))
    return


def print_hist(day, trsct_meta, trsct_amt, bals, success=True, verbosity=1):
    # catch non-logging cases and failed attempts
    if not verbosity or verbosity < 3 and not success:
        return
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

