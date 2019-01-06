'''This module sets up the camera'''

# External Libraries
import cv2      # OpenCV

# My Modules
import config
import info_logger

def main():
    '''Initialise and apply camera settings'''
    reload(config) # Reload any config changes

    capture = cv2.VideoCapture(0)
    capture.set(3, config.CAM_WIDTH)
    capture.set(4, config.CAM_HEIGHT)
    capture.set(5, config.CAM_FPS)

    info_logger.camera_settings(capture)

    return capture
