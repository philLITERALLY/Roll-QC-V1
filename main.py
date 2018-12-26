"""This program performs Quality Control on Sub Rolls"""

# External Libraries
import cv2

# My Modules
import camera_setup
import info_logger
import config

# Create new log with date time
info_logger.init()

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
PASS_COUNT = []
FAIL_COUNT = []

for i in range(config.LANE_COUNT):
    PASS_COUNT.append(0)
    FAIL_COUNT.append(0)

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
                calc_dimensions = config.dimension_calc(w, h)

                if w < config.FAIL_WIDTH_LOW or w > config.FAIL_WIDTH_HIGH or h < config.FAIL_HEIGHT_LOW or h > config.FAIL_HEIGHT_HIGH:
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

                    if average_width < config.FAIL_WIDTH_LOW or \
                        average_width > config.FAIL_WIDTH_HIGH or \
                        average_height < config.FAIL_HEIGHT_LOW or \
                        average_height > config.FAIL_HEIGHT_HIGH:
                        FAIL_COUNT[lane] += 1
                    else:
                        PASS_COUNT[lane] += 1

                # Reset arrays
                WIDTHS_ARR[i] = []
                HEIGHTS_ARR[i] = []

    # Show Lane Boundaries
    cv2.rectangle(CROPPED, (LANE_X1, LANE_Y1), (LANE_X2, LANE_Y2), config.YELLOW, 2)
    cv2.rectangle(CROPPED, (SPLIT_X1, LANE_Y1), (SPLIT_X2, LANE_Y2), config.YELLOW, 2)

    # Show Pass Fail Rate for each
    for i in range(config.LANE_COUNT):
        cv2.putText(CROPPED, "PASS: " + str(PASS_COUNT[i]) + " FAIL: " + str(FAIL_COUNT[i]), (config.PASS_FAIL_X[i], LANE_Y2 + 30), config.FONT, 1, config.BLUE, 2)

    # Resize and show image
    cv2.imshow('CROPPED', cv2.resize(CROPPED, (1280, 960)))

    # write the frame
    if 'record' in config.DEV_MODE:
        OUT.write(CROPPED)

    # RUNONCE = 0

    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break
    elif k == 13:
        print("Keycard Value: " + KEYCARD_VALUE)
        break
    elif k != 255:
        KEYCARD_VALUE += chr(k)

info_logger.shutdown()

# Release everything if job is finished
CAPTURE.release()

if 'record' in config.DEV_MODE:
    OUT.release()

cv2.destroyAllWindows()
