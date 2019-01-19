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
import handle_config

my_path = os.path.abspath(os.path.dirname(__file__))

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

    def change_config_value(self, variable, value, text):
        if variable == 'WHITE_THRESH':
            handle_config.WHITE_THRESH += value
            handle_config.setValue('THRESHOLD', 'WHITE_THRESH', handle_config.WHITE_THRESH)
            self.root.settings_win.threshold_text.set(handle_config.WHITE_THRESH)
        elif variable == 'FAIL_WIDTH_LOW':
            handle_config.FAIL_WIDTH_LOW += value
            handle_config.setValue('THRESHOLD', 'FAIL_WIDTH_LOW', handle_config.FAIL_WIDTH_LOW)

            for index, _ in enumerate(handle_config.LANE_FAIL_WIDTHS_LOW):
                handle_config.LANE_FAIL_WIDTHS_LOW[index] = \
                    handle_config.FAIL_WIDTH_LOW / handle_config.WIDTH_RATIOS[index]
            handle_config.setValue('THRESHOLD', 'LANE_FAIL_WIDTHS_LOW', handle_config.LANE_FAIL_WIDTHS_LOW)

            self.root.settings_win.min_length_text.set(handle_config.FAIL_WIDTH_LOW)
        elif variable == 'FAIL_WIDTH_HIGH':
            handle_config.FAIL_WIDTH_HIGH += value
            handle_config.setValue('THRESHOLD', 'FAIL_WIDTH_HIGH', handle_config.FAIL_WIDTH_HIGH)

            for index, _ in enumerate(handle_config.LANE_FAIL_WIDTHS_HIGH):
                handle_config.LANE_FAIL_WIDTHS_HIGH[index] = \
                    handle_config.FAIL_WIDTH_HIGH / handle_config.WIDTH_RATIOS[index]
            handle_config.setValue('THRESHOLD', 'LANE_FAIL_WIDTHS_HIGH', handle_config.LANE_FAIL_WIDTHS_HIGH)

            self.root.settings_win.max_length_text.set(handle_config.FAIL_WIDTH_HIGH)
        elif variable == 'FAIL_HEIGHT_LOW':
            handle_config.FAIL_HEIGHT_LOW += value
            handle_config.setValue('THRESHOLD', 'FAIL_HEIGHT_LOW', handle_config.FAIL_HEIGHT_LOW)

            for index, _ in enumerate(handle_config.LANE_FAIL_HEIGHTS_LOW):
                handle_config.LANE_FAIL_HEIGHTS_LOW[index] = \
                    handle_config.FAIL_HEIGHT_LOW / handle_config.HEIGHT_RATIOS[index]
            handle_config.setValue('THRESHOLD', 'LANE_FAIL_HEIGHTS_LOW', handle_config.LANE_FAIL_HEIGHTS_LOW)

            self.root.settings_win.min_thickness_text.set(handle_config.FAIL_HEIGHT_LOW)
        elif variable == 'FAIL_HEIGHT_HIGH':
            handle_config.FAIL_HEIGHT_HIGH += value
            handle_config.setValue('THRESHOLD', 'FAIL_HEIGHT_HIGH', handle_config.FAIL_HEIGHT_HIGH)

            for index, _ in enumerate(handle_config.LANE_FAIL_HEIGHTS_HIGH):
                handle_config.LANE_FAIL_HEIGHTS_HIGH[index] = \
                    handle_config.FAIL_HEIGHT_HIGH / handle_config.HEIGHT_RATIOS[index]
            handle_config.setValue('THRESHOLD', 'LANE_FAIL_HEIGHTS_HIGH', handle_config.LANE_FAIL_HEIGHTS_HIGH)

            self.root.settings_win.max_thickness_text.set(handle_config.FAIL_HEIGHT_HIGH)

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
            self.root.settings_win.overrideredirect(1)

            y = 75          # y co-ord for settings window
            if admin == True:
                h = 305     # height for the settings window
                w = 1180    # width for the settings window
                x = 60      # x co-ord for settings window
            else:
                h = 305     # height for the settings window
                w = 490     # width for the settings window
                x = 410     # x co-ord for settings window

            # set the dimensions of the settings window and where it is placed
            self.root.settings_win.geometry('%dx%d+%d+%d' % (w, h, x, y))

            # Setup max length value + buttons
            self.root.settings_win.max_length_label = buttons.createLabel(self.root.settings_win, 'Max Length')
            self.root.settings_win.max_length_label.grid(row=0, column=0, columnspan=4, pady=(5,5), sticky='w,e,n,s')
            self.root.settings_win.max_length_text = Tkinter.StringVar()
            self.root.settings_win.max_length_text.set(handle_config.FAIL_WIDTH_HIGH)
            self.root.settings_win.max_length_value = buttons.createLabelText(self.root.settings_win, self.root.settings_win.max_length_text)
            self.root.settings_win.max_length_value.grid(row=1, column=1, columnspan=2, padx=(20,20), sticky='w,e,n,s')
            self.root.settings_win.max_length_minus = \
                buttons.createBtn(self.root.settings_win, '-', lambda: self.change_config_value('FAIL_WIDTH_HIGH', -1, self))
            self.root.settings_win.max_length_minus.grid(row=1, column=0, padx=(20,0))
            self.root.settings_win.max_length_plus = \
                buttons.createBtn(self.root.settings_win, '+', lambda: self.change_config_value('FAIL_WIDTH_HIGH', 1, self))
            self.root.settings_win.max_length_plus.grid(row=1, column=3)

            # Setup min length value + buttons
            self.root.settings_win.min_length_label = buttons.createLabel(self.root.settings_win, 'Min Length (mm)')
            self.root.settings_win.min_length_label.grid(row=0, column=4, columnspan=4, pady=(5,5), sticky='w,e,n,s')
            self.root.settings_win.min_length_text = Tkinter.StringVar()
            self.root.settings_win.min_length_text.set(handle_config.FAIL_WIDTH_LOW)
            self.root.settings_win.min_length_value = buttons.createLabelText(self.root.settings_win, self.root.settings_win.min_length_text)
            self.root.settings_win.min_length_value.grid(row=1, column=5, columnspan=2, padx=(20,20), sticky='w,e,n,s')
            self.root.settings_win.min_length_minus = \
                buttons.createBtn(self.root.settings_win, '-', lambda: self.change_config_value('FAIL_WIDTH_LOW', -1, self))
            self.root.settings_win.min_length_minus.grid(row=1, column=4, padx=(20,0))
            self.root.settings_win.min_length_plus = \
                buttons.createBtn(self.root.settings_win, '+', lambda: self.change_config_value('FAIL_WIDTH_LOW', 1, self))
            self.root.settings_win.min_length_plus.grid(row=1, column=7)

            # Setup max thickness value + buttons
            self.root.settings_win.max_thickness_label = buttons.createLabel(self.root.settings_win, 'Max Thickness (mm)')
            self.root.settings_win.max_thickness_label.grid(row=4, column=0, columnspan=4, pady=(5,5), sticky='w,e,n,s')
            self.root.settings_win.max_thickness_text = Tkinter.StringVar()
            self.root.settings_win.max_thickness_text.set(handle_config.FAIL_HEIGHT_HIGH)
            self.root.settings_win.max_thickness_value = buttons.createLabelText(self.root.settings_win, self.root.settings_win.max_thickness_text)
            self.root.settings_win.max_thickness_value.grid(row=5, column=1, columnspan=2, padx=(20,20), sticky='w,e,n,s')
            self.root.settings_win.max_thickness_minus = \
                buttons.createBtn(self.root.settings_win, '-', lambda: self.change_config_value('FAIL_HEIGHT_HIGH', -1, self))
            self.root.settings_win.max_thickness_minus.grid(row=5, column=0, padx=(20,0))
            self.root.settings_win.max_thickness_plus = \
                buttons.createBtn(self.root.settings_win, '+', lambda: self.change_config_value('FAIL_HEIGHT_HIGH', 1, self))
            self.root.settings_win.max_thickness_plus.grid(row=5, column=3)

            # Setup min thickness value + buttons
            self.root.settings_win.min_thickness_label = buttons.createLabel(self.root.settings_win, 'Min Thickness (mm)')
            self.root.settings_win.min_thickness_label.grid(row=4, column=4, columnspan=4, pady=(5,5), sticky='w,e,n,s')
            self.root.settings_win.min_thickness_text = Tkinter.StringVar()
            self.root.settings_win.min_thickness_text.set(handle_config.FAIL_HEIGHT_LOW)
            self.root.settings_win.min_thickness_value = buttons.createLabelText(self.root.settings_win, self.root.settings_win.min_thickness_text)
            self.root.settings_win.min_thickness_value.grid(row=5, column=5, columnspan=2, padx=(20,20), sticky='w,e,n,s')
            self.root.settings_win.min_thickness_minus = \
                buttons.createBtn(self.root.settings_win, '-', lambda: self.change_config_value('FAIL_HEIGHT_LOW', -1, self))
            self.root.settings_win.min_thickness_minus.grid(row=5, column=4, padx=(20,0))
            self.root.settings_win.min_thickness_plus = \
                buttons.createBtn(self.root.settings_win, '+', lambda: self.change_config_value('FAIL_HEIGHT_LOW', 1, self))
            self.root.settings_win.min_thickness_plus.grid(row=5, column=7)

            self.root.settings_win.return_running = buttons.returnRunningBtn(self, self.root.settings_win)
            self.root.settings_win.return_running.grid(row=100, column=0, columnspan=100, pady=(20,0), padx=(20,20), sticky='w,e,s')

            if admin == True:
                # Setup threshold value + buttons
                self.root.settings_win.threshold_label = buttons.createLabel(self.root.settings_win, 'Threshold')
                self.root.settings_win.threshold_label.grid(row=0, column=8, columnspan=4, pady=(5,5), sticky='w,e,n,s')
                self.root.settings_win.threshold_text = Tkinter.StringVar()
                self.root.settings_win.threshold_text.set(handle_config.WHITE_THRESH)
                self.root.settings_win.threshold_value = buttons.createLabelText(self.root.settings_win, self.root.settings_win.threshold_text)
                self.root.settings_win.threshold_value.grid(row=1, column=9, columnspan=2, padx=(20,20), sticky='w,e,n,s')
                self.root.settings_win.threshold_minus = \
                    buttons.createBtn(self.root.settings_win, '-', lambda: self.change_config_value('WHITE_THRESH', -5, self))
                self.root.settings_win.threshold_minus.grid(row=1, column=8, padx=(20,0))
                self.root.settings_win.threshold_plus = \
                    buttons.createBtn(self.root.settings_win, '+', lambda: self.change_config_value('WHITE_THRESH', 5, self))
                self.root.settings_win.threshold_plus.grid(row=1, column=11)

                self.root.settings_win.calibrateModeBtn = buttons.calibrateModeBtn(self, self.root.settings_win)
                self.root.settings_win.calibrateModeBtn.grid(row=0, rowspan=6, column=12, columnspan=2, padx=(20,0), pady=(5,5), sticky='w,e,n,s')

                self.root.settings_win.threshModeBtn = buttons.threshModeBtn(self, self.root.settings_win)
                self.root.settings_win.threshModeBtn.grid(row=0, rowspan=6, column=14, columnspan=2, padx=(20,0), pady=(5,5), sticky='w,e,n,s')

    def settings_window_close(self):
        # Stop calibrate mode and start running again
        program_state.set_calibrate_mode(False)
        program_state.set_thresh(False)
        program_state.set_run_mode(True)
        self.root.settings_win.destroy()

    def results_btn(self):
        os.system(R'C:/Users/User/Desktop/results.csv')

    def calibrate_btn(self):
        program_state.request_calibration(True)

    def thresh_btn(self):
        if (self.root.settings_win.threshModeBtn.cget('text') == 'THRESH MODE') :
                program_state.set_thresh(True)
                self.root.settings_win.threshModeBtn.configure(bg='red', activebackground='red', text='STOP THRESH MODE')

        elif (self.root.settings_win.threshModeBtn.cget('text') == 'STOP THRESH MODE') :
                program_state.set_thresh(False)
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

