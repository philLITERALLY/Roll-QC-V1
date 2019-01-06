import Tkinter

def resultsBtn(self):
    return Tkinter.Button(
        self.root,
        text='RESULTS',
        font='Helvetica 24 bold',
        width=20,
        height=5,
        bg='blue',
        activebackground='blue',
        foreground='white',
        command=self.results_btn
    )

def calibrateModeBtn(self, settings_win):
    return Tkinter.Button(
        settings_win,
        text='CALIBRATE',
        font='Helvetica 24 bold',
        width=20,
        height=5,
        bg='yellow',
        activebackground='yellow',
        command=self.calibrate_btn
    )

def threshModeBtn(self, settings_win):
    return Tkinter.Button(
        settings_win,
        text='THRESH MODE',
        font='Helvetica 24 bold',
        width=20,
        height=5,
        bg='blue',
        activebackground='blue',
        command=self.thresh_btn
    )