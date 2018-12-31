'''This module contains the running window'''

# External Libraries
import threading
import Tkinter
import os

# Main Variables 
import program_state
import get_logins
import info_logger
import buttons

LOGINS = get_logins.main()
KEYCARD_VALUE = ''

class RunningWindow(threading.Thread):
    def key(self, event):
        global KEYCARD_VALUE
        KEYCARD_VALUE += event.char

    def enter(self, event):
        global KEYCARD_VALUE
        username = ''
        
        # Loop through users to find keycard value
        for user in LOGINS:
            if user[0] == KEYCARD_VALUE:
                username = user[1]

        # If keycard value exists and user found
        if username != '':
            info_logger.logout(KEYCARD_VALUE, username)
            
            program_state.stop_program(True)        
            self.root.quit()
        else:
            info_logger.logout_error(KEYCARD_VALUE)

        KEYCARD_VALUE = ''

    def results_btn(self):
        os.system('results.csv')

    def calibrate_btn(self):
        program_state.request_calibration(True)

    def __init__(self):
        self.root = Tkinter.Tk()
        self.root.overrideredirect(1)
        self.root.attributes('-topmost', True)

        ws = self.root.winfo_screenwidth() # width of the screen
        hs = self.root.winfo_screenheight() # height of the screen

        if program_state.ADMIN_USER == 'True':
            w = 780 # width for the Tk root
        else:
            w = 390 # width for the Tk root
        h = 214 # height for the Tk root

        # calculate x and y coordinates for the Tk root window
        x = ws - w
        y = hs - h

        # set the dimensions of the screen and where it is placed
        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))

        self.root.resultsBtn = buttons.resultsBtn(self)
        self.root.resultsBtn.pack(side=Tkinter.LEFT)

        if program_state.ADMIN_USER == 'True':
            self.root.calibrateModeBtn = buttons.calibrateModeBtn(self)
            self.root.calibrateModeBtn.pack(side=Tkinter.LEFT)
        
        self.root.protocol('WM_DELETE_WINDOW', self.disable_close)
        self.root.bind('<Key>', self.key)
        self.root.bind('<Return>', self.enter)
        
        threading.Thread.__init__(self)

    def run(self):
        self.root.mainloop()

    def disable_close(self):
        pass

