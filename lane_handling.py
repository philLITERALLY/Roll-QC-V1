"""This module handles the each lane"""

# External Libraries
import cv2      # OpenCV

# My Modules
import config
import contour_handling

TEXT_Y = config.LANE_HEIGHT_END[0] - config.EDGE_GAP + 30

def main(lane, CROPPED, THRESHOLD_IMG, WIDTHS_ARR, HEIGHTS_ARR, FAIL_COUNTS, PASS_COUNTS, LANE_FAIL, LANE_PASS):
    # If no array exists to gather size info create
    if len(WIDTHS_ARR) <= lane or len(WIDTHS_ARR) <= lane:
        WIDTHS_ARR.append([])
        HEIGHTS_ARR.append([])

    ORIG_LANE_IMG = CROPPED[config.LANE_HEIGHT_START[lane]:config.LANE_HEIGHT_END[lane], config.LANE_WIDTH_START[lane]:config.LANE_WIDTH_END[lane]]
    THRESH_LANE_IMG = THRESHOLD_IMG[config.LANE_HEIGHT_START[lane]:config.LANE_HEIGHT_END[lane], config.LANE_WIDTH_START[lane]:config.LANE_WIDTH_END[lane]]

    if 'thresh' in config.DEV_MODE:
        cv2.imshow('THRESH' + str(lane), THRESH_LANE_IMG)
    
    # run opencv find contours, only external boxes
    _, CONTOURS, _ = cv2.findContours(THRESH_LANE_IMG, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    CONTOURS = [cnt for cnt in CONTOURS if cv2.contourArea(cnt) > config.MIN_AREA]

    # for each contour draw a bounding box and dimensions
    for contour in CONTOURS:
        contour_handling.main(lane, contour, WIDTHS_ARR, HEIGHTS_ARR, ORIG_LANE_IMG, FAIL_COUNTS, PASS_COUNTS, LANE_FAIL, LANE_PASS)
    
    # Show Pass Fail Rate for each
    cv2.putText(CROPPED, "PASS: " + str(PASS_COUNTS[lane]) + " FAIL: " + str(FAIL_COUNTS[lane]), (config.PASS_FAIL_X[lane], TEXT_Y), config.FONT, 1, config.BLUE, 2)
