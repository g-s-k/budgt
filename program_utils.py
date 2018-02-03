import argparse

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
