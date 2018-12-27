"""This module contains all functions and setup required for the programs logging"""

# External Libraries
import logging
import datetime

# My Modules
import variables
import config

logging.basicConfig(filename='logging_' + datetime.datetime.now().strftime('%d-%m-%Y') + '.log', level=logging.DEBUG)


def init():
    """This function creates a new log with current date time"""
    logging.info('------')
    logging.info(' ')
    logging.info('Start: %s', str(datetime.datetime.now()))


def camera_settings(capture):
    """This function writes the camera settings to the log"""
    logging.debug(' ')
    logging.debug('Camera Settings: ')
    for camera_setting in range(len(variables.CAMERA_VARIABLES)):
        logging.debug(
            '\t' + str(variables.CAMERA_VARIABLES[camera_setting]) +
            ' - ' + str(capture.get(camera_setting))
        )

def login(keycard_value, username):
    """This function writes the login information to the log"""
    logging.info(' ')
    logging.info('Login success:')
    logging.info('  Keycard Value: %s', keycard_value)
    logging.info('  Username: %s', username)
    logging.info('  Time: %s', datetime.datetime.now())

def login_error(keycard_value):
    """This function writes failed login attempt information to the log"""
    logging.error(' ')
    logging.error('Login Fail:')
    logging.error('  Keycard Value: %s', keycard_value)
    logging.error('  Time: %s', datetime.datetime.now())

def logout(keycard_value, username):
    """This function writes the logout information to the log"""
    logging.info(' ')
    logging.info('Logout success:')
    logging.info('  Keycard Value: %s', keycard_value)
    logging.info('  Username: %s', username)
    logging.info('  Time: %s', datetime.datetime.now())

def logout_error(keycard_value):
    """This function writes failed logout attempt information to the log"""
    logging.error(' ')
    logging.error('Logout Fail:')
    logging.error('  Keycard Value: %s', keycard_value)
    logging.error('  Time: %s', datetime.datetime.now())

def results_header():
    """This creates the header for running results logging"""
    logging.info(' ')
    logging.info('LANE 1 PASS                | LANE 1 FAIL                | LANE 2 PASS                | LANE 2 FAIL                | LANE 3 PASS                | LANE 3 FAIL        ')

def result(pass_counts, fail_counts):
    """This adds a row result"""
    result_str = ''
    for i in range(config.LANE_COUNT):
        result_str += str(pass_counts[i]).ljust(26) + ' | ' + str(fail_counts[i]).ljust(26) + ' | '
    
    logging.info(result_str)

def shutdown():
    """This function writes the shutdown information to the log"""
    logging.info(' ')
    logging.info('End: %s', str(datetime.datetime.now()))
    logging.info(' ')
