"""This program performs Quality Control on Sub Rolls"""

# External Libraries
import csv
import cv2

# My Modules
import camera_setup
import info_logger
import config

# Load login info
LOGINS = []
with open('logins.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        LOGINS.append([row['card_number'], row['user_name']])

# Get camera stream
CAPTURE = camera_setup.main()

# Setup cropped image width
CAM_WIDTH_MIDPOINT = config.CAM_WIDTH / 2
HALF_FRAME_WIDTH = config.FRAME_WIDTH / 2
FRAME_WIDTH_START = CAM_WIDTH_MIDPOINT - HALF_FRAME_WIDTH
FRAME_WIDTH_END = CAM_WIDTH_MIDPOINT + HALF_FRAME_WIDTH

# Setup cropped image height
CAM_HEIGHT_MIDPOINT = config.CAM_HEIGHT / 2
HALF_FRAME_HEIGHT = config.FRAME_HEIGHT / 2
FRAME_HEIGHT_START = CAM_HEIGHT_MIDPOINT - HALF_FRAME_HEIGHT
FRAME_HEIGHT_END = CAM_HEIGHT_MIDPOINT + HALF_FRAME_HEIGHT

# Setup bounding box
LANE_X1 = config.LANE_WIDTH_START[0] - 10
LANE_Y1 = config.LANE_HEIGHT_START[0] + config.EDGE_GAP
LANE_X2 = config.LANE_WIDTH_END[config.LANE_COUNT - 1] + 10
LANE_Y2 = config.LANE_HEIGHT_END[0] - config.EDGE_GAP
SPLIT_X1 = config.LANE_WIDTH_START[1]
SPLIT_X2 = config.LANE_WIDTH_END[1]

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
PASS_COUNTS = []
FAIL_COUNTS = []

for i in range(config.LANE_COUNT):
    PASS_COUNTS.append(0)
    FAIL_COUNTS.append(0)

info_logger.results_header()

while RUNONCE:
    # Take each FRAME
    _, FRAME = CAPTURE.read()

    CROPPED = FRAME[FRAME_HEIGHT_START:FRAME_HEIGHT_END, FRAME_WIDTH_START:FRAME_WIDTH_END]
    GRAY = cv2.cvtColor(CROPPED, cv2.COLOR_BGR2GRAY)
    _, THRESHOLD_IMG = cv2.threshold(GRAY, config.WHITE_THRESH, 255, 0)

    for i in range(config.LANE_COUNT):
        # If no array exists to gather size info create
        if len(WIDTHS_ARR) <= i or len(WIDTHS_ARR) <= i:
            WIDTHS_ARR.append([])
            HEIGHTS_ARR.append([])

        ORIG_LANE_IMG = CROPPED[config.LANE_HEIGHT_START[i]:config.LANE_HEIGHT_END[i], config.LANE_WIDTH_START[i]:config.LANE_WIDTH_END[i]]
        THRESH_LANE_IMG = THRESHOLD_IMG[config.LANE_HEIGHT_START[i]:config.LANE_HEIGHT_END[i], config.LANE_WIDTH_START[i]:config.LANE_WIDTH_END[i]]

        if 'thresh' in config.DEV_MODE:
            cv2.imshow('THRESH' + str(i), THRESH_LANE_IMG)
        
        # run opencv find contours, only external boxes
        _, CONTOURS, _ = cv2.findContours(THRESH_LANE_IMG, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        CONTOURS = [cnt for cnt in CONTOURS if cv2.contourArea(cnt) > config.MIN_AREA]

        # for each contour draw a bounding box and dimensions
        for cnt in CONTOURS:
            x, y, w, h = cv2.boundingRect(cnt)
            color = config.GREEN

            leading_edge = y + h
            exiting_box = config.LANE_HEIGHT - config.EDGE_GAP

            # If blob deteced within our scan section
            if y > config.EDGE_GAP and leading_edge < exiting_box :
                WIDTHS_ARR[i].append(w)
                HEIGHTS_ARR[i].append(h)

                pixel_dimensions = "{0}px x {1}px".format(w, h)
                calc_dimensions = config.dimension_calc(i, w, h)

                if w < config.LANE_FAIL_WIDTHS_LOW[i] or \
                    w > config.LANE_FAIL_WIDTHS_HIGH[i] or \
                    h < config.LANE_FAIL_HEIGHTS_LOW[i] or \
                    h > config.LANE_FAIL_HEIGHTS_HIGH[i]:
                    color = config.RED

                cv2.rectangle(ORIG_LANE_IMG, (x, y), (x+w, y+h), color, 2)
                cv2.putText(ORIG_LANE_IMG, calc_dimensions, (x, y), config.FONT, 1, color, 2)

                if 'pixels' in config.DEV_MODE:
                    cv2.putText(ORIG_LANE_IMG, pixel_dimensions, (x, y + h), config.FONT, 1, config.BLUE, 2)

            # If blob is leaving scan section we average sizes and determine pass/fail
            elif leading_edge > exiting_box and (WIDTHS_ARR[i] or HEIGHTS_ARR[i]):
                cv2.rectangle(ORIG_LANE_IMG, (x, y), (x+w, y+h), config.BLUE, 2)

                for lane in range(config.LANE_COUNT):
                    average_width = 0
                    average_height = 0

                    if len(WIDTHS_ARR[lane]) > 0:
                        average_width = sum(WIDTHS_ARR[lane]) / len(WIDTHS_ARR[lane])

                    if len(HEIGHTS_ARR[lane]) > 0:
                        average_height = sum(HEIGHTS_ARR[lane]) / len(HEIGHTS_ARR[lane])

                    if average_width < config.LANE_FAIL_WIDTHS_LOW[lane] or \
                        average_width > config.LANE_FAIL_WIDTHS_HIGH[lane] or \
                        average_height < config.LANE_FAIL_HEIGHTS_LOW[lane] or \
                        average_height > config.LANE_FAIL_HEIGHTS_HIGH[lane]:
                        FAIL_COUNTS[lane] += 1
                    else:
                        PASS_COUNTS[lane] += 1
                
                info_logger.result(PASS_COUNTS, FAIL_COUNTS)
                with open('results.csv','a') as fd:
                    fd.write(myCsvRow)

                # Reset arrays
                WIDTHS_ARR[i] = []
                HEIGHTS_ARR[i] = []

    # Show Lane Boundaries
    cv2.rectangle(CROPPED, (LANE_X1, LANE_Y1), (LANE_X2, LANE_Y2), config.YELLOW, 2)
    cv2.rectangle(CROPPED, (SPLIT_X1, LANE_Y1), (SPLIT_X2, LANE_Y2), config.YELLOW, 2)

    # Show Pass Fail Rate for each
    for i in range(config.LANE_COUNT):
        cv2.putText(CROPPED, "PASS: " + str(PASS_COUNTS[i]) + " FAIL: " + str(FAIL_COUNTS[i]), (config.PASS_FAIL_X[i], LANE_Y2 + 30), config.FONT, 1, config.BLUE, 2)

    # Resize and show image
    cv2.imshow('CROPPED', cv2.resize(CROPPED, (1280, 960)))

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

# Release everything if job is finished
CAPTURE.release()

if 'record' in config.DEV_MODE:
    OUT.release()

cv2.destroyAllWindows()
