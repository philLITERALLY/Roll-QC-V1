"""This module contains any configuration variables required for the program to run"""

# Camera Settings
CAM_WIDTH = 1920
CAM_HEIGHT = 1080
CAM_FPS = 30

# Size Settings
ACTUAL_WIDTH = 355  # mm
ACTUAL_HEIGHT = 28  # mm
PIXEL_WIDTH = 474
PIXEL_HEIGHT = 45.2
WIDTH_RATIO = ACTUAL_WIDTH / PIXEL_WIDTH
HEIGHT_RATIO = ACTUAL_HEIGHT / PIXEL_HEIGHT


def dimension_calc(width, height):
    """This function takes the pixel width and using the defined ratios converts to mm"""
    converted_width = int(width * WIDTH_RATIO)
    converted_height = int(height * HEIGHT_RATIO)
    return "{0}mm x {1}mm".format(converted_width, converted_height)
