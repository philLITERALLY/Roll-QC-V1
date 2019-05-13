''' This module contains all functions and setup required for the programs logging '''

# External Libraries
import os
import logging
import datetime
import csv

# My Modules
import variables
import handle_config

my_path = os.path.abspath(os.path.dirname(__file__))

logging.basicConfig(filename='logging_' + datetime.datetime.now().strftime('%d-%m-%Y') + '.log', level=logging.DEBUG)


def init():
    ''' This function creates a new log with current date time '''
    logging.info('------')
    logging.info(' ')
    logging.info('Start: %s', str(datetime.datetime.now()))

def decode_fourcc(v):
  v = int(v)
  return "".join([chr((v >> 8 * i) & 0xFF) for i in range(4)])

def camera_settings(capture):
    ''' This function writes the camera settings to the log '''
    logging.debug(' ')
    logging.debug('Camera Settings: ')
    for camera_setting in range(len(variables.CAMERA_VARIABLES)):
        cam_var =  str(variables.CAMERA_VARIABLES[camera_setting])
        cam_setting = str(capture.get(camera_setting))
        decode_cam = ''

        if variables.CAMERA_VARIABLES[camera_setting] == 'CAP_PROP_FOURCC':
            decode_cam = ' (' + str(decode_fourcc(capture.get(camera_setting))) + ')'

        logging.debug('\t' + cam_var + ' - ' + cam_setting + decode_cam)

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

def result(lane, width, height):
    ''' This adds a row result to CSV file '''
    row = [str(datetime.datetime.now().strftime('%Y:%m:%d:%H:%M:%S'))]
    row.append(str(lane + 1))
    row.append(str(int(width * handle_config.WIDTH_RATIOS[lane])))
    row.append(str(int(height * handle_config.HEIGHT_RATIOS[lane])))
    row.append(str(int(width * height)))

    with open(R'C:/Users/User/Desktop/results.csv', 'ab') as csvFile:
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