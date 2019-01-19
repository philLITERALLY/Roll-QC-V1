'''This module gets stored login information'''

import csv

def main():
    LOGINS = []

    with open(R'C:\Users\User\Roll-QC-V1\Locker\logins.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            LOGINS.append([row['card_number'], row['user_name']])

    return LOGINS