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
        font='Helvetica 12 bold',
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
        font='Helvetica 12 bold',
        width=20,
        height=5,
        bg='blue',
        activebackground='blue',
        fg='white',
        command=self.thresh_btn
    )

def returnRunningBtn(self, settings_win):
    return Tkinter.Button(
        settings_win,
        text='RETURN',
        font='Helvetica 12 bold',
        width=40,
        height=5,
        bg='red',
        activebackground='red',
        command=self.settings_window_close
    )

def createLabel(settings_win, text):
    return Tkinter.Label(
        settings_win,
        text=text,
        font='Helvetica 12',
    )

def createBtn(settings_win, text, action):
    return Tkinter.Button(
        settings_win,
        text=text,
        font='Helvetica 12',
        width=6,
        height=2,
        command=action
    )