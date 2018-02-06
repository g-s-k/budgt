# budgt.py
Budget forecasting with Python

## What it can do
  * Make its own database file
  * Add and remove accounts and transactions
  * Help you see what's in your database and update the values
  * Use that data to project your future account balances
  * Plot your balances into the future
  * Tell you when to pay off your credit card

## What it should do
  * Calculate and plot net worth
  * Stack different accounts' balances on top of each other
  * Provide color and order configuration that is stored in the database
  * Get current balances from the web (via OFX)
  * Support payment due dates
  * Support negative date indices
  * Support batch import/export from json

## How it works
  1. Account balances and recurrent transactions (paydays, expenses, etc.) are stored in a sqlite3 database
  2. These are pulled out with python and extrapolated for some period of time (default is a calendar year)
  3. The projected daily balances are plotted with matplotlib and displayed
  4. The program decides on the optimal times to pay off debts and lists these in the terminal
