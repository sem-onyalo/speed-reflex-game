import datetime
import random
import time

class SpotChallenge:
    trackingThreshold = 20
    isObjectInPosition = False
    showResult = False
    minObjectSize = None
    maxObjectSize = None
    calibrationStep = 1
    calibrationSubStep = 1
    rectPt1 = None
    rectPt2 = None
    currentRep = 0
    maxRep = 2
    playerMode = None
    defaultFont = None

    # Timer vars
    calibrationStartTime = None
    calibrationMaxTime = 3
    countdownStartTime = None
    countdownMaxTime = 3
    roundStartTime = None
    roundElapsedTime = 0
    roundFreezeTime = False

    # Game mode constants
    gameModeAwaitingCalibrationConfirm = 'AWCL'
    gameModeAwaitingPlayConfirm = 'AWPL'
    gameModeCalibration = 'CLBT'
    gameModeGetPlayers = 'GTPL'
    gameModeCountdown = 'CTDN'
    gameModePlay = 'PLAY'

    # Constructor init'd vars
    audioManager = None
    videoManager = None
    classesToDetect = ["red ball", "blue ball"]
    gameMode = None

    def __init__(self, videoManager, audioManager):
        self.gameMode = self.gameModeAwaitingCalibrationConfirm
        self.defaultFont = videoManager.getDefaultFont()
        self.audioManager = audioManager
        self.videoManager = videoManager

    def isObjectInSpot(self, cols, rows, xLeft, yTop, xRight, yBottom):
        xLeftDiff = abs(xLeft - self.rectPt1[0])
        yTopDiff = abs(yTop - self.rectPt1[1])
        xRightDiff = abs(xRight - self.rectPt2[0])
        yBottomDiff = abs(yBottom - self.rectPt2[1])
        isObjectInPosition = xLeftDiff < self.trackingThreshold and yTopDiff < self.trackingThreshold and xRightDiff < self.trackingThreshold and yBottomDiff < self.trackingThreshold
        return isObjectInPosition

    def getRectanglePts(self):
        maxWidth = self.videoManager.frameWidth
        minHeight = self.videoManager.imgMargin
        maxHeight = self.videoManager.frameHeight - self.videoManager.imgMargin
        size = self.minObjectSize # size = random.randint(self.minObjectSize, self.maxObjectSize)
        widthPt = random.randint(0, maxWidth)
        heightPt = random.randint(minHeight, maxHeight)
        if widthPt + size > maxWidth:
            xRight = widthPt
            xLeft = widthPt - size
        else:
            xLeft = widthPt
            xRight = widthPt + size
        if heightPt + size > maxHeight:
            yBottom = heightPt
            yTop = heightPt - size
        else:
            yTop = heightPt
            yBottom = heightPt + size
        rectPt1 = (xLeft, yTop)
        rectPt2 = (xRight, yBottom)
        return rectPt1, rectPt2
    
    def getElapsedTimeStr(self, elapsedTime):
        if self.roundFreezeTime:
            if self.roundElapsedTime == 0:
                self.roundElapsedTime = elapsedTime
            elapsedTime = self.roundElapsedTime
        elapsedTimeStr = str(datetime.timedelta(seconds=elapsedTime))
        elapsedTimeStr = elapsedTimeStr[(elapsedTimeStr.index(':') + 1):]
        return elapsedTimeStr

    def getTextPosition(self, text, textFont, textScale, textThickness, widthFactor=1, widthPos='centre', heightPos='centre'):
        textSize = self.videoManager.getTextSize(text, self.defaultFont, textScale, textThickness)
        textWidth = textSize[0]
        textHeight = textSize[1]

        if widthPos == 'right':
            textX = int(round((self.videoManager.frameWidth / widthFactor - textWidth) / 2)) + self.videoManager.frameWidth - int(round(self.videoManager.frameWidth / widthFactor))
        else: # elif widthPos == 'centre'
            textX = int(round((self.videoManager.frameWidth / widthFactor - textWidth) / 2))

        if heightPos == 'top':
            textY = self.videoManager.imgMargin + textHeight
        else: # elif heightPos == 'centre'
            textY = int(round((self.videoManager.frameHeight - textHeight) / 2)) + textHeight

        return textX, textY, textWidth, textHeight

    def addText(self, text, textScale=1, textColor=(238,238,238), textThickness=2, menuColor=(155,109,29), showBackground=True, position='centre'):
        textX, textY, textWidth, textHeight = self.getTextPosition(text, self.defaultFont, textScale, textThickness)
        menuPadX = 15
        menuPadY = 20
        rectPt1X = textX - menuPadX
        rectPt1Y = textY - textHeight - menuPadY
        rectPt2X = textX + textWidth + menuPadX
        rectPt2Y = textY + menuPadY
        if showBackground:
            self.videoManager.addRectangle((rectPt1X, rectPt1Y), (rectPt2X, rectPt2Y), menuColor, -1)
        self.videoManager.addText(text, (textX, textY), self.defaultFont, textScale, textColor, textThickness)

    def showOnePlayerGameStats(self, elapsedTime, maxRep, currentRep):
        widthPositionFactor = 3
        textColor = (114, 70, 20)
        titleScale = 1
        titleThickness = 3
        valueScale = 1.5
        valueThickness = 4

        timeTitle = 'TIME'
        timeTitleTopPad = 10
        timeValueTopPad = timeTitleTopPad + 15
        timeValue = self.getElapsedTimeStr(elapsedTime)
        timeTitleX, timeTitleY, _, timeTitleHeight = self.getTextPosition(timeTitle, self.defaultFont, titleScale, titleThickness, widthPositionFactor, heightPos='top')
        timeValueX, timeValueY, _, _ = self.getTextPosition(timeValue, self.defaultFont, valueScale, valueThickness, widthPositionFactor, heightPos='top')
        self.videoManager.addText(timeTitle, (timeTitleX, timeTitleY + timeTitleTopPad), self.defaultFont, titleScale, textColor, titleThickness)
        self.videoManager.addText(timeValue, (timeValueX, timeValueY + timeTitleHeight + timeValueTopPad), self.defaultFont, valueScale, textColor, valueThickness)
        
        progTitle = 'PROGRESS'
        progTitleTopPad = 10
        progValueTopPad = progTitleTopPad + 15
        progValue = str(currentRep) + '/' + str(maxRep)
        progTitleX, progTitleY, _, progTitleHeight = self.getTextPosition(progTitle, self.defaultFont, titleScale, titleThickness, widthPositionFactor, widthPos='right', heightPos='top')
        progValueX, progValueY, _, _ = self.getTextPosition(progValue, self.defaultFont, valueScale, valueThickness, widthPositionFactor, widthPos='right', heightPos='top')
        self.videoManager.addText(progTitle, (progTitleX, progTitleY + progTitleTopPad), self.defaultFont, titleScale, textColor, titleThickness)
        self.videoManager.addText(progValue, (progValueX, progValueY + progTitleHeight + progValueTopPad), self.defaultFont, valueScale, textColor, valueThickness)
    
        if self.roundFreezeTime:
            self.addText(timeValue, textScale=4, textThickness=8)

    def showTwoPlayerGameStats(self, elapsedTime, maxRep, currentReps, splitLineThickness):
        widthPositionFactor = 4
        textColor = (114, 70, 20)
        timeTitleScale = 2
        timeTitleThickness = 5
        timeValueScale = 3
        timeValueThickness = 8
        progTitleScale = 1
        progTitleThickness = 3
        progValueScale = 1.5
        progValueThickness = 4
        
        timeTitle = 'TIME'
        timeValue = self.getElapsedTimeStr(elapsedTime)
        timeTitleTopPad = 10
        timeValueTopPad = timeTitleTopPad + 15
        timeTitleX, timeTitleY, _, timeTitleHeight = self.getTextPosition(timeTitle, self.defaultFont, timeTitleScale, timeTitleThickness, heightPos='top')
        timeValueX, timeValueY, _, _ = self.getTextPosition(timeValue, self.defaultFont, timeValueScale, timeValueThickness, heightPos='top')
        self.videoManager.addText(timeTitle, (timeTitleX, timeTitleY + timeTitleTopPad), self.defaultFont, timeTitleScale, textColor, timeTitleThickness)
        self.videoManager.addText(timeValue, (timeValueX, timeValueY + timeTitleHeight + timeValueTopPad), self.defaultFont, timeValueScale, textColor, timeValueThickness)

        progTitle = 'PROGRESS'
        progTitleTopPad = 10
        progValueTopPad = progTitleTopPad + 15
        
        progValueP1 = str(currentReps[0]) + '/' + str(maxRep)
        progTitleP1X, progTitleP1Y, _, progTitleP1Height = self.getTextPosition(progTitle, self.defaultFont, progTitleScale, progTitleThickness, widthPositionFactor, heightPos='top')
        progValueP1X, progValueP1Y, _, _ = self.getTextPosition(progValueP1, self.defaultFont, progValueScale, progValueThickness, widthPositionFactor, heightPos='top')
        self.videoManager.addText(progTitle, (progTitleP1X, progTitleP1Y + progTitleTopPad), self.defaultFont, progTitleScale, textColor, progTitleThickness)
        self.videoManager.addText(progValueP1, (progValueP1X, progValueP1Y + progTitleP1Height + progValueTopPad), self.defaultFont, progValueScale, textColor, progValueThickness)

        progValueP2 = str(currentReps[1]) + '/' + str(maxRep)
        progTitleP2X, progTitleP2Y, _, progTitleP2Height = self.getTextPosition(progTitle, self.defaultFont, progTitleScale, progTitleThickness, widthPositionFactor, widthPos='right', heightPos='top')
        progValueP2X, progValueP2Y, _, _ = self.getTextPosition(progValueP2, self.defaultFont, progValueScale, progValueThickness, widthPositionFactor, widthPos='right', heightPos='top')
        self.videoManager.addText(progTitle, (progTitleP2X, progTitleP2Y + progTitleTopPad), self.defaultFont, progTitleScale, textColor, progTitleThickness)
        self.videoManager.addText(progValueP2, (progValueP2X, progValueP2Y + progTitleP2Height + progValueTopPad), self.defaultFont, progValueScale, textColor, progValueThickness)

    def showCalibrateMenu(self):
        text = "Press 'C' to calibrate"
        self.addText(text)

    def showPlayerModeMenu(self):
        text = 'No. of Players?'
        self.addText(text)

    def showPlayOrExitMenu(self):
        text = 'Play again?'
        self.addText(text)

    def updateCalibrationParams(self):
        calibrationComplete = False
        if self.calibrationStep == 1: # calibrate for smallest object size
            if self.calibrationSubStep == 1:
                print('Hold object farthest from screen')
                self.calibrationStartTime = time.time()
                self.calibrationSubStep = self.calibrationSubStep + 1
            elif self.calibrationSubStep == 2:
                currentTime = time.time()
                if currentTime - self.calibrationStartTime > self.calibrationMaxTime:
                    xCoordDiff = self.videoManager.getXCoordDetectionDiff()
                    yCoordDiff = self.videoManager.getYCoordDetectionDiff()
                    if xCoordDiff != None and yCoordDiff != None:
                        self.minObjectSize = min(int(xCoordDiff), int(yCoordDiff))
                        self.calibrationStep = self.calibrationStep + 1
                        self.calibrationSubStep = 1
                    else:
                        raise RuntimeError('Calibration failed at step', self.calibrationStep, self.calibrationSubStep)

        elif self.calibrationStep == 2: # calculate calibration parmas
            self.calibrationSubStep = 1
            self.calibrationStep = 1
            calibrationComplete = True
            print('Calibration complete!')

        return calibrationComplete

    def updateGameParams(self, playerMode):
        labelDetections = True
        isRoundComplete = False
        if playerMode == 1:
            boxColor = (0, 255, 255)
            if self.rectPt1 == None or self.rectPt2 == None: # initial state, on first run
                self.rectPt1, self.rectPt2 = self.getRectanglePts()
            elif self.showResult:
                boxColor = (0, 255, 0)
                if self.roundFreezeTime:
                    if not self.audioManager.audioStatus[self.audioManager.winLevelAudioKey]:
                        isRoundComplete = True
                        # reset game vars
                        self.rectPt1, self.rectPt2 = self.getRectanglePts()
                        self.showResult = False
                        self.currentRep = 0
                    else:
                        labelDetections = False
                elif not self.audioManager.audioStatus[self.audioManager.winItemAudioKey]:
                    self.rectPt1, self.rectPt2 = self.getRectanglePts()
                    self.showResult = False
                else:
                    labelDetections = False
            elif self.isObjectInPosition:
                boxColor = (0, 255, 0)
                labelDetections = False
                self.currentRep = self.currentRep + 1
                self.isObjectInPosition = False
                self.showResult = True
                if self.currentRep == self.maxRep:
                    self.roundFreezeTime = True
                    self.audioManager.playAudio(self.audioManager.winLevelAudioKey)
                else:
                    self.audioManager.playAudio(self.audioManager.winItemAudioKey)
            
            if not self.roundFreezeTime:
                self.videoManager.addRectangle(self.rectPt1, self.rectPt2, boxColor, 6)

        return isRoundComplete, labelDetections

    def runGameCountdown(self):
        countdownComplete = False
        if self.countdownStartTime == None:
            self.countdownStartTime = time.time()
            countdownStr = str(self.countdownMaxTime)
        else:
            currentTime = time.time()
            if currentTime - self.countdownStartTime > self.countdownMaxTime:
                countdownStr = 'GO'
                self.countdownStartTime = None
                countdownComplete = True
            else:
                countdownStr = str(self.countdownMaxTime - int(currentTime - self.countdownStartTime))
        self.addText(countdownStr, textScale=4, textThickness=8)
        return countdownComplete

    def runGamePlay(self, playerMode, elapsedTime, labelDetections):
        if self.playerMode == 1:
            trackingFunc = lambda cols, rows, xLeft, yTop, xRight, yBottom : self.isObjectInSpot(cols, rows, xLeft, yTop, xRight, yBottom)
            if labelDetections:
                self.isObjectInPosition = self.videoManager.labelDetections(self.classesToDetect[0], trackingFunc)
            self.showOnePlayerGameStats(elapsedTime, self.maxRep, self.currentRep)

        elif self.playerMode == 2:
            splitLineThickness = 10
            currentReps = [0, 0]
            trackingFunc = lambda cols, rows, xLeft, yTop, xRight, yBottom : False
            splitLinePt1 = (int(self.videoManager.frameWidth/2), 0)
            splitLinePt2 = (int(self.videoManager.frameWidth/2), self.videoManager.frameHeight)
            self.videoManager.addLine(splitLinePt1, splitLinePt2, (255, 255, 255), thickness=splitLineThickness)
            self.videoManager.labelDetections(self.classesToDetect[0], trackingFunc)
            self.showTwoPlayerGameStats(elapsedTime, self.maxRep, currentReps, splitLineThickness=splitLineThickness)

    def runGameStep(self):
        continueRun = True
        cmd = self.videoManager.getKeyPress()

        if cmd == 27: # ESC
            continueRun = False

        elif self.gameMode == self.gameModeAwaitingCalibrationConfirm:
            self.videoManager.readNewFrame()
            self.showCalibrateMenu()
            if cmd == 67 or cmd == 99: # C or c
                self.gameMode = self.gameModeCalibration
                print('Switching game mode:', self.gameMode)
        
        elif self.gameMode == self.gameModeCalibration:
            self.videoManager.runDetection()
            isCalibrationComplete = self.updateCalibrationParams()
            trackingFunc = lambda cols, rows, xLeft, yTop, xRight, yBottom : False
            self.videoManager.labelDetections(self.classesToDetect[0], trackingFunc)
            if isCalibrationComplete:
                self.gameMode = self.gameModeGetPlayers
                print('Switching game mode:', self.gameMode)
        
        elif self.gameMode == self.gameModeGetPlayers:
            self.videoManager.readNewFrame()
            self.showPlayerModeMenu()
            if cmd == 49 or cmd == 50: # 1 or 2
                if cmd == 49: # 1
                    self.playerMode = 1
                elif cmd == 50: # 2
                    self.playerMode = 2
                self.gameMode = self.gameModeCountdown
                print('Switching game mode:', self.gameMode)
        
        elif self.gameMode == self.gameModeCountdown:
            self.videoManager.readNewFrame()
            isCountdownComplete = self.runGameCountdown()
            if isCountdownComplete:
                self.roundElapsedTime = 0
                self.roundFreezeTime = False
                self.roundStartTime = time.time()
                self.gameMode = self.gameModePlay
                print('Switching game mode:', self.gameMode)

        elif self.gameMode == self.gameModePlay:
            elapsedTime = int(time.time() - self.roundStartTime)
            self.videoManager.runDetection()
            isRoundComplete, labelDetections = self.updateGameParams(self.playerMode)
            self.runGamePlay(self.playerMode, elapsedTime, labelDetections)
            if isRoundComplete:
                self.gameMode = self.gameModeAwaitingPlayConfirm
                print('Switching game mode:', self.gameMode)

        elif self.gameMode == self.gameModeAwaitingPlayConfirm:
            self.videoManager.readNewFrame()
            self.showPlayOrExitMenu()
            if cmd == 78 or cmd == 110: # N or n
                continueRun = False
            elif cmd == 89 or cmd == 121: # Y or y
                self.gameMode = self.gameModeGetPlayers
                print('Switching game mode:', self.gameMode)

        else:
            raise RuntimeError('Game mode error, current game mode is', self.gameMode)
        
        self.videoManager.showImage()
        return continueRun

    def shutdownGame(self):
        self.videoManager.shutdown()