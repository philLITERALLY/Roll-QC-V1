'''This program performs Quality Control on Sub Rolls'''

# External Libraries
import sys
import cv2
import datetime
import fileinput

# My Modules
import info_logger
import config
import get_logins
import camera_setup
import running_window
import lane_handling
import program_state

# Set if program is in admin mode
program_state.set_admin_user('True')
if len(sys.argv) > 1:
    program_state.set_admin_user(sys.argv[1])

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

for i in range(config.LANE_COUNT):
    LANE_PASS.append(0)
    LANE_FAIL.append(0)
    PASS_COUNTS.append(0)
    FAIL_COUNTS.append(0)

app = running_window.RunningWindow()
app.start()

while RUNONCE:
    reload(config)

    # Take each FRAME
    _, FRAME = CAPTURE.read()

    CROPPED = FRAME[config.FRAME_HEIGHT_START:config.FRAME_HEIGHT_END, config.FRAME_WIDTH_START:config.FRAME_WIDTH_END]
    GRAY = cv2.cvtColor(CROPPED, cv2.COLOR_BGR2GRAY)
    _, THRESHOLD_IMG = cv2.threshold(GRAY, config.WHITE_THRESH, 255, 0)

    # Running Mode
    running_statement = (lane for lane in range(config.LANE_COUNT) if program_state.RUN_MODE)
    for lane in running_statement:
        lane_handling.running(lane, CROPPED, THRESHOLD_IMG, WIDTHS_ARR, HEIGHTS_ARR, FAIL_COUNTS, PASS_COUNTS, LANE_FAIL, LANE_PASS)

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
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow(window_name, CROPPED)

    # write the frame
    if 'record' in config.DEV_MODE:
        OUT.write(CROPPED)

    # RUNONCE = 0

    k = cv2.waitKey(1) & 0xFF
    if k == 13:
        username = ''
        
        # Loop through users to find keycard value
        for user in LOGINS:
            if user[0] == KEYCARD_VALUE:
                username = user[1]

        # If keycard value exists and user found
        if username != '':
            info_logger.logout(KEYCARD_VALUE, username)
            break
        else:
            info_logger.logout_error(KEYCARD_VALUE)

        KEYCARD_VALUE = ''
    elif k != 255 and k != 27:
        KEYCARD_VALUE += chr(k)

    if program_state.STOP_PROGRAM == True:
        break

# Release everything if job is finished
CAPTURE.release()

if 'record' in config.DEV_MODE:
    OUT.release()

cv2.destroyAllWindows()
app.root.destroy()
