import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

def project_balances(n_days, accounts, transactions):
    days = np.arange(0, n_days) * dt.timedelta(days=1) + dt.date.today()
    trans_lst = []
    for trans in transactions:
        trans_lst.append({"name": trans["name"], "source": trans["source"],
                          "dest": trans["dest"]})
        if trans["frequency"] == "daily":
            trans_lst[-1]["value"] = np.ones(days.shape)
        elif trans["frequency"] == "weekly":
            trans_lst[-1]["value"] = np.array([day.weekday() == trans["day"] for day in days])
        elif trans["frequency"] == "monthly":
            trans_lst[-1]["value"] = np.array([day.day == trans["day"] for day in days])
        else:
            trans_lst[-1]["value"] = np.array([day.timetuple().tm_yday == trans["day"] for day in days])
    for account in accounts:
        account = dict(account)
        account["init_balance"] = (-1)**(account["positive"] + 1) * \
            account["balance"] - account["holds"]
        account["value"] = np.zeros(days.shape) + account["init_balance"]
        for trans in trans_lst:
            if trans["source"] == account["name"]:
                account["value"] -= trans["value"]
            elif trans["dest"] == account["name"]:
                account["value"] += trans["value"]
        plt.plot(days, account["value"])
    # display the projections
    plt.show()
