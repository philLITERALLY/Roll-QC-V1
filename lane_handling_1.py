'''This module handles the each lane'''

# External Libraries
import cv2      # OpenCV

# My Modules
import config
import contour_handling
import program_state

TEXT_Y = config.LANE_HEIGHT_END - config.EDGE_GAP + 30

def running(lane, THRESHOLD_IMG, CONTOURS):
    # run opencv find contours, only external boxes
    _, CONTOURS, _ = cv2.findContours(THRESHOLD_IMG, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    CONTOURS = [cnt for cnt in CONTOURS if cv2.contourArea(cnt) > config.MIN_AREA]

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