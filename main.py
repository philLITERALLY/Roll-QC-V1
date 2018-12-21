"""This program performs Quality Control on Sub Rolls"""

# External Libraries
import cv2

# My Modules
import camera_setup
import info_logger
import config

# Create new log with date time
info_logger.init()

# Get camera stream
CAPTURE = camera_setup.main()

# Setup font
FONT = cv2.FONT_HERSHEY_SIMPLEX

# Define the codec and create VideoWriter object
FOURCC = cv2.VideoWriter_fourcc(*'DIVX')
OUT = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(
    'D', 'I', 'V', 'X'), 10.0, (1920, 200))
OUT2 = cv2.VideoWriter('output2.avi', cv2.VideoWriter_fourcc(
    'D', 'I', 'V', 'X'), 10.0, (1920, 200), False)

while 1:
    # Take each FRAME
    _, FRAME = CAPTURE.read()

    CROPPED = FRAME[450:650, 0:1920]
    GRAY = cv2.cvtColor(CROPPED, cv2.COLOR_BGR2GRAY)
    _, THRESHOLD_IMG = cv2.threshold(GRAY, 190, 255, 0)
    DRAW_IMG = CROPPED

    # run opencv find contours, only external boxes
    _, CONTOURS, _ = cv2.findContours(
        THRESHOLD_IMG, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    CONTOURS = [cnt for cnt in CONTOURS if cv2.contourArea(cnt) > 2000]

    # for each contour draw a bounding box and order number
    for cnt in CONTOURS:
        x, y, w, h = cv2.boundingRect(cnt)
        dimensions = config.dimension_calc(w, h)

        cv2.rectangle(DRAW_IMG, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(DRAW_IMG, dimensions, (x, y), FONT, 1, (0, 0, 255), 2)

    # cv2.imshow('THRESHOLD_IMG', THRESHOLD_IMG)
    cv2.imshow('DRAW_IMG', DRAW_IMG)

    # # write the flipped frame
    OUT.write(DRAW_IMG)
    OUT2.write(THRESHOLD_IMG)

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

info_logger.shutdown()

# Release everything if job is finished
CAPTURE.release()
OUT.release()
OUT2.release()
cv2.destroyAllWindows()
