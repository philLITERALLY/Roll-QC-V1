'''This module handles the each lane'''

# External Libraries
import cv2      # OpenCV

# My Modules
import config
import contour_handling
import program_state

TEXT_Y = config.LANE_HEIGHT_END - config.EDGE_GAP + 30

def running(lane, CROPPED, THRESHOLD_IMG, WIDTHS_ARR, HEIGHTS_ARR, FAIL_COUNTS, PASS_COUNTS, LANE_FAIL, LANE_PASS, AVG_WIDTHS, AVG_HEIGHTS):
    # If no array exists to gather size info create
    if len(WIDTHS_ARR) <= lane or len(WIDTHS_ARR) <= lane:
        WIDTHS_ARR.append([])
        HEIGHTS_ARR.append([])

    ORIG_LANE_IMG = CROPPED[config.LANE_HEIGHT_START:config.LANE_HEIGHT_END, config.LANE_WIDTH_START[lane]:config.LANE_WIDTH_END[lane]]
    THRESH_LANE_IMG = THRESHOLD_IMG[config.LANE_HEIGHT_START:config.LANE_HEIGHT_END, config.LANE_WIDTH_START[lane]:config.LANE_WIDTH_END[lane]]
    
    # run opencv find contours, only external boxes
    _, CONTOURS, _ = cv2.findContours(THRESH_LANE_IMG, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    CONTOURS = [cnt for cnt in CONTOURS if cv2.contourArea(cnt) > config.MIN_AREA]

    # for each contour draw a bounding box and dimensions
    for contour in CONTOURS:
        contour_handling.running(lane, contour, WIDTHS_ARR, HEIGHTS_ARR, ORIG_LANE_IMG, FAIL_COUNTS, PASS_COUNTS, LANE_FAIL, LANE_PASS, AVG_WIDTHS, AVG_HEIGHTS)

    # Show Pass Fail Rate for each	
    for i in range(config.LANE_COUNT):        
        PASS_TEXT = 'PASS: ' + str(PASS_COUNTS[i])
        FAIL_TEXT = 'FAIL: ' + str(FAIL_COUNTS[i])

        AVG_TEXT = 'AVG: 0%'
        if PASS_COUNTS[i] > 0:
            AVG_TEXT = 'AVG: ' + str(100 * PASS_COUNTS[i] / (PASS_COUNTS[i] + FAIL_COUNTS[i])) + '%'

        AVG_WIDTHS_TEXT = ''
        if len(AVG_WIDTHS[i]) > 0:
            AVG_WIDTH = int(sum(AVG_WIDTHS[i]) / float(len(AVG_WIDTHS[i])))
            AVG_WIDTHS_TEXT = 'AVG WIDTH: ' + str(AVG_WIDTH) + 'mm'

        AVG_HEIGHTS_TEXT = ''
        if len(AVG_HEIGHTS[i]) > 0:
            AVG_HEIGHT = int(sum(AVG_HEIGHTS[i]) / float(len(AVG_HEIGHTS[i])))
            AVG_HEIGHTS_TEXT = 'AVG HEIGHT: ' + str(AVG_HEIGHT) + 'mm'

        cv2.putText(CROPPED, PASS_TEXT, (config.PASS_FAIL_X[i], TEXT_Y), config.FONT, 1, config.WHITE, 2)
        cv2.putText(CROPPED, FAIL_TEXT, (config.PASS_FAIL_X[i], TEXT_Y + 30), config.FONT, 1, config.WHITE, 2)
        cv2.putText(CROPPED, AVG_TEXT, (config.PASS_FAIL_X[i], TEXT_Y + 60), config.FONT, 1, config.WHITE, 2)
        cv2.putText(CROPPED, AVG_WIDTHS_TEXT, (config.PASS_FAIL_X[i], TEXT_Y + 90), config.FONT, 1, config.WHITE, 2)
        cv2.putText(CROPPED, AVG_HEIGHTS_TEXT, (config.PASS_FAIL_X[i], TEXT_Y + 120), config.FONT, 1, config.WHITE, 2)

def calibrate(lane, CROPPED, THRESHOLD_IMG, request_calibrate, CALIB_WIDTHS, CALIB_HEIGHTS):
    # If no array exists to gather size info create
    if len(CALIB_WIDTHS) <= lane or len(CALIB_HEIGHTS) <= lane:
        CALIB_WIDTHS.append(1.0)
        CALIB_HEIGHTS.append(1.0)
        
    ORIG_LANE_IMG = CROPPED[config.LANE_HEIGHT_START:config.LANE_HEIGHT_END, config.LANE_WIDTH_START[lane]:config.LANE_WIDTH_END[lane]]
    THRESH_LANE_IMG = THRESHOLD_IMG[config.LANE_HEIGHT_START:config.LANE_HEIGHT_END, config.LANE_WIDTH_START[lane]:config.LANE_WIDTH_END[lane]]

    if program_state.THRESH_MODE:
        window_name = 'THRESH' + str(lane)
        cv2.namedWindow(window_name)
        cv2.moveWindow(window_name, config.LANE_WIDTH_START[lane] - 68, 500)
        cv2.imshow('THRESH' + str(lane), THRESH_LANE_IMG)
    
    # run opencv find contours, only external boxes
    _, CONTOURS, _ = cv2.findContours(THRESH_LANE_IMG, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    CONTOURS = [cnt for cnt in CONTOURS if cv2.contourArea(cnt) > config.MIN_AREA]

    # for each contour draw a bounding box and dimensions
    for contour in CONTOURS:
        contour_handling.calibrate(lane, contour, ORIG_LANE_IMG, request_calibrate, CALIB_WIDTHS, CALIB_HEIGHTS)