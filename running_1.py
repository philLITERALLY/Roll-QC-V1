'''This program performs Quality Control on Sub Rolls'''

# External Libraries
import cv2
import threading
import numpy as np

# My Modules
import config
import camera_setup
import running_window
import program_state
import variables
import lane_handling_1

# AIO DLL
import clr
AIO_DLL = clr.AddReference(R'C:\Users\User\Roll-QC-V1\AIOWDMNet.dll')
from AIOWDMNet import AIOWDM # pylint: disable=E0401
AIO_INSTANCE = AIOWDM()
AIO_INSTANCE.RelOutPort(0, 0, 0) # Reset AIO to empty

CAPTURE = camera_setup.main() # Get camera stream

app = running_window.RunningWindow() # GetUI instance
app.start() # Start UI

AIO_ACTIONS = []    # array to hold AIO Actions
THREADS = []        # array to hold threads
THRESHOLD_IMG = []  # shared img
RECTS_ARR = []       # array to hold rectangles
BOX_ARR = []        # array to hold contours
for lane in range(config.LANE_COUNT):
    RECTS_ARR.append([])
    BOX_ARR.append([])

# DELETE            
PASSES = [0, 0, 0]
FAILS = [0, 0, 0]
AVGS = [0, 0, 0]
AVG_WIDTHS = [0, 0, 0]
AVG_HEIGHTS = [0, 0, 0]

class aioThread (threading.Thread):    
    def __init__(self):
      threading.Thread.__init__(self)

    def run(self):
        global AIO_ACTIONS # Action pool
        while not program_state.STOP_PROGRAM:
            if program_state.RUN_MODE:                
                AIO_INSTANCE.RelOutPort(0, 0, variables.IO_RUNNING) # Set AIO to running (high on 8)
            elif program_state.CALIBRATE_MODE:                
                AIO_INSTANCE.RelOutPort(0, 0, 0) # Set AIO to empty
            
            if AIO_ACTIONS: # if actions to perform
                lane_IO = variables.IO_REQUEST[AIO_ACTIONS[0][0]]           # Request Value
                lane_ACK = variables.IO_ACK[AIO_ACTIONS[0][0]]              # ACK Value
                action_IO = variables.CALCULATE_IO_VALUE(AIO_ACTIONS[0][1]) # Action

                AIO_INSTANCE.RelOutPort(0, 0, lane_IO) # Request ACK from PLC for given lane
                
                while AIO_INSTANCE.RelInPort(0, 4) != lane_ACK: # Wait for ACK from PLC
                    if program_state.CALIBRATE_MODE or program_state.STOP_PROGRAM:
                        break
                    pass

                if not program_state.CALIBRATE_MODE and not program_state.STOP_PROGRAM:
                    AIO_INSTANCE.RelOutPort(0, 0, action_IO)    # Send action
                    AIO_ACTIONS.pop(0)                          # Remove action from queue

