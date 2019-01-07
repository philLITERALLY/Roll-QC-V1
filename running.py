'''This program performs Quality Control on Sub Rolls'''

# External Libraries
import cv2
import threading
import numpy as np
import time

# My Modules
import config
import camera_setup
import running_window
import program_state
import variables
import info_logger

# AIO DLL
import clr
AIO_DLL = clr.AddReference(R'C:\Users\User\Roll-QC-V1\AIOWDMNet.dll')
from AIOWDMNet import AIOWDM # pylint: disable=E0401
AIO_INSTANCE = AIOWDM()
AIO_INSTANCE.RelOutPort(0, 0, 0) # Reset AIO to empty

CAPTURE = camera_setup.main() # Get camera stream

app = running_window.RunningWindow() # GetUI instance
app.start() # Start UI

OUTPUT = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # current AIO output
AIO_PASS_FAIL_PULSE = [] # array to hold Lane AIO Pass/Fail
AIO_ACTIONS = []         # array to hold AIO Values
LANE_FLAG = []           # array to hold Lane AIO Outputs
THREADS = []             # array to hold threads
THRESHOLD_IMG = []       # shared img
RECTS_ARR = []           # array to hold rectangles
BOX_ARR = []             # array to hold contours
AVG_WIDTHS_CURRENT = []  # array to hold [0] current avg width [1] total scanned
AVG_HEIGHTS_CURRENT = [] # array to hold [0] current avg height [1] total scanned
AVG_WIDTHS_TOTAL = []    # array to hold [0] current total width [1] total ran
AVG_HEIGHTS_TOTAL = []   # array to hold [0] current total height [1] total ran
PASS_COUNTS = []         # array to hold total pass count
FAIL_COUNTS = []         # array to hold total fail count

# Setup variables for number of lanes
for lane in range(config.LANE_COUNT):
    AIO_PASS_FAIL_PULSE.append([0, 0])
    AIO_ACTIONS.append(0)
    LANE_FLAG.append('')
    RECTS_ARR.append([])
    BOX_ARR.append([])
    AVG_WIDTHS_CURRENT.append([0, 0])
    AVG_HEIGHTS_CURRENT.append([0, 0])
    AVG_WIDTHS_TOTAL.append([0, 0])
    AVG_HEIGHTS_TOTAL.append([0, 0])
    PASS_COUNTS.append(0)
    FAIL_COUNTS.append(0)

class lanePulseThread (threading.Thread):
    ''' One Per Lane '''
    ''' This thread listens for pass/fail flags '''
    ''' After a delay sets the AIO value and clears the flag '''
    def __init__(self, lane):
        threading.Thread.__init__(self)
        self.lane = lane

    def run(self):
        global LANE_FLAG
        lane = self.lane
        while not program_state.STOP_PROGRAM and not program_state.CALIBRATE_MODE:
            if LANE_FLAG[lane]: # if flag detected
                if LANE_FLAG[lane] == 'Pass':
                    AIO_PASS_FAIL_PULSE[lane] = [1, 0]
                    time.sleep(config.AIO_WAIT)      # sleep for 200 ms
                    AIO_ACTIONS[lane] = 0
                elif LANE_FLAG[lane] == 'Fail':
                    AIO_PASS_FAIL_PULSE[lane] = [0, 1]
                    time.sleep(config.AIO_WAIT)      # sleep for 200 ms
                    AIO_ACTIONS[lane] = 1

                AIO_PASS_FAIL_PULSE[lane] = [0, 0]
                LANE_FLAG[lane] = ''

class aioThread (threading.Thread):
    ''' Master '''
    ''' This thread controls the AIO '''
    ''' If running mode - Sets AIO to running state with any Pass/Fail values '''
    ''' If calibrate mode - Sets AIO to stop running '''
    def __init__(self):
      threading.Thread.__init__(self)

    def run(self):
        global AIO_ACTIONS, OUTPUT
        LAST_OUTPUT = []
        while not program_state.STOP_PROGRAM:
            if program_state.RUN_MODE:
                # Set AIO to running (high on 8) and any pulses
                OUTPUT = [
                    AIO_PASS_FAIL_PULSE[0][0], AIO_PASS_FAIL_PULSE[0][1], # Lane 1 Pass, Fail
                    AIO_PASS_FAIL_PULSE[1][0], AIO_PASS_FAIL_PULSE[1][1], # Lane 2 Pass, Fail
                    AIO_PASS_FAIL_PULSE[2][0], AIO_PASS_FAIL_PULSE[2][1], # Lane 3 Pass, Fail
                    0, 0,
                    1, # Running
                    AIO_ACTIONS[0], AIO_ACTIONS[1], AIO_ACTIONS[2]
                ]
            elif program_state.CALIBRATE_MODE:
                # Set AIO to stop
                OUTPUT = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

            # Only send update if it is different than last value
            if OUTPUT != LAST_OUTPUT:
                AIO_INSTANCE.RelOutPort(0, 0, variables.CALCULATE_IO_VALUE(OUTPUT))
                LAST_OUTPUT = OUTPUT[:]

