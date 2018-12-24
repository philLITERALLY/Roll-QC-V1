"""This module contains any configuration variables required for the program to run"""

# External Libraries
import cv2

# Camera Settings
CAM_WIDTH = 1920
CAM_HEIGHT = 1080
CAM_FPS = 30
FRAME_WIDTH = 1440
FRAME_HEIGHT = 1080

# Lane Settings
LANE_COUNT = 3
LANE_WIDTH = 480
LANE_HEIGHT = 200
LANE_WIDTH_START = [0, 480, 960] # Creating manually for now
LANE_WIDTH_END = [480, 960, 1440]
LANE_HEIGHT_START = [460, 460, 460]
LANE_HEIGHT_END = [650, 650, 650]
EDGE_GAP = 40 # How far roll has to be in to count

# Size Settings - Calibration Settings
ACTUAL_WIDTH = 265.0  # mm
ACTUAL_HEIGHT = 33.0  # mm
PIXEL_WIDTH = 345.0
PIXEL_HEIGHT = 50.0
WIDTH_RATIO = ACTUAL_WIDTH / PIXEL_WIDTH
HEIGHT_RATIO = ACTUAL_HEIGHT / PIXEL_HEIGHT

# Draw Settings
FONT = cv2.FONT_HERSHEY_SIMPLEX
GREEN = (0, 255, 0)
RED = (0, 0, 255)
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)

# Threshold Settings
WHITE_THRESH = 190
MIN_AREA = 2000 # Pixels
FAIL_WIDTH_LOW = 260.0 / WIDTH_RATIO # mm / ratio
FAIL_WIDTH_HIGH = 300.0 / WIDTH_RATIO # mm / ratio
FAIL_HEIGHT_LOW = 20.0 / HEIGHT_RATIO # mm
FAIL_HEIGHT_HIGH = 38.0 / HEIGHT_RATIO # mm

def dimension_calc(width, height):
    """This function takes the pixel width and using the defined ratios converts to mm"""
    converted_width = int(width * WIDTH_RATIO)
    converted_height = int(height * HEIGHT_RATIO)
    return "{0}mm x {1}mm".format(converted_width, converted_height)