class imgProc (threading.Thread):
    def __init__(self):
      threading.Thread.__init__(self)
      
    def run(self):
        global THRESHOLD_IMG, PASSES, FAILS, AVGS, AVG_WIDTHS, AVG_HEIGHTS, CONTOURS
        while not program_state.STOP_PROGRAM:
            _, FRAME = CAPTURE.read() # Take each FRAME

            CROPPED = FRAME[config.FRAME_HEIGHT_START:config.FRAME_HEIGHT_END, config.FRAME_WIDTH_START:config.FRAME_WIDTH_END]
            GRAY = cv2.cvtColor(CROPPED, cv2.COLOR_BGR2GRAY)
            _, THRESHOLD_IMG = cv2.threshold(GRAY, config.WHITE_THRESH, 255, 0)
            DISPLAY_IMG = CROPPED
            
            if program_state.THRESH_MODE:
                DISPLAY_IMG = THRESHOLD_IMG

            # Not Thresh Mode
            thresh_statement = (lane for lane in range(config.LANE_COUNT) if not program_state.THRESH_MODE)
            for lane in thresh_statement:
                cv2.putText(CROPPED, "PASS: " + str(PASSES[lane]), (config.PASS_FAIL_X[lane], config.TEXT_Y), config.FONT, 1, config.WHITE, 2)
                cv2.putText(CROPPED, "FAIL: " + str(FAILS[lane]), (config.PASS_FAIL_X[lane], config.TEXT_Y + 30), config.FONT, 1, config.WHITE, 2)
                cv2.putText(CROPPED, "AVG: " + str(AVGS[lane]), (config.PASS_FAIL_X[lane], config.TEXT_Y + 60), config.FONT, 1, config.WHITE, 2)
                if AVG_WIDTHS[lane] > 0:
                    cv2.putText(CROPPED, "AVG WIDTH: " + str(AVG_WIDTHS[lane]), (config.PASS_FAIL_X[lane], config.TEXT_Y + 90), config.FONT, 1, config.WHITE, 2)
                if AVG_HEIGHTS[lane] > 0:
                    cv2.putText(CROPPED, "AVG HEIGHT: " + str(AVG_HEIGHTS[lane]), (config.PASS_FAIL_X[lane], config.TEXT_Y + 120), config.FONT, 1, config.WHITE, 2)
                        
            # Show Lane Boundaries
            cv2.rectangle(CROPPED, (config.LANE_X1, config.LANE_Y1), (config.LANE_X2, config.LANE_Y2), config.YELLOW, 2)
            cv2.rectangle(CROPPED, (config.SPLIT_X1, config.LANE_Y1), (config.SPLIT_X2, config.LANE_Y2), config.YELLOW, 2)

            for lane in range(config.LANE_COUNT):
                for index, rect in enumerate(RECTS_ARR[lane]): 
                    x = rect[0][0]
                    y = rect[0][1]
                    w = rect[1][0]
                    h = rect[1][1]

                    calc_dimensions = config.dimension_calc(lane, w, h)

                    x += config.LANE_WIDTH_START[lane]
                    y += config.LANE_HEIGHT_START

                    start_pos = int(x - (w/2))
                    high_pos = int(y - (h/2))
                    low_pos = int(y + (h/2))
                    cv2.drawContours(CROPPED, [BOX_ARR[lane][index]], 0, config.RED, 2)
                    cv2.putText(CROPPED, calc_dimensions, (start_pos, high_pos), config.FONT, 1, config.RED, 2)

                    if program_state.CALIBRATE_MODE:
                        pixel_dimensions = '{0}px x {1}px'.format(int(w), int(h))
                        cv2.putText(CROPPED, pixel_dimensions, (start_pos, low_pos), config.FONT, 1, config.RED, 2)

            window_name = 'LINE VIEW'
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
        global THRESHOLD_IMG, CONTOURS
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
            CONTOURS = [cnt for cnt in CONTOURS if cv2.contourArea(cnt) > config.MIN_AREA]

            for contour in CONTOURS:
                rect = cv2.minAreaRect(contour)
                box = cv2.boxPoints(rect)
                box = np.int64(box)

                for position in box:
                    position[0] += config.LANE_WIDTH_START[lane]
                    position[1] += config.LANE_HEIGHT_START

                LANE_RECTS.append(rect)
                LANE_BOXES.append(box)

            RECTS_ARR[lane] = LANE_RECTS
            BOX_ARR[lane] = LANE_BOXES

THREADS.append(aioThread())
THREADS.append(imgProc())

for lane in range(config.LANE_COUNT):
    THREADS.append(laneThread(lane))

for thread in THREADS:
    thread.start()

# Wait for stop program
while program_state.STOP_PROGRAM == False:
    pass

print "Stoping"

# Wait for all threads to complete
for t in THREADS:
    t.join()
    
print "Exiting Main Thread"

# CAPTURE.release() # Release everything if job is finished
AIO_INSTANCE.RelOutPort(0, 0, 0) # Reset AIO to empty
cv2.destroyAllWindows() # Destroy all opencv windows
app.root.destroy() # Destroy tkInter windows