class statsThread (threading.Thread):
    ''' Master '''
    ''' This thread calculates the running statistics and flags pass/fail'''
    def __init__(self):
      threading.Thread.__init__(self)

    def calculate_avg(self, array, newVal):
        total = array[0] * array[1]
        new_total = total + newVal
        new_total_count = array[1] + 1
        new_avg = new_total / new_total_count
        return [new_avg, new_total_count]

    def run(self):
        global LANE_FLAG                               # flag to alert AIO
        global RECTS_ARR                               # contains current bounding rectangles
        global PASS_COUNTS, FAIL_COUNTS                # total counts
        global AVG_WIDTHS_TOTAL, AVG_HEIGHTS_TOTAL     # total average width/height
        global AVG_WIDTHS_CURRENT, AVG_HEIGHTS_CURRENT # current average width/height
        while not program_state.STOP_PROGRAM:
            if not program_state.RUN_MODE:
                # Reset stats
                for lane in range(config.LANE_COUNT):
                    AIO_PASS_FAIL_PULSE[lane] = [0, 0]
                    AIO_ACTIONS[lane] = 0
                    LANE_FLAG[lane] = ''
                    AVG_WIDTHS_CURRENT[lane] = [0, 0]
                    AVG_HEIGHTS_CURRENT[lane] = [0, 0]
                    AVG_WIDTHS_TOTAL[lane] = [0, 0]
                    AVG_HEIGHTS_TOTAL[lane] = [0, 0]
                    PASS_COUNTS[lane] = 0
                    FAIL_COUNTS[lane] = 0

                # Skip everything else
                pass

            for lane in range(config.LANE_COUNT):
                # If blob deteced within our scan section
                if len(RECTS_ARR[lane]) > 0:
                    current_rect = RECTS_ARR[lane][:]

                    try:
                        if current_rect[1][0] > current_rect[1][1]:
                            w = current_rect[1][0]
                            h = current_rect[1][1]
                        else:
                            w = current_rect[1][1]
                            h = current_rect[1][0]

                        # Calculate AVG width and height
                        AVG_WIDTHS_CURRENT[lane] = self.calculate_avg(AVG_WIDTHS_CURRENT[lane], w)
                        AVG_HEIGHTS_CURRENT[lane] = self.calculate_avg(AVG_HEIGHTS_CURRENT[lane], h)
                    except Exception as e:
                        info_logger.stats_error(lane, current_rect, RECTS_ARR, e)

                # If no blob is detected
                elif AVG_WIDTHS_CURRENT[lane][0] > 0 and AVG_HEIGHTS_CURRENT[lane][0] > 0:
                    average_width = AVG_WIDTHS_CURRENT[lane][0]
                    average_height = AVG_HEIGHTS_CURRENT[lane][0]

                    # Calculate total AVG width and height
                    AVG_WIDTHS_TOTAL[lane] = self.calculate_avg(AVG_WIDTHS_TOTAL[lane], average_width)
                    AVG_HEIGHTS_TOTAL[lane] = self.calculate_avg(AVG_HEIGHTS_TOTAL[lane], average_height)

                    if average_width < config.LANE_FAIL_WIDTHS_LOW[lane] or \
                        average_width > config.LANE_FAIL_WIDTHS_HIGH[lane] or \
                        average_height < config.LANE_FAIL_HEIGHTS_LOW[lane] or \
                        average_height > config.LANE_FAIL_HEIGHTS_HIGH[lane]:
                        FAIL_COUNTS[lane] += 1
                        LANE_FLAG[lane] = 'Fail'
                    else:
                        PASS_COUNTS[lane] += 1
                        LANE_FLAG[lane] = 'Pass'

                    info_logger.result(lane + 1, int(average_width), int(average_height))

                    # Reset arrays
                    AVG_WIDTHS_CURRENT[lane] = [0, 0]
                    AVG_HEIGHTS_CURRENT[lane] = [0, 0]

