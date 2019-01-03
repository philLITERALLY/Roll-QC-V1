'''This module contains the running window'''

# External Libraries
import threading
import Tkinter
import os
import cv2

# Main Variables 
import program_state
import get_logins
import info_logger
import buttons
import config

LOGINS = get_logins.main()
KEYCARD_VALUE = ''

class RunningWindow(threading.Thread):
    def key(self, event):
        global KEYCARD_VALUE
        KEYCARD_VALUE += event.char
        if event.keysym == 'Escape':
            program_state.stop_program(True)

    def enter(self, event):
        global KEYCARD_VALUE
        username = ''
        
        # Loop through users to find keycard value
        for user in LOGINS:
            if user[0] == KEYCARD_VALUE:
                username = user[1]

        # If keycard value exists and user found
        if username != '':
            info_logger.settings_access(KEYCARD_VALUE, username)

            if username == 'Master':
                self.settings_window(True)
            else:
                self.settings_window(False)
        else:
            info_logger.settings_access_error(KEYCARD_VALUE)

        KEYCARD_VALUE = ''

    def settings_window(self, admin):
        # If settings window not already open
        if self.root.settings_win == None or not Tkinter.Toplevel.winfo_exists(self.root.settings_win):
            # Stop Running and turn on calibrate mode
            program_state.set_run_mode(False)
            program_state.set_calibrate_mode(True)

            # Create Settings Window
            self.root.settings_win = Tkinter.Toplevel(self.root)
            # Make Settings Window remain on top until destroyed, or attribute changes.
            self.root.settings_win.attributes('-topmost', True)
            self.root.settings_win.protocol('WM_DELETE_WINDOW', self.settings_window_close)

            self.root.settings_win.placeholder_label = Tkinter.Label(self.root.settings_win, text='Settings Window Placeholder!')
            self.root.settings_win.placeholder_label.pack()  

            if admin == True:
                self.root.settings_win.calibrateModeBtn = buttons.calibrateModeBtn(self, self.root.settings_win)
                self.root.settings_win.calibrateModeBtn.pack()

                self.root.settings_win.threshModeBtn = buttons.threshModeBtn(self, self.root.settings_win)
                self.root.settings_win.threshModeBtn.pack()

    def settings_window_close(self):
        # Stop calibrate mode and start running again
        program_state.set_calibrate_mode(False)
        program_state.set_thresh(False)
        program_state.set_run_mode(True)
        self.root.settings_win.destroy()

    def results_btn(self):
        os.system('results.csv')

    def calibrate_btn(self):
        program_state.request_calibration(True)

    def thresh_btn(self):
        if (self.root.settings_win.threshModeBtn.cget('text') == 'THRESH MODE') :
                program_state.set_thresh(True)
                self.root.settings_win.threshModeBtn.configure(bg='red', activebackground='red', text='STOP THRESH MODE')

        elif (self.root.settings_win.threshModeBtn.cget('text') == 'STOP THRESH MODE') :
                program_state.set_thresh(False)
                for i in range(config.LANE_COUNT):        
                    cv2.destroyWindow('THRESH' + str(i))
                self.root.settings_win.threshModeBtn.configure(bg='blue', activebackground='blue', text='THRESH MODE')

    def __init__(self):
        self.root = Tkinter.Tk()
        self.root.overrideredirect(1)
        self.root.attributes('-topmost', True)

        # Create Placeholder for settings window
        self.root.settings_win = None

        ws = self.root.winfo_screenwidth() # width of the screen
        hs = self.root.winfo_screenheight() # height of the screen

        w = 390 # width for the Tk root
        h = 214 # height for the Tk root

        # calculate x and y coordinates for the Tk root window
        x = ws - w
        y = hs - h

        # set the dimensions of the screen and where it is placed
        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))

        self.root.resultsBtn = buttons.resultsBtn(self)
        self.root.resultsBtn.pack(side=Tkinter.LEFT)
        
        self.root.protocol('WM_DELETE_WINDOW', self.disable_close)
        self.root.bind('<Key>', self.key)
        self.root.bind('<Return>', self.enter)

        self.root.deiconify()
        
        threading.Thread.__init__(self)

    def take_focus(self):
        self.root.focus_force()
        self.root.after(1, lambda: self.take_focus())

    def run(self):
        self.root.after(1, lambda: self.take_focus())
        self.root.mainloop()

    def disable_close(self):
        pass

