import time

class Timer:
    startTime = 0
    maxTime = 0

    def __init__(self, maxTime=0):
        self.maxTime = maxTime
        self.startTime = time.time()

    def isElapsed(self):
        currentTime = time.time()
        return currentTime - self.startTime > self.maxTime

    def getElapsedCountdown(self):
        currentTime = time.time()
        return self.maxTime - int(currentTime - self.startTime)

    def getElapsed(self):
        currentTime = time.time()
        return int(currentTime - self.startTime)