class imgProc (threading.Thread):
    ''' Master '''
    ''' This thread controls the displayed image '''
    ''' Displays any contours along with run information and AIO state '''
    def __init__(self):
      threading.Thread.__init__(self)

    def run(self):
        global THRESHOLD_IMG                       # Thresholded image
        global RECTS_ARR                           # contains current bounding rectangles
        global PASS_COUNTS, FAIL_COUNTS            # total counts
        global AVG_WIDTHS_TOTAL, AVG_HEIGHTS_TOTAL # average width/height
        while not program_state.STOP_PROGRAM:
            reload(config) # Reload any config changes

            _, FRAME = CAPTURE.read() # Take each FRAME

            CROPPED = FRAME[config.FRAME_HEIGHT_START:config.FRAME_HEIGHT_END, config.FRAME_WIDTH_START:config.FRAME_WIDTH_END]
            GRAY = cv2.cvtColor(CROPPED, cv2.COLOR_BGR2GRAY)                    # Turn image to Grayscale
            _, THRESHOLD_IMG = cv2.threshold(GRAY, config.WHITE_THRESH, 255, 0) # Run threshold on gray image
            DISPLAY_IMG = CROPPED

            if program_state.THRESH_MODE:
                DISPLAY_IMG = THRESHOLD_IMG

            for lane in range(config.LANE_COUNT):
                if RECTS_ARR[lane]:
                    color = config.RED
                    current_rect = RECTS_ARR[lane]
                    current_box = BOX_ARR[lane]

                    if current_rect[1][0] > current_rect[1][1]:
                        w = current_rect[1][0]
                        h = current_rect[1][1]
                    else:
                        w = current_rect[1][1]
                        h = current_rect[1][0]

                    calc_dimensions = config.dimension_calc(lane, w, h)

                    if variables.is_pass(lane, w, h):
                        color = config.GREEN

                    start_pos = min([position[0] for position in current_box])
                    high_pos = min([position[1] for position in current_box])
                    low_pos = max([position[1] for position in current_box])
                    cv2.drawContours(CROPPED, [current_box], 0, color, 2)
                    cv2.putText(CROPPED, calc_dimensions, (start_pos, high_pos), config.FONT, 1, color, 2)

                    if program_state.CALIBRATE_MODE:
                        pixel_dimensions = '{0}px x {1}px'.format(int(w), int(h))
                        cv2.putText(CROPPED, pixel_dimensions, (start_pos, low_pos), config.FONT, 1, config.RED, 2)

            if program_state.REQUEST_CALIBRATE:
                lines = open('config.py', 'r').readlines() # open config file

                calib_widths = lines[6][15:-6] # get calibration widths
                calib_widths = calib_widths.replace(']','').replace('[','')
                calib_widths = calib_widths.split(", ") # turn into array

                calib_heights = lines[7][16:-6] # get calibration heights
                calib_heights = calib_heights.replace(']','').replace('[','')
                calib_heights = calib_heights.split(", ") # turn into array

                for lane in range(config.LANE_COUNT): # loop through lanes
                    if RECTS_ARR[lane]: # if lane has contour
                        current_rect = RECTS_ARR[lane]
                        if current_rect[1][0] > current_rect[1][1]:
                            w = current_rect[1][0]
                            h = current_rect[1][1]
                        else:
                            w = current_rect[1][1]
                            h = current_rect[1][0]

                        calib_widths[lane] = w
                        calib_heights[lane] = h

                lines[6] = 'PIXEL_WIDTHS = ' + str(calib_widths) + ' # px\n'
                lines[7] = 'PIXEL_HEIGHTS = ' + str(calib_heights) + ' # px\n'
                out = open('config.py', 'w')
                out.writelines(lines)
                out.close()

                program_state.request_calibration(False)

            # Not Thresh Mode
            not_thresh_statement = (lane for lane in range(config.LANE_COUNT) if not program_state.THRESH_MODE and not program_state.CALIBRATE_MODE)
            for lane in not_thresh_statement:
                AVG_TEXT = 'AVG: 0%'
                AVG_WIDTHS_TEXT = 'AVG WIDTH: ' + str(int(AVG_WIDTHS_TOTAL[lane][0] * config.WIDTH_RATIOS[lane])) + 'mm'
                AVG_HEIGHTS_TEXT = 'AVG HEIGHT: ' + str(int(AVG_HEIGHTS_TOTAL[lane][0] * config.HEIGHT_RATIOS[lane])) + 'mm'
                if PASS_COUNTS[lane] > 0:
                    AVG_TEXT = 'AVG: ' + str(100 * PASS_COUNTS[lane] / (PASS_COUNTS[lane] + FAIL_COUNTS[lane])) + '%'
                cv2.putText(CROPPED, "PASS: " + str(PASS_COUNTS[lane]), (config.PASS_FAIL_X[lane], config.TEXT_Y), config.FONT, 1, config.WHITE, 2)
                cv2.putText(CROPPED, "FAIL: " + str(FAIL_COUNTS[lane]), (config.PASS_FAIL_X[lane], config.TEXT_Y + 30), config.FONT, 1, config.WHITE, 2)
                cv2.putText(CROPPED, AVG_TEXT, (config.PASS_FAIL_X[lane], config.TEXT_Y + 60), config.FONT, 1, config.WHITE, 2)
                if AVG_WIDTHS_TOTAL[lane][0] > 0:
                    cv2.putText(CROPPED, AVG_WIDTHS_TEXT, (config.PASS_FAIL_X[lane], config.TEXT_Y + 90), config.FONT, 1, config.WHITE, 2)
                if AVG_HEIGHTS_TOTAL[lane][0] > 0:
                    cv2.putText(CROPPED, AVG_HEIGHTS_TEXT, (config.PASS_FAIL_X[lane], config.TEXT_Y + 120), config.FONT, 1, config.WHITE, 2)

            # Show Lane Boundaries
            cv2.rectangle(CROPPED, (config.LANE_X1, config.LANE_Y1), (config.LANE_X2, config.LANE_Y2), config.YELLOW, 2)
            cv2.rectangle(CROPPED, (config.SPLIT_X1, config.LANE_Y1), (config.SPLIT_X2, config.LANE_Y2), config.YELLOW, 2)

            # Show current AIO
            cv2.putText(CROPPED, "OUTPUT: " + str(OUTPUT), (350, 50), config.FONT, 1, config.RED, 2)

            # Show min/max values
            cv2.putText(CROPPED, "MIN WIDTH: " + str(int(config.FAIL_WIDTH_LOW)) + "mm", (50, 900), config.FONT, 1, config.RED, 2)
            cv2.putText(CROPPED, "MAX WIDTH: " + str(int(config.FAIL_WIDTH_HIGH)) + "mm", (50, 950), config.FONT, 1, config.RED, 2)
            cv2.putText(CROPPED, "MIN HEIGHT: " + str(int(config.FAIL_HEIGHT_LOW)) + "mm", (50, 1000), config.FONT, 1, config.RED, 2)
            cv2.putText(CROPPED, "MAX HEIGHT: " + str(int(config.FAIL_HEIGHT_HIGH)) + "mm", (50, 1050), config.FONT, 1, config.RED, 2)

            window_name = 'LINE VIEW'
            if DISPLAY_IMG != []:
                cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                cv2.imshow(window_name, DISPLAY_IMG)

            # Required for loop no need for key read
            k = cv2.waitKey(1) & 0xFF

