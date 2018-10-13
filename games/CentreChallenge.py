import time

class CentreChallenge:
    winGameText = 'YOU WIN!'
    trackingThreshold = 50
    maxTime = 5
    showResultMaxTime = 3
    startTime = None
    showResult = False
    startShowResultTime = None
    isObjectInPosition = False
    isWinning = False

    videoManager = None
    classToDetect = ""

    def __init__(self, videoManager, classToDetect):
        self.videoManager = videoManager
        self.classToDetect = classToDetect

    def isObjectInMiddle(self, cols, rows, xLeft, yTop, xRight, yBottom):
        return abs(xLeft - (cols - xRight)) < self.trackingThreshold and abs(yTop - (rows - yBottom)) < self.trackingThreshold

    def updateGameParams(self):
        gameLabel = None
        if self.isWinning and self.isObjectInPosition and self.startTime is not None:
            currentTime = time.time()
            elapsedTime = currentTime - self.startTime
            if self.showResult and self.startShowResultTime is not None:
                gameLabel = self.winGameText
                currentShowResultTime = time.time()
                elapsedShowResultTime = currentShowResultTime - self.startShowResultTime
                if elapsedShowResultTime > self.showResultMaxTime:
                    # reset game
                    self.startShowResultTime = None
                    self.startTime = None
                    self.showResult = False
                    self.isWinning = False
                    self.isObjectInPosition = False
                    gameLabel = None
            else:
                if elapsedTime > self.maxTime:
                    self.startShowResultTime = time.time()
                    self.showResult = True
                    gameLabel = self.winGameText
                else:
                    gameLabel = str(int(elapsedTime)) if elapsedTime >= 1 else None
        elif self.isWinning and not self.isObjectInPosition:
            self.isWinning = False
            self.startTime = None
        elif not self.isWinning and self.isObjectInPosition:
            self.startTime = time.time()
            self.isWinning = True
        return gameLabel
        
    def runGameStep(self, cmd):
        self.videoManager.runDetection()
        gameLabel = self.updateGameParams()
        trackingFunc = lambda cols, rows, xLeft, yTop, xRight, yBottom : self.isObjectInMiddle(cols, rows, xLeft, yTop, xRight, yBottom)
        
        self.isObjectInPosition = self.videoManager.labelDetections(self.classToDetect, trackingFunc, gameLabel)
        return self.videoManager.getImage(), True