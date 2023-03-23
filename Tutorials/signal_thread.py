import threading
import signal
import os
import time

def my_thread():
    while True:
        print("Thread is running...")
        time.sleep(1)

# create the thread and start it
thread = threading.Thread(target=my_thread)
thread.start()

# Wait for the user to press Ctrl+C
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # terminate the thread
    print("Terminating thread...")
    
    pass


