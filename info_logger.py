''' This module contains all functions and setup required for the programs logging '''

# External Libraries
import logging
import datetime
import csv

# My Modules
import variables
import config

logging.basicConfig(filename='logging_' + datetime.datetime.now().strftime('%d-%m-%Y') + '.log', level=logging.DEBUG)


def init():
    ''' This function creates a new log with current date time '''
    logging.info('------')
    logging.info(' ')
    logging.info('Start: %s', str(datetime.datetime.now()))


def camera_settings(capture):
    ''' This function writes the camera settings to the log '''
    logging.debug(' ')
    logging.debug('Camera Settings: ')
    for camera_setting in range(len(variables.CAMERA_VARIABLES)):
        logging.debug(
            '\t' + str(variables.CAMERA_VARIABLES[camera_setting]) +
            ' - ' + str(capture.get(camera_setting))
        )

def settings_access(keycard_value, username):
    ''' This function writes the settings_access information to the log '''
    logging.info(' ')
    logging.info('Settings Accessed:')
    logging.info('  Keycard Value: %s', keycard_value)
    logging.info('  Username: %s', username)
    logging.info('  Time: %s', datetime.datetime.now())

def settings_access_error(keycard_value):
    ''' This function writes failed settings access attempt information to the log '''
    logging.error(' ')
    logging.error('Settings Access Fail:')
    logging.error('  Keycard Value: %s', keycard_value)
    logging.error('  Time: %s', datetime.datetime.now())

def result(lane, width, height, frames):
    ''' This adds a row result to CSV file '''
    row = [str(datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S'))]
    row.append(str(lane + 1))
    row.append(str(int(width / config.WIDTH_RATIOS[lane])))
    row.append(str(int(height / config.HEIGHT_RATIOS[lane])))
    row.append(str(frames))

    with open('results.csv', 'ab') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)

    csvFile.close()

def shutdown():
    ''' This function writes the shutdown information to the log '''
    logging.info(' ')
    logging.info('End: %s', str(datetime.datetime.now()))
    logging.info(' ')

def stats_error(lane, current_rect, rects_arr, exception):
    ''' This function writes any errors with the stats to the log '''
    logging.error(' ')
    logging.error('Stats Error:')
    logging.error('  Time: %s', datetime.datetime.now())
    logging.error('  Lane: %s', str(lane))
    logging.error('  current_rect: %s', str(current_rect))
    logging.error('  rects_arr: %s', str(rects_arr))
    logging.error('  Exception: %s', str(exception))

def lane_error(lane, contours, exception):
    ''' This function writes any errors with the lane to the log '''
    logging.error(' ')
    logging.error('Lane Error:')
    logging.error('  Time: %s', datetime.datetime.now())
    logging.error('  Lane: %s', str(lane))
    logging.error('  Contours: %s', str(contours))
    logging.error('  Exception: %s', str(exception))