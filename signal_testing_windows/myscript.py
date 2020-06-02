import signal


def handler(signum, frame):
    time.sleep(2)
    print("DONE!")


signal.signal(signal.SIGBREAK, handler)

while True:
    pass
