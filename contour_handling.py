'''This module handles the contours'''

# External Libraries
import cv2      # OpenCV
import time

# AIO DLL
import clr
AIO_DLL = clr.AddReference(R'C:\Users\Public\Documents\ACCES\PCIe-IDIO-24\Win32\C#\bin\Release\AIOWDMNet.dll')
from AIOWDMNet import AIOWDM # pylint: disable=E0401
AIO_INSTANCE = AIOWDM()

# My Modules
import config
import info_logger
import variables

def running(lane, contour, WIDTHS_ARR, HEIGHTS_ARR, ORIG_LANE_IMG, FAIL_COUNTS, PASS_COUNTS, FAIL, PASS, AVG_WIDTHS, AVG_HEIGHTS):
    x, y, w, h = cv2.boundingRect(contour)
    color = config.GREEN

    leading_edge = y + h
    exiting_box = config.LANE_HEIGHT - config.EDGE_GAP
    
    # If blob deteced within our scan section
    if y > config.EDGE_GAP and leading_edge < exiting_box :
        WIDTHS_ARR[lane].append(w)
        HEIGHTS_ARR[lane].append(h)

        pixel_dimensions = '{0}px x {1}px'.format(w, h)
        calc_dimensions = config.dimension_calc(lane, w, h)

        if w < config.LANE_FAIL_WIDTHS_LOW[lane] or \
            w > config.LANE_FAIL_WIDTHS_HIGH[lane] or \
            h < config.LANE_FAIL_HEIGHTS_LOW[lane] or \
            h > config.LANE_FAIL_HEIGHTS_HIGH[lane]:
            color = config.RED

        cv2.rectangle(ORIG_LANE_IMG, (x, y), (x+w, y+h), color, 2)
        cv2.putText(ORIG_LANE_IMG, calc_dimensions, (x, y), config.FONT, 1, color, 2)

        if 'pixels' in config.DEV_MODE:
            cv2.putText(ORIG_LANE_IMG, pixel_dimensions, (x, y + h), config.FONT, 1, config.BLUE, 2)

    # If blob is leaving scan section we average sizes and determine pass/fail
    elif leading_edge > exiting_box and (WIDTHS_ARR[lane] or HEIGHTS_ARR[lane]):
        cv2.rectangle(ORIG_LANE_IMG, (x, y), (x+w, y+h), config.BLUE, 2)

        for index in range(config.LANE_COUNT):
            average_width = 0
            average_height = 0

            if len(WIDTHS_ARR[index]) > 0:
                average_width = sum(WIDTHS_ARR[index]) / len(WIDTHS_ARR[index])
                AVG_WIDTHS[lane].append(average_width * config.WIDTH_RATIOS[lane])

            if len(HEIGHTS_ARR[index]) > 0:
                average_height = sum(HEIGHTS_ARR[index]) / len(HEIGHTS_ARR[index])
                AVG_HEIGHTS[lane].append(average_height * config.HEIGHT_RATIOS[lane])

            if average_width < config.LANE_FAIL_WIDTHS_LOW[index] or \
                average_width > config.LANE_FAIL_WIDTHS_HIGH[index] or \
                average_height < config.LANE_FAIL_HEIGHTS_LOW[index] or \
                average_height > config.LANE_FAIL_HEIGHTS_HIGH[index]:
                FAIL_COUNTS[index] += 1
                FAIL[index] = 1
                PASS[index] = 0
            else:
                PASS_COUNTS[index] += 1
                PASS[index] = 1
                FAIL[index] = 0
               
        # Request ACK from PLC
        AIO_INSTANCE.RelOutPort(0, 0, variables.IO_REQUEST)

        # Create output for IO
        OUTPUT = []
        for i in range(config.LANE_COUNT):
            OUTPUT.append(PASS[i])
            OUTPUT.append(FAIL[i])

        # Wait for ACK from PLC
        while AIO_INSTANCE.RelInPort(0, 4) != variables.IO_ACK:
            pass

        AIO_INSTANCE.RelOutPort(0, 0, variables.CALCULATE_IO_VALUE(OUTPUT))        

        info_logger.result(PASS, FAIL)

        # Reset arrays
        WIDTHS_ARR[lane] = []
        HEIGHTS_ARR[lane] = []

def calibrate(lane, contour, ORIG_LANE_IMG, request_calibrate, CALIB_WIDTHS, CALIB_HEIGHTS):
    x, y, w, h = cv2.boundingRect(contour)
    color = config.BLUE

    leading_edge = y + h
    exiting_box = config.LANE_HEIGHT - config.EDGE_GAP
    
    # If blob deteced within our scan section
    if y > config.EDGE_GAP and leading_edge < exiting_box :
        pixel_dimensions = '{0}px x {1}px'.format(w, h)
        calc_dimensions = config.dimension_calc(lane, w, h)

        cv2.rectangle(ORIG_LANE_IMG, (x, y), (x+w, y+h), color, 2)
        cv2.putText(ORIG_LANE_IMG, calc_dimensions, (x, y), config.FONT, 1, color, 2)

        cv2.putText(ORIG_LANE_IMG, pixel_dimensions, (x, y + h), config.FONT, 1, config.BLUE, 2)
       
        if request_calibrate:
            CALIB_WIDTHS[lane] = float(w)
            CALIB_HEIGHTS[lane] = float(h)