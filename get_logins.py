'''This module gets stored login information'''

import os
import csv

def main():
    LOGINS = []

    my_path = os.path.abspath(os.path.dirname(__file__))
    with open(my_path + '/logins.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            LOGINS.append([row['card_number'], row['user_name']])

    return LOGINS