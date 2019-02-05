import time

class Timer:
    startTime = 0
    maxTime = 0

    def __init__(self, maxTime):
        self.maxTime = maxTime
        self.startTime = time.time()

    def isElapsed(self):
        currentTime = time.time()
        return currentTime - self.startTime > self.maxTime