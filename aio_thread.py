import threading
import time

exitFlag = 0

class aioThread (threading.Thread):
    def __init__(self, actions):
        self.actions = actions
      
    def run(self):
        print "Starting AIO"
        while True:
            print("Actions: " + str(self.actions))
        print "Exiting AIO"
