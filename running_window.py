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

    def change_config_value(self, type, value, text):
        reload(config)

        text.set(value)

        lines = open('config.py', 'r').readlines() # open config file

        if type == 'Thresh':
            lines[64] = 'WHITE_THRESH = ' + str(value) + '\n'
        elif type == 'WidthLow':
            lines[66] = 'FAIL_WIDTH_LOW = ' + str(value) + ' # mm\n'
        elif type == 'WidthHigh':
            lines[67] = 'FAIL_WIDTH_HIGH = ' + str(value) + ' # mm\n'
        elif type == 'HeightLow':
            lines[68] = 'FAIL_HEIGHT_LOW = ' + str(value) + ' # mm\n'
        elif type == 'HeightHigh':
            lines[69] = 'FAIL_HEIGHT_HIGH = ' + str(value) + ' # mm\n'

        out = open('config.py', 'w')
        out.writelines(lines)
        out.close()

        reload(config)

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

            # Setup max length value + buttons
            self.root.settings_win.max_length_label = buttons.createLabel(self.root.settings_win, 'Max Length')
            self.root.settings_win.max_length_label.grid(row=0, column=0, columnspan=4, sticky='w,e,n,s')
            self.root.settings_win.max_length_text = Tkinter.StringVar()
            self.root.settings_win.max_length_text.set(config.FAIL_WIDTH_HIGH)
            self.root.settings_win.max_length_value = buttons.createLabelText(self.root.settings_win, self.root.settings_win.max_length_text)
            self.root.settings_win.max_length_value.grid(row=1, column=1, columnspan=2, sticky='w,e,n,s')
            self.root.settings_win.max_length_minus = \
                buttons.createBtn(self.root.settings_win, '-', lambda: self.change_config_value('WidthHigh', config.FAIL_WIDTH_HIGH - 1, self.root.settings_win.max_length_text))
            self.root.settings_win.max_length_minus.grid(row=1, column=0)
            self.root.settings_win.max_length_plus = \
                buttons.createBtn(self.root.settings_win, '+', lambda: self.change_config_value('WidthHigh', config.FAIL_WIDTH_HIGH + 1, self.root.settings_win.max_length_text))
            self.root.settings_win.max_length_plus.grid(row=1, column=3)

            # Setup min length value + buttons
            self.root.settings_win.min_length_label = buttons.createLabel(self.root.settings_win, 'Min Length (mm)')
            self.root.settings_win.min_length_label.grid(row=2, column=0, columnspan=4, sticky='w,e,n,s')
            self.root.settings_win.min_length_text = Tkinter.StringVar()
            self.root.settings_win.min_length_text.set(config.FAIL_WIDTH_LOW)
            self.root.settings_win.min_length_value = buttons.createLabelText(self.root.settings_win, self.root.settings_win.min_length_text)
            self.root.settings_win.min_length_value.grid(row=3, column=1, columnspan=2, sticky='w,e,n,s')
            self.root.settings_win.min_length_minus = \
                buttons.createBtn(self.root.settings_win, '-', lambda: self.change_config_value('WidthLow', config.FAIL_WIDTH_LOW - 1, self.root.settings_win.min_length_text))
            self.root.settings_win.min_length_minus.grid(row=3, column=0)
            self.root.settings_win.min_length_plus = \
                buttons.createBtn(self.root.settings_win, '+', lambda: self.change_config_value('WidthLow', config.FAIL_WIDTH_LOW + 1, self.root.settings_win.min_length_text))
            self.root.settings_win.min_length_plus.grid(row=3, column=3)

            # Setup max thickness value + buttons
            self.root.settings_win.max_thickness_label = buttons.createLabel(self.root.settings_win, 'Max Thickness (mm)')
            self.root.settings_win.max_thickness_label.grid(row=4, column=0, columnspan=4, sticky='w,e,n,s')
            self.root.settings_win.max_thickness_text = Tkinter.StringVar()
            self.root.settings_win.max_thickness_text.set(config.FAIL_HEIGHT_HIGH)
            self.root.settings_win.max_thickness_value = buttons.createLabelText(self.root.settings_win, self.root.settings_win.max_thickness_text)
            self.root.settings_win.max_thickness_value.grid(row=5, column=1, columnspan=2, sticky='w,e,n,s')
            self.root.settings_win.max_thickness_minus = \
                buttons.createBtn(self.root.settings_win, '-', lambda: self.change_config_value('HeightHigh', config.FAIL_HEIGHT_HIGH - 1, self.root.settings_win.max_thickness_text))
            self.root.settings_win.max_thickness_minus.grid(row=5, column=0)
            self.root.settings_win.max_thickness_plus = \
                buttons.createBtn(self.root.settings_win, '+', lambda: self.change_config_value('HeightHigh', config.FAIL_HEIGHT_HIGH + 1, self.root.settings_win.max_thickness_text))
            self.root.settings_win.max_thickness_plus.grid(row=5, column=3)

            # Setup min thickness value + buttons
            self.root.settings_win.min_thickness_label = buttons.createLabel(self.root.settings_win, 'Min Thickness (mm)')
            self.root.settings_win.min_thickness_label.grid(row=6, column=0, columnspan=4, sticky='w,e,n,s')
            self.root.settings_win.min_thickness_text = Tkinter.StringVar()
            self.root.settings_win.min_thickness_text.set(config.FAIL_HEIGHT_LOW)
            self.root.settings_win.min_thickness_value = buttons.createLabelText(self.root.settings_win, self.root.settings_win.min_thickness_text)
            self.root.settings_win.min_thickness_value.grid(row=7, column=1, columnspan=2, sticky='w,e,n,s')
            self.root.settings_win.min_thickness_minus = \
                buttons.createBtn(self.root.settings_win, '-', lambda: self.change_config_value('HeightLow', config.FAIL_HEIGHT_LOW - 1, self.root.settings_win.min_thickness_text))
            self.root.settings_win.min_thickness_minus.grid(row=7, column=0)
            self.root.settings_win.min_thickness_plus = \
                buttons.createBtn(self.root.settings_win, '+', lambda: self.change_config_value('HeightLow', config.FAIL_HEIGHT_LOW + 1, self.root.settings_win.min_thickness_text))
            self.root.settings_win.min_thickness_plus.grid(row=7, column=3)

            self.root.settings_win.return_running = buttons.returnRunningBtn(self, self.root.settings_win)
            self.root.settings_win.return_running.grid(row=100, column=0, columnspan=4, pady=(20, 0), sticky='s')

            if admin == True:
                # Setup threshold value + buttons
                self.root.settings_win.threshold_label = buttons.createLabel(self.root.settings_win, 'Threshold')
                self.root.settings_win.threshold_label.grid(row=8, column=0, columnspan=4, sticky='w,e,n,s')
                self.root.settings_win.threshold_text = Tkinter.StringVar()
                self.root.settings_win.threshold_text.set(config.WHITE_THRESH)
                self.root.settings_win.threshold_value = buttons.createLabelText(self.root.settings_win, self.root.settings_win.threshold_text)
                self.root.settings_win.threshold_value.grid(row=9, column=1, columnspan=2, sticky='w,e,n,s')
                self.root.settings_win.threshold_minus = \
                buttons.createBtn(self.root.settings_win, '-', lambda: self.change_config_value('Thresh', config.WHITE_THRESH - 5, self.root.settings_win.threshold_text))
                self.root.settings_win.threshold_minus.grid(row=9, column=0)
                self.root.settings_win.threshold_plus = \
                buttons.createBtn(self.root.settings_win, '+', lambda: self.change_config_value('Thresh', config.WHITE_THRESH + 5, self.root.settings_win.threshold_text))
                self.root.settings_win.threshold_plus.grid(row=9, column=3)

                self.root.settings_win.calibrateModeBtn = buttons.calibrateModeBtn(self, self.root.settings_win)
                self.root.settings_win.calibrateModeBtn.grid(row=10, column=0, columnspan=2, pady=(20, 0), sticky='s')

                self.root.settings_win.threshModeBtn = buttons.threshModeBtn(self, self.root.settings_win)
                self.root.settings_win.threshModeBtn.grid(row=10, column=2, columnspan=2, pady=(20, 0), sticky='s')

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

