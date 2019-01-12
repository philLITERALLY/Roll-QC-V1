'''This module sets up the camera'''

# External Libraries
import cv2      # OpenCV

# My Modules
import handle_config
import info_logger

def main():
    '''Initialise and apply camera settings'''
    capture = cv2.VideoCapture(0)
    print handle_config.CAM_WIDTH
    capture.set(3, handle_config.CAM_WIDTH)
    capture.set(4, handle_config.CAM_HEIGHT)
    capture.set(5, handle_config.CAM_FPS)

    info_logger.camera_settings(capture)

    return capture