class laneThread (threading.Thread):
    def __init__(self, lane):
      threading.Thread.__init__(self)
      self.lane = lane

    def run(self):
        global THRESHOLD_IMG # Thresholded image
        global RECTS_ARR     # contains current bounding rectangles
        while not program_state.STOP_PROGRAM:
            lane = self.lane
            while len(THRESHOLD_IMG) == 0:
                pass

            reload(config) # Reload any config changes

            LANE_RECTS = []
            LANE_BOXES = []
            THRESH_LANE_IMG = THRESHOLD_IMG[config.LANE_HEIGHT_START:config.LANE_HEIGHT_END, config.LANE_WIDTH_START[lane]:config.LANE_WIDTH_END[lane]]

            # run opencv find contours, only external boxes
            _, CONTOURS, _ = cv2.findContours(THRESH_LANE_IMG, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if CONTOURS:
                try:
                    contour = max(CONTOURS, key=cv2.contourArea) # find the biggest area
                except Exception as e:
                    info_logger.lane_error(lane, CONTOURS, e)

                rect = cv2.minAreaRect(contour)
                box = cv2.boxPoints(rect)[:]
                box = np.int64(box)

                start_pos = min([position[1] for position in box])
                high_pos = max([position[1] for position in box])
                exiting_box = config.LANE_HEIGHT - config.EDGE_GAP

                # if area big enough
                # if contour within top bound
                # if contour hasn't left bottom bound
                if cv2.contourArea(contour) > config.MIN_AREA and \
                    start_pos > config.EDGE_GAP and \
                    high_pos < exiting_box:

                    for position in box:
                        position[0] += config.LANE_WIDTH_START[lane]
                        position[1] += config.LANE_HEIGHT_START

                    LANE_RECTS = rect
                    LANE_BOXES = box

            RECTS_ARR[lane] = LANE_RECTS
            BOX_ARR[lane] = LANE_BOXES

THREADS.append(aioThread())
THREADS.append(statsThread())
THREADS.append(imgProc())

for lane in range(config.LANE_COUNT):
    THREADS.append(lanePulseThread(lane))
    THREADS.append(laneThread(lane))

for thread in THREADS:
    thread.start()

# Wait for stop program
while program_state.STOP_PROGRAM == False:
    pass

print "Stopping"

# Wait for all threads to complete
for t in THREADS:
    t.join()

print "Exiting Main Thread"

CAPTURE.release() # Release everything if job is finished
AIO_INSTANCE.RelOutPort(0, 0, 0) # Reset AIO to empty
cv2.destroyAllWindows() # Destroy all opencv windows
app.root.destroy() # Destroy tkInter windows
