"""This module contains the running window"""

# External Libraries
import threading
import Tkinter

# Main Variables 
import program_state
import get_logins
import info_logger

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


    def run_btn(self):
        if (self.root.runBtn.cget('text') == "RUN") :
                # Set App to running mode
                program_state.toggle_runmode(True)
                
                # Change runBtn to stop colour
                self.root.runBtn.configure(bg="red", activebackground="red", text="PAUSE")

        elif (self.root.runBtn.cget('text') == "PAUSE") :
                # Take App out of running mode
                program_state.toggle_runmode(False)

                # Change runBtn to default
                self.root.runBtn.configure(bg="green", activebackground="green", text="RUN")

    def __init__(self):
        self.root = Tkinter.Tk()

        self.root.runBtn = Tkinter.Button(self.root, text="RUN", command=self.run_btn)
        self.root.runBtn.pack()
        
        self.root.protocol("WM_DELETE_WINDOW", self.disable_close)
        self.root.bind("<Key>", self.key)
        self.root.bind("<Return>", self.enter)
        
        threading.Thread.__init__(self)

    def run(self):
        self.root.mainloop()

    def disable_close(self):
        pass

