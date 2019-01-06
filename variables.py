'''This module contains any variables required for the program to run'''

# My modules
import config

CAMERA_VARIABLES = [
    'CAP_PROP_POS_MSEC',
    'CAP_PROP_POS_FRAMES',
    'CAP_PROP_POS_AVI_RATIO',
    'CAP_PROP_FRAME_WIDTH',
    'CAP_PROP_FRAME_HEIGHT',
    'CAP_PROP_FPS',
    'CAP_PROP_FOURCC',
    'CAP_PROP_FRAME_COUNT',
    'CAP_PROP_FORMAT',
    'CAP_PROP_MODE',
    'CAP_PROP_BRIGHTNESS',
    'CAP_PROP_CONTRAST',
    'CAP_PROP_SATURATION',
    'CAP_PROP_HUE',
    'CAP_PROP_GAIN',
    'CAP_PROP_EXPOSURE',
    'CAP_PROP_CONVERT_RGB',
    'CAP_PROP_WHITE_BALANCE',
    'CAP_PROP_RECTIFICATION',
]

IO_RUNNING = 256 # Output 8 set high
IO_LANE1_REQUEST = 768 # Outputs 8 and 9 set high
IO_LANE2_REQUEST = 1280 # Outputs 8 and 10 set high
IO_LANE3_REQUEST = 2304 # Outputs 8 and 11 set high
IO_REQUEST = [IO_LANE1_REQUEST, IO_LANE2_REQUEST, IO_LANE3_REQUEST]
IO_LANE1_ACK = 1 # Input 0 set high
IO_LANE2_ACK = 2 # Input 1 set high
IO_LANE3_ACK = 4 # Input 2 set high
IO_ACK = [IO_LANE1_ACK, IO_LANE2_ACK, IO_LANE3_ACK]

# Changes IO array to value
def CALCULATE_IO_VALUE(VALUES):
    returnVal = VALUES[:]

    # reverse array
    returnVal.reverse()
    # turn array into string
    returnVal = ''.join(map(str, returnVal))

    # return binary string converted to decimal
    return int(returnVal, 2)

# Changes value IO array
def CALCULATE_FROM_IO_VALUE(VALUE):
    VALUE = '{0:#b}'.format(VALUE)

    # reverse binary
    VALUE[::-1]

    # return binary string converted to decimal
    print(VALUE)

def is_pass(lane, width, height):
    if width < config.LANE_FAIL_WIDTHS_LOW[lane] or \
       width > config.LANE_FAIL_WIDTHS_HIGH[lane] or \
       height < config.LANE_FAIL_HEIGHTS_LOW[lane] or \
       height > config.LANE_FAIL_HEIGHTS_HIGH[lane]:
        return False
    else:
        return True