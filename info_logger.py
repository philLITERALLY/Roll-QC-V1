"""This module contains all functions and setup required for the programs logging"""

# External Libraries
import logging
import datetime

# My Modules
import variables

logging.basicConfig(filename='logging.log', level=logging.DEBUG)


def init():
    """This function creates a new log with current date time"""
    logging.info('------')
    logging.info(' ')
    logging.info('Start: %s', str(datetime.datetime.now()))
    logging.info(' ')


def camera_settings(capture):
    """This function writes the camera settings to the log"""
    logging.info('Camera Settings: ')
    for camera_setting in range(len(variables.CAMERA_VARIABLES)):
        logging.info(
            '\t' + str(variables.CAMERA_VARIABLES[camera_setting]) +
            ' - ' + str(capture.get(camera_setting))
        )
    logging.info(' ')


def shutdown():
    """This function writes the shutdown information to the log"""
    logging.info('End: %s', str(datetime.datetime.now()))
    logging.info(' ')
