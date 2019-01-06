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

def settings_access(keycard_value, username):
    '''This function writes the settings_access information to the log'''
    logging.info(' ')
    logging.info('Settings Accessed:')
    logging.info('  Keycard Value: %s', keycard_value)
    logging.info('  Username: %s', username)
    logging.info('  Time: %s', datetime.datetime.now())

def settings_access_error(keycard_value):
    '''This function writes failed settings access attempt information to the log'''
    logging.error(' ')
    logging.error('Settings Access Fail:')
    logging.error('  Keycard Value: %s', keycard_value)
    logging.error('  Time: %s', datetime.datetime.now())

def result(lane, width, height):
    '''This adds a row result to CSV file'''
    row = [str(datetime.datetime.now())]
    row.append(str(lane))
    row.append(str(width))
    row.append(str(height))

    with open('results.csv', 'ab') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)

    csvFile.close()

def shutdown():
    '''This function writes the shutdown information to the log'''
    logging.info(' ')
    logging.info('End: %s', str(datetime.datetime.now()))
    logging.info(' ')
