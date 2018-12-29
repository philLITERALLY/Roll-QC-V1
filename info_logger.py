'''This module contains all functions and setup required for the programs logging'''

# External Libraries
import logging
import datetime
import csv

# My Modules
import variables
import config

logging.basicConfig(filename='logging_' + datetime.datetime.now().strftime('%d-%m-%Y') + '.log', level=logging.DEBUG)


def init():
    '''This function creates a new log with current date time'''
    logging.info('------')
    logging.info(' ')
    logging.info('Start: %s', str(datetime.datetime.now()))


def camera_settings(capture):
    '''This function writes the camera settings to the log'''
    logging.debug(' ')
    logging.debug('Camera Settings: ')
    for camera_setting in range(len(variables.CAMERA_VARIABLES)):
        logging.debug(
            '\t' + str(variables.CAMERA_VARIABLES[camera_setting]) +
            ' - ' + str(capture.get(camera_setting))
        )

def login(keycard_value, username):
    '''This function writes the login information to the log'''
    logging.info(' ')
    logging.info('Login success:')
    logging.info('  Keycard Value: %s', keycard_value)
    logging.info('  Username: %s', username)
    logging.info('  Time: %s', datetime.datetime.now())

def login_error(keycard_value):
    '''This function writes failed login attempt information to the log'''
    logging.error(' ')
    logging.error('Login Fail:')
    logging.error('  Keycard Value: %s', keycard_value)
    logging.error('  Time: %s', datetime.datetime.now())

def logout(keycard_value, username):
    '''This function writes the logout information to the log'''
    logging.info(' ')
    logging.info('Logout success:')
    logging.info('  Keycard Value: %s', keycard_value)
    logging.info('  Username: %s', username)
    logging.info('  Time: %s', datetime.datetime.now())

def logout_error(keycard_value):
    '''This function writes failed logout attempt information to the log'''
    logging.error(' ')
    logging.error('Logout Fail:')
    logging.error('  Keycard Value: %s', keycard_value)
    logging.error('  Time: %s', datetime.datetime.now())

def result(pass_counts, fail_counts):
    '''This adds a row result to CSV file'''
    row = [str(datetime.datetime.now())]

    for i in range(config.LANE_COUNT):
        row.append(str(pass_counts[i]))
        row.append(str(fail_counts[i]))

    with open('results.csv', 'ab') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)

    csvFile.close()

def shutdown():
    '''This function writes the shutdown information to the log'''
    logging.info(' ')
    logging.info('End: %s', str(datetime.datetime.now()))
    logging.info(' ')
