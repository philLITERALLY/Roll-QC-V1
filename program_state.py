'''This module handles the programs state'''

RUN_MODE = False
STOP_PROGRAM = False
ADMIN_USER = False
CALIBRATE_MODE = False
REQUEST_CALIBRATE = False

def set_admin_user(value):
    global ADMIN_USER
    ADMIN_USER = value

def set_calibrate_mode(value):
    global CALIBRATE_MODE
    CALIBRATE_MODE = value

def request_calibration(value):
    global REQUEST_CALIBRATE
    REQUEST_CALIBRATE = value

def set_runmode(value):
    global RUN_MODE
    RUN_MODE = value

def stop_program(value):
    global STOP_PROGRAM
    STOP_PROGRAM = True