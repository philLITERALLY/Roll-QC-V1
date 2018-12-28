"""This module handles the programs state"""

RUN_MODE = False
STOP_PROGRAM = False

def toggle_runmode(value):
    global RUN_MODE
    RUN_MODE = value

def stop_program(value):
    global STOP_PROGRAM
    STOP_PROGRAM = True