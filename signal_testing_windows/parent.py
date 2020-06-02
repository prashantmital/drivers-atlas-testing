import subprocess
import os
import time

proc = subprocess.Popen(['C:/cygwin/bin/bash', 'myscript'], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)

time.sleep(3)

os.kill(proc.pid, signal.CTRL_BREAK_EVENT)

proc.wait(timeout=5)
