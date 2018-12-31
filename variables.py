'''This module contains any variables required for the program to run'''

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
IO_REQUEST = 1280 # Outputs 8 and 10 set high
IO_ACK = 1 # Input 1 set high

# Changes IO array to value
def CALCULATE_IO_VALUE(VALUES):
    # reverse array
    VALUES.reverse()
    # turn array into string
    VALUES = ''.join(map(str, VALUES))

    # return binary string converted to decimal
    return int(VALUES, 2)

# Changes value IO array
def CALCULATE_FROM_IO_VALUE(VALUE):
    VALUE = "{0:#b}".format(VALUE)
    
    # reverse binary
    VALUE[::-1]

    # return binary string converted to decimal
    print(VALUE)