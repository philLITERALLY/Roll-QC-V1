import Tkinter

def runningBtn(self):
    return Tkinter.Button(
        self.root,
        text='RUN',
        font='Helvetica 24 bold',
        width=20,
        height=5,
        bg='green',
        activebackground='green',
        command=self.run_btn
    )

def calibrateModeBtn(self):
    return Tkinter.Button(
        self.root, 
        text='CALIBRATE MODE', 
        font='Helvetica 24 bold',
        width=20,
        height=5,
        bg='yellow',
        activebackground='yellow',
        command=self.calibrate_mode_btn
    )

def calibrateBtn(self):
    return Tkinter.Button(
        self.root, 
        text='CALIBRATE', 
        font='Helvetica 24 bold',
        width=20,
        height=5,
        bg='green',
        activebackground='green',
        command=self.calibrate_btn
    )