
# External Libraries
import csv
import Tkinter as tk
import tkMessageBox
import os

# My Modules
import info_logger
import get_logins

# Create new application start with date time
info_logger.init()

login_page = tk.Tk()
login_page.attributes("-fullscreen", True)
login_page.title("LOGIN PAGE")

# Create error message that will hide/show
error = tk.Label(login_page ,text="KEYCARD ERROR - TRY AGAIN", font="Helvetica 26 bold", fg="red")

# Load login info
LOGINS = get_logins.main()

def return_key(event):
    username = ''
    keycard_value = keycard_input.get()

    # Clear any existing error message
    error.place_forget()

    # Loop through users to find keycard value
    for user in LOGINS:
        if user[0] == keycard_value:
            username = user[1]

    # If keycard value exists and user found
    if username != '':
        info_logger.login(keycard_value, username)

        # Hide login window
        login_page.withdraw()

        # Load camera script
        os.system('running.py')
        
        # When camera script exists show login window
        login_page.deiconify()
    else:
        info_logger.login_error(keycard_value)
        error.place(relx=0.5, rely=0.65, anchor=tk.CENTER)

    keycard_input.set('')

def on_closing():
    if tkMessageBox.askokcancel("Quit", "Do you want to quit?"):
        info_logger.shutdown()
        login_page.destroy()

# If window is closed call logging function
login_page.protocol("WM_DELETE_WINDOW", on_closing)

# If return key entered on page call login function
login_page.bind('<Return>', return_key)

header = tk.Label(login_page ,text="SCAN KEYCARD", font="Helvetica 26 bold")
header.place(relx=0.5, rely=0.45, anchor=tk.CENTER)

keycard_input = tk.StringVar()
input = tk.Entry(login_page, font="Helvetica 26 bold", textvariable=keycard_input)
input.place(relx=0.5, rely=0.55, anchor=tk.CENTER)
input.focus()

login_page.mainloop()
