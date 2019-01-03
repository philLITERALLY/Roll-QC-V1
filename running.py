'''This program performs Quality Control on Sub Rolls'''

# External Libraries
import sys
import cv2
import datetime
import fileinput
import time
import os

# My Modules
import info_logger
import config
import get_logins
import camera_setup
import running_window
import lane_handling
import program_state
import variables

# AIO DLL
import clr
AIO_DLL = clr.AddReference(R'C:\Users\User\Roll-QC-V1\AIOWDMNet.dll')
from AIOWDMNet import AIOWDM # pylint: disable=E0401
AIO_INSTANCE = AIOWDM()

# Reset AIO to empty
AIO_INSTANCE.RelOutPort(0, 0, 0)

RUN_MODE = program_state.RUN_MODE
STOP_PROGRAM = program_state.STOP_PROGRAM

# Load login info
LOGINS = get_logins.main()

# Get camera stream
CAPTURE = camera_setup.main()

# Define the codec and create VideoWriter object
if 'record' in config.DEV_MODE:
    FOURCC = cv2.VideoWriter_fourcc(*'MJPG')
    OUT = cv2.VideoWriter('output.avi', FOURCC, 10.0, (1440, 1080))

RUNONCE = 1

# Create a list of lists for each lane. Will hold each frames dimensions to calculate average
WIDTHS_ARR = []
HEIGHTS_ARR = []
CALIB_WIDTHS = []
CALIB_HEIGHTS = []

# Create Keycard String
KEYCARD_VALUE = ''

# Create Pass/Fail Counts
LANE_PASS = []
LANE_FAIL = []
PASS_COUNTS = []
FAIL_COUNTS = []
AVG_WIDTHS = []
AVG_HEIGHTS = []

for i in range(config.LANE_COUNT):
    LANE_PASS.append(0)
    LANE_FAIL.append(0)
    PASS_COUNTS.append(0)
    FAIL_COUNTS.append(0)
    AVG_WIDTHS.append([])
    AVG_HEIGHTS.append([])

app = running_window.RunningWindow()
app.start()

while True:
    if program_state.RUN_MODE:
        # Set AIO to running (high on 8)
        AIO_INSTANCE.RelOutPort(0, 0, variables.IO_RUNNING)
    elif program_state.CALIBRATE_MODE:
        # Set AIO to empty
        AIO_INSTANCE.RelOutPort(0, 0, 0)

    # Reload any config changes
    reload(config)

    if not program_state.RUN_MODE:
        LANE_PASS = []
        LANE_FAIL = []
        PASS_COUNTS = []
        FAIL_COUNTS = []
        AVG_WIDTHS = []
        AVG_HEIGHTS = []

        for i in range(config.LANE_COUNT):
            LANE_PASS.append(0)
            LANE_FAIL.append(0)
            PASS_COUNTS.append(0)
            FAIL_COUNTS.append(0)
            AVG_WIDTHS.append([])
            AVG_HEIGHTS.append([])

    # Take each FRAME
    _, FRAME = CAPTURE.read()

    CROPPED = FRAME[config.FRAME_HEIGHT_START:config.FRAME_HEIGHT_END, config.FRAME_WIDTH_START:config.FRAME_WIDTH_END]
    GRAY = cv2.cvtColor(CROPPED, cv2.COLOR_BGR2GRAY)
    _, THRESHOLD_IMG = cv2.threshold(GRAY, config.WHITE_THRESH, 255, 0)

    # Running Mode
    running_statement = (lane for lane in range(config.LANE_COUNT) if program_state.RUN_MODE)
    for lane in running_statement:
        lane_handling.running(lane, CROPPED, THRESHOLD_IMG, WIDTHS_ARR, HEIGHTS_ARR, FAIL_COUNTS, PASS_COUNTS, LANE_FAIL, LANE_PASS, AVG_WIDTHS, AVG_HEIGHTS)

    # Calibrate Mode
    calibrate_statement = (lane for lane in range(config.LANE_COUNT) if program_state.CALIBRATE_MODE)
    for lane in calibrate_statement:
        lane_handling.calibrate(lane, CROPPED, THRESHOLD_IMG, program_state.REQUEST_CALIBRATE, CALIB_WIDTHS, CALIB_HEIGHTS)

    if program_state.REQUEST_CALIBRATE:
        lines = open('config.py', 'r').readlines()
        lines[6] = 'PIXEL_WIDTHS = ' + str(CALIB_WIDTHS) + ' # px\n'
        lines[7] = 'PIXEL_HEIGHTS = ' + str(CALIB_HEIGHTS) + ' # px\n'
        out = open('config.py', 'w')
        out.writelines(lines)
        out.close()

        program_state.request_calibration(False)
        CALIB_WIDTHS = []
        CALIB_HEIGHTS = []

    # Show Lane Boundaries
    cv2.rectangle(CROPPED, (config.LANE_X1, config.LANE_Y1), (config.LANE_X2, config.LANE_Y2), config.YELLOW, 2)
    cv2.rectangle(CROPPED, (config.SPLIT_X1, config.LANE_Y1), (config.SPLIT_X2, config.LANE_Y2), config.YELLOW, 2)

    # get the size of the screen
    width, height = 1280, 1024
    window_name = 'LINE VIEW'
    if program_state.THRESH_MODE:
        cv2.destroyWindow(window_name)
    else:
        cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow(window_name, CROPPED)

    # write the frame
    if 'record' in config.DEV_MODE:
        OUT.write(CROPPED)

    # Required for loop no need for key read
    k = cv2.waitKey(1) & 0xFF

    if program_state.STOP_PROGRAM == True:
        break

# Release everything if job is finished
CAPTURE.release()

# Reset AIO to empty
AIO_INSTANCE.RelOutPort(0, 0, 0)

if 'record' in config.DEV_MODE:
    OUT.release()

cv2.destroyAllWindows()
app.root.destroy()
