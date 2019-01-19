from ConfigParser import ConfigParser
import ast

def getArray(config, section, variable):
    return ast.literal_eval(config.get(section, variable))

def setValue(section, variable, value):
    config.set(section, variable, str(value))   # Set new value
    with open(R'C:\Users\User\Documents\Low Cost Automation Ltd\config.ini', 'w') as configfile: # Save new value
        config.write(configfile)

def init():
    # Config File
    global config

    # Setup Camera Settings
    global CAM_WIDTH, CAM_HEIGHT, CAM_FPS

    # Setup Crop Settings
    global FRAME_WIDTH_START, FRAME_WIDTH_END
    global FRAME_HEIGHT_START, FRAME_HEIGHT_END

    # Calibration Values
    global WIDTH_RATIOS, HEIGHT_RATIOS
    global PIXEL_WIDTHS, PIXEL_HEIGHTS
    global ACTUAL_WIDTH, ACTUAL_HEIGHT

    # Thresh
    global MIN_AREA, WHITE_THRESH

    # Pass/Fail Settings
    global FAIL_WIDTH_LOW, FAIL_WIDTH_HIGH
    global FAIL_HEIGHT_LOW, FAIL_HEIGHT_HIGH
    global LANE_FAIL_WIDTHS_LOW, LANE_FAIL_WIDTHS_HIGH
    global LANE_FAIL_HEIGHTS_LOW, LANE_FAIL_HEIGHTS_HIGH

    # Lane Settings
    global LANE_COUNT
    global LANE_HEIGHT, EDGE_GAP
    global LANE_WIDTH_START, LANE_WIDTH_END
    global LANE_HEIGHT_START, LANE_HEIGHT_END

    # Draw Settings
    global FONT
    global GREEN, RED, YELLOW
    global PASS_FAIL_X, PASS_FAIL_Y
    global TEXT_Y

    # Bounding Box Settings
    global LANE_X1, LANE_Y1, LANE_X2, LANE_Y2, SPLIT_X1, SPLIT_X2

    # AIO Settings
    global AIO_WAIT

    # Load config file
    config = ConfigParser()
    config.read(R'C:\Users\User\Documents\Low Cost Automation Ltd\config.ini')

    # Get Camera Settings
    CAM_WIDTH = config.getint('CAMERA', 'CAM_WIDTH')
    CAM_HEIGHT = config.getint('CAMERA', 'CAM_HEIGHT')
    CAM_FPS = config.getint('CAMERA', 'CAM_FPS')
    FRAME_WIDTH = config.getint('CAMERA', 'FRAME_WIDTH')
    FRAME_HEIGHT = config.getint('CAMERA', 'FRAME_HEIGHT')

    # Get Calibration Settings
    ACTUAL_WIDTH = config.getfloat('CALIBRATION', 'ACTUAL_WIDTH')
    ACTUAL_HEIGHT = config.getfloat('CALIBRATION', 'ACTUAL_HEIGHT')
    PIXEL_WIDTHS = getArray(config, 'CALIBRATION', 'PIXEL_WIDTHS')
    PIXEL_HEIGHTS = getArray(config, 'CALIBRATION', 'PIXEL_HEIGHTS')

    HEIGHT_RATIOS, WIDTH_RATIOS = [], []
    for width in PIXEL_WIDTHS:
        WIDTH_RATIOS.append(ACTUAL_WIDTH / width)
    for height in PIXEL_HEIGHTS:
        HEIGHT_RATIOS.append(ACTUAL_HEIGHT / height)

    # Get Thresh Setting
    MIN_AREA = config.getint('THRESHOLD', 'MIN_AREA')
    WHITE_THRESH = config.getfloat('THRESHOLD', 'WHITE_THRESH')

    # Get Pass/Fail Settings
    FAIL_WIDTH_LOW = config.getfloat('THRESHOLD', 'FAIL_WIDTH_LOW')
    FAIL_WIDTH_HIGH = config.getfloat('THRESHOLD', 'FAIL_WIDTH_HIGH')
    FAIL_HEIGHT_LOW = config.getfloat('THRESHOLD', 'FAIL_HEIGHT_LOW')
    FAIL_HEIGHT_HIGH = config.getfloat('THRESHOLD', 'FAIL_HEIGHT_HIGH')

    # Setup Width Pass/Fail
    LANE_FAIL_WIDTHS_LOW, LANE_FAIL_WIDTHS_HIGH = [], []
    for ratio in WIDTH_RATIOS:
        LANE_FAIL_WIDTHS_LOW.append(FAIL_WIDTH_LOW / ratio)
    for ratio in WIDTH_RATIOS:
        LANE_FAIL_WIDTHS_HIGH.append(FAIL_WIDTH_HIGH / ratio)

    # Setup Height Pass/Fail
    LANE_FAIL_HEIGHTS_LOW, LANE_FAIL_HEIGHTS_HIGH = [], []
    for ratio in HEIGHT_RATIOS:
        LANE_FAIL_HEIGHTS_LOW.append(FAIL_HEIGHT_LOW / ratio)
    for ratio in HEIGHT_RATIOS:
        LANE_FAIL_HEIGHTS_HIGH.append(FAIL_HEIGHT_HIGH / ratio)

    # Get Lane Settings
    LANE_COUNT = config.getint('LANE', 'LANE_COUNT')
    LANE_HEIGHT = config.getint('LANE', 'LANE_HEIGHT')
    LANE_HEIGHT_END = config.getint('LANE', 'LANE_HEIGHT_END')
    EDGE_GAP = config.getint('LANE', 'EDGE_GAP')
    LANE_WIDTH_START = getArray(config, 'LANE', 'LANE_WIDTH_START')
    LANE_WIDTH_END = getArray(config, 'LANE', 'LANE_WIDTH_END')
    LANE_HEIGHT_START = getArray(config, 'LANE', 'LANE_HEIGHT_START')

    # Get Draw Settings
    FONT = config.getint('DRAW', 'FONT')
    GREEN = getArray(config, 'DRAW', 'GREEN')
    RED = getArray(config, 'DRAW', 'RED')
    YELLOW = getArray(config, 'DRAW', 'YELLOW')
    PASS_FAIL_X = getArray(config, 'DRAW', 'PASS_FAIL_X')
    PASS_FAIL_Y = getArray(config, 'DRAW', 'PASS_FAIL_Y')
    TEXT_Y = LANE_HEIGHT_END - EDGE_GAP + 30

    # Get Bounding Box Settings
    LANE_X1 = LANE_WIDTH_START[0]
    LANE_Y1 = LANE_HEIGHT_START + EDGE_GAP
    LANE_X2 = LANE_WIDTH_END[LANE_COUNT - 1]
    LANE_Y2 = LANE_HEIGHT_END - EDGE_GAP
    SPLIT_X1 = LANE_WIDTH_START[1]
    SPLIT_X2 = LANE_WIDTH_END[1]

    # Get AIO Settings
    AIO_WAIT = config.getfloat('AIO', 'AIO_WAIT')

    # Get Crop Settings
    CAM_WIDTH_MIDPOINT = CAM_WIDTH / 2
    HALF_FRAME_WIDTH = FRAME_WIDTH / 2
    FRAME_WIDTH_START = CAM_WIDTH_MIDPOINT - HALF_FRAME_WIDTH
    FRAME_WIDTH_END = CAM_WIDTH_MIDPOINT + HALF_FRAME_WIDTH
    CAM_HEIGHT_MIDPOINT = CAM_HEIGHT / 2
    HALF_FRAME_HEIGHT = FRAME_HEIGHT / 2
    FRAME_HEIGHT_START = CAM_HEIGHT_MIDPOINT - HALF_FRAME_HEIGHT
    FRAME_HEIGHT_END = CAM_HEIGHT_MIDPOINT + HALF_FRAME_HEIGHT