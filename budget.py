#!/usr/bin/env python3

import sqlite3
import sys
from datetime import date, timedelta
import numpy as np
import matplotlib.pyplot as plt


# data file
db_file = 'budget.db'

# number of days to forecast
if __name__ == '__main__' and len(sys.argv) > 1:
    numdays = int(sys.argv[1])
else:
    numdays = 365

# connect to database
conn = sqlite3.connect(db_file)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# get transaction data
c.execute("SELECT * FROM TRANSACTIONS")
transactions = c.fetchall()

# get account info
c.execute("SELECT * FROM ACCOUNTS")
accounts = c.fetchall()
conn.close()

# vector of days
days = [date.today() + timedelta(days=x) for x in range(0, numdays)]

series = {}

for acct in accounts:
    if acct['positive']:
        fac = 1
    else:
        fac = -1
    bal = fac * acct['balance'] - acct['holds']
    series[acct['name']] = np.array([bal for day in days])


# function to update accounts
def effect_accounts(data_ind, transaction, series_data):
    if transaction['type'] == 'income':
        series_data[transaction['account']][data_ind:] += transaction['amount']
    else:
        series_data[transaction['account']][data_ind:] -= transaction['amount']
    if transaction['type'] == 'transfer':
        series_data[transaction['name']][data_ind:] += transaction['amount']
    return series_data

for i, day in enumerate(days):
    for el in transactions:
        if el['frequency'] == 'weekly' and day.weekday() == el['day']:
            series = effect_accounts(i, el, series)
        elif el['frequency'] == 'monthly' and day.day == el['day']:
            series = effect_accounts(i, el, series)
        elif el['frequency'] == 'annual' and int(day.strftime('%j')) == el['day']:
            series = effect_accounts(i, el, series)


# function to report payments
def print_transfer(dat, disc, secu, sink='credit card', source='secu_checking'):
    print('transfer ${0:.02f} from {4:s} to {3:s} on {1}. remaining bank balance is ${2:.02f}'.format(
        -disc, dat.strftime('%m-%d'), secu, sink, source))

for j, day in enumerate(days):
    current_balance_c = series['citi'][j]
    current_balance_d = series['discover'][j]
    if current_balance_c < -250 and day.weekday() == 4 and all(x > -current_balance_c for x in series['secu_checking'][j:]):
        series['secu_checking'][j:] = [a + current_balance_c for a in series['secu_checking'][j:]]
        series['citi'][j:] = [a - current_balance_c for a in series['citi'][j:]]
        print_transfer(day, current_balance_c, series['secu_checking'][j], sink='citi')
    if current_balance_d < -50 and day.weekday() == 4 and all(x > -current_balance_d for x in series['secu_checking'][j:]):
        series['secu_checking'][j:] = [a + current_balance_d for a in series['secu_checking'][j:]]
        series['discover'][j:] = [a - current_balance_d for a in series['discover'][j:]]
        print_transfer(day, current_balance_d, series['secu_checking'][j], sink='discover')
    if all(x > 2500 for x in series['secu_checking'][j:]):
        if series['discover'][j] <= -1000:
            payoff_bal = 1000
            series['secu_checking'][j:] = [a - payoff_bal for a in series['secu_checking'][j:]]
            series['discover'][j:] = [a + payoff_bal for a in series['discover'][j:]]
            print_transfer(day, -payoff_bal, series['secu_checking'][j])
        elif series['student_loan'][j] < 0:
            current_loan = max(-1000, series['student_loan'][j])
            series['secu_checking'][j:] = [a + current_loan for a in series['secu_checking'][j:]]
            series['student_loan'][j:] = [a - current_loan for a in series['student_loan'][j:]]
            print_transfer(day, current_loan, series['secu_checking'][j], 'student loan')
        else:
            savings_amt = 1000
            series['secu_checking'][j:] = [a - savings_amt for a in series['secu_checking'][j:]]
            series['secu_savings'][j:] = [a + savings_amt for a in series['secu_savings'][j:]]
            print_transfer(day, -savings_amt, series['secu_checking'][j], 'secu_savings')
    for acct in accounts:
        if not acct['positive'] and series[acct['name']][j] > 0:
            series['secu_checking'][j:] += series[acct['name']][j]
            series[acct['name']][j:] -= series[acct['name']][j]
        elif acct['positive'] and series[acct['name']][j] < 0:
            raise ValueError('Positive account with negative balance: {} on {}'.format(acct['name'],
                                                                                       days[j].strftime('%y-%m-%d')))

# calculate net worth
net_worth = np.zeros_like(series['discover'])
for key in series.keys():
    net_worth += series[key]
print('final net worth on {1} is ${0:0.02f}'.format(net_worth[-1], days[-1].strftime('%Y-%m-%d')))

# plot graph
plt.fill_between(days,
                 series['secu_checking'],
                 color='green',
                 alpha=0.5)
plt.fill_between(days,
                 series['secu_savings'] + series['secu_checking'],
                 y2=series['secu_checking'],
                 color='blue',
                 alpha=0.5)
plt.fill_between(days,
                 series['secu_savings'] + series['roth_ira'] + series['secu_checking'],
                 y2=series['secu_savings'] + series['secu_checking'],
                 color='black',
                 alpha=0.5)
plt.fill_between(days,
                 series['secu_savings'] + series['roth_ira'] + series['secu_checking'] + series['401k'],
                 y2=series['secu_savings'] + series['secu_checking'] + series['roth_ira'],
                 color='purple',
                 alpha=0.5)

plt.fill_between(days,
                 series['citi'],
                 color='yellow',
                 alpha=0.5)
plt.fill_between(days,
                 series['discover'] + series['citi'],
                 y2=series['citi'],
                 color='red',
                 alpha=0.5)
plt.fill_between(days,
                 series['student_loan'] + series['discover'] + series['citi'],
                 y2=series['discover'] + series['citi'],
                 color='orange',
                 alpha=0.5)
plt.plot(days, net_worth, 'k--')
plt.grid()
plt.show()
