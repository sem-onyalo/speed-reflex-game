import time

class CentreChallenge:
    winGameText = 'YOU WIN!'
    classToDetect = "red ball"
    trackingThreshold = 50
    maxTime = 5
    showResultMaxTime = 3
    startTime = None
    showResult = False
    startShowResultTime = None
    isObjectInPosition = False
    isWinning = False
    defaultFont = None

    videoManager = None

    def __init__(self, videoManager):
        self.defaultFont = videoManager.getDefaultFont()
        self.videoManager = videoManager

    def isObjectInMiddle(self, cols, rows, xLeft, yTop, xRight, yBottom):
        return abs(xLeft - (cols - xRight)) < self.trackingThreshold and abs(yTop - (rows - yBottom)) < self.trackingThreshold

    def addText(self, text, textScale=1, textColor=(238,238,238), textThickness=2, menuColor=(155,109,29), showMenuBack=True, position='centre'):
        textSize = self.videoManager.getTextSize(text, self.defaultFont, textScale, textThickness)
        textWidth = textSize[0]
        textHeight = textSize[1]
        textX = int(round((self.videoManager.frameWidth - textWidth) / 2))
        textY = int(round((self.videoManager.frameHeight - textHeight) / 2)) + textHeight
        menuPadX = 15
        menuPadY = 20
        rectPt1X = textX - menuPadX
        rectPt1Y = textY - textHeight - menuPadY
        rectPt2X = textX + textWidth + menuPadX
        rectPt2Y = textY + menuPadY
        if showMenuBack:
            self.videoManager.addRectangle((rectPt1X, rectPt1Y), (rectPt2X, rectPt2Y), menuColor, -1)
        self.videoManager.addText(text, (textX, textY), self.defaultFont, textScale, textColor, textThickness)

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
        
    def runGameStep(self):
        self.videoManager.runDetection()
        gameLabel = self.updateGameParams()
        trackingFunc = lambda cols, rows, xLeft, yTop, xRight, yBottom : self.isObjectInMiddle(cols, rows, xLeft, yTop, xRight, yBottom)
        self.isObjectInPosition = self.videoManager.labelDetections([self.classToDetect], trackingFunc)

        if gameLabel != None:
            self.addText(gameLabel, textScale=3, textThickness=7)

        self.videoManager.showImage()
        return self.continueGame()

    def continueGame(self):
        ch = self.videoManager.getKeyPress()
        return ch != 27 # ESC

    def shutdownGame(self):
        self.videoManager.shutdown()