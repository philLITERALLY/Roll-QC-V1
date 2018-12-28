"""This program performs Quality Control on Sub Rolls"""

# External Libraries
import cv2
import datetime

# My Modules
import info_logger
import config
import get_logins
import camera_setup
import running_window
import lane_handling
import program_state

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
    # Take each FRAME
    _, FRAME = CAPTURE.read()

    CROPPED = FRAME[config.FRAME_HEIGHT_START:config.FRAME_HEIGHT_END, config.FRAME_WIDTH_START:config.FRAME_WIDTH_END]
    GRAY = cv2.cvtColor(CROPPED, cv2.COLOR_BGR2GRAY)
    _, THRESHOLD_IMG = cv2.threshold(GRAY, config.WHITE_THRESH, 255, 0)

    for_statement = (lane for lane in range(config.LANE_COUNT) if program_state.RUN_MODE)
    for lane in for_statement:
        lane_handling.main(lane, CROPPED, THRESHOLD_IMG, WIDTHS_ARR, HEIGHTS_ARR, FAIL_COUNTS, PASS_COUNTS, LANE_FAIL, LANE_PASS)

    # Show Lane Boundaries
    cv2.rectangle(CROPPED, (config.LANE_X1, config.LANE_Y1), (config.LANE_X2, config.LANE_Y2), config.YELLOW, 2)
    cv2.rectangle(CROPPED, (config.SPLIT_X1, config.LANE_Y1), (config.SPLIT_X2, config.LANE_Y2), config.YELLOW, 2)

    # Resize and show image
    cv2.imshow('LINE VIEW', cv2.resize(CROPPED, (1280, 960)))

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
