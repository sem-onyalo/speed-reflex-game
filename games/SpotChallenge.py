import datetime
import random
import time
from core import Player, Point, Rectangle

class SpotChallenge:
    trackingThreshold = 20
    minObjectSize = None
    maxObjectSize = None
    calibrationStep = 1
    calibrationSubStep = 1
    gameRectangles = [None, None]
    playerMode = None
    defaultFont = None
    twoPlayerSplitLineThickness = 10

    # Timer vars
    calibrationStartTime = None
    calibrationMaxTime = 3
    countdownStartTime = None
    countdownMaxTime = 3
    roundStartTime = None
    roundElapsedTime = 0
    winItemSleepMaxTime = 0.5
    winRoundSleepMaxTime = 7

    # Game mode constants
    gameModeAwaitingCalibrationConfirm = 'AWCL'
    gameModeAwaitingPlayConfirm = 'AWPL'
    gameModeCalibration = 'CLBT'
    gameModeGetPlayers = 'GTPL'
    gameModeCountdown = 'CTDN'
    gameModePlay = 'PLAY'

    # Constructor init'd vars
    player1 = None
    player2 = None
    gameMode = None
    audioManager = None
    videoManager = None
    classesToDetect = ["red ball", "blue ball"]

    def __init__(self, videoManager, audioManager):
        self.gameMode = self.gameModeAwaitingCalibrationConfirm
        self.defaultFont = videoManager.getDefaultFont()
        self.audioManager = audioManager
        self.videoManager = videoManager
        self.player1 = Player.Player()
        self.player2 = Player.Player()

    def getGameRectangle(self, minSize, xRange, yRange):
        widthPt = random.randint(xRange[0], xRange[1])
        heightPt = random.randint(yRange[0], yRange[1])
        if widthPt + minSize > xRange[1]:
            xRight = widthPt
            xLeft = widthPt - minSize
        else:
            xLeft = widthPt
            xRight = widthPt + minSize
        if heightPt + minSize > yRange[1]:
            yBottom = heightPt
            yTop = heightPt - minSize
        else:
            yTop = heightPt
            yBottom = heightPt + minSize
        rect = Rectangle.Rectangle(Point.Point(xLeft,yTop), Point.Point(xRight,yBottom))
        return rect

    def getGameRectangleDiff(self, gameRectangle, xLeft, yTop, xRight, yBottom):
        xLeftDiff = abs(xLeft - gameRectangle.pt1.x)
        yTopDiff = abs(yTop - gameRectangle.pt1.y)
        xRightDiff = abs(xRight - gameRectangle.pt2.x)
        yBottomDiff = abs(yBottom - gameRectangle.pt2.y)
        return xLeftDiff, yTopDiff, xRightDiff, yBottomDiff
    
    def getElapsedTimeStr(self, elapsedTime):
        if self.player1.freezeRoundResult:
            if self.roundElapsedTime == 0:
                self.roundElapsedTime = elapsedTime
            elapsedTime = self.roundElapsedTime
        elapsedTimeStr = str(datetime.timedelta(seconds=elapsedTime))
        elapsedTimeStr = elapsedTimeStr[(elapsedTimeStr.index(':') + 1):]
        return elapsedTimeStr

    def getTextPosition(self, text, textFont, textScale, textThickness, widthFactor=1, widthPos='centre', heightPos='centre'):
        topPad = 30 #self.videoManager.imgMargin
        textSize = self.videoManager.getTextSize(text, self.defaultFont, textScale, textThickness)
        textWidth = textSize[0]
        textHeight = textSize[1]

        if widthPos == 'right':
            textX = int(round((self.videoManager.frameWidth / widthFactor - textWidth) / 2)) + self.videoManager.frameWidth - int(round(self.videoManager.frameWidth / widthFactor))
        else: # elif widthPos == 'centre'
            textX = int(round((self.videoManager.frameWidth / widthFactor - textWidth) / 2))

        if heightPos == 'top':
            textY = topPad + textHeight
        else: # elif heightPos == 'centre'
            textY = int(round((self.videoManager.frameHeight - textHeight) / 2)) + textHeight

        return textX, textY, textWidth, textHeight

    def addText(self, text, textScale=1, textColor=(238,238,238), textThickness=2, menuColor=(155,109,29), showBackground=True, widthFactor=1, widthPos='centre', heightPos='centre'):
        textX, textY, textWidth, textHeight = self.getTextPosition(text, self.defaultFont, textScale, textThickness, widthFactor=widthFactor, widthPos=widthPos, heightPos=heightPos)
        menuPadX = 15
        menuPadY = 20
        rectPt1X = textX - menuPadX
        rectPt1Y = textY - textHeight - menuPadY
        rectPt2X = textX + textWidth + menuPadX
        rectPt2Y = textY + menuPadY
        if showBackground:
            self.videoManager.addRectangle((rectPt1X, rectPt1Y), (rectPt2X, rectPt2Y), menuColor, -1)
        self.videoManager.addText(text, (textX, textY), self.defaultFont, textScale, textColor, textThickness)

    def showCalibrateMenu(self):
        text = "Press 'C' to calibrate"
        self.addText(text)

    def showPlayerModeMenu(self):
        text = 'No. of Players?'
        self.addText(text)

    def showPlayOrExitMenu(self):
        text = 'Play again?'
        self.addText(text)

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
    
        if self.player1.freezeRoundResult:
            self.addText(timeValue, textScale=4, textThickness=8)

    def showTwoPlayerGameStats(self, elapsedTime, maxReps, currentReps):
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
        timeValueX, timeValueY, _, timeValueHeight = self.getTextPosition(timeValue, self.defaultFont, timeValueScale, timeValueThickness, heightPos='top')
        self.videoManager.addText(timeTitle, (timeTitleX, timeTitleY + timeTitleTopPad), self.defaultFont, timeTitleScale, textColor, timeTitleThickness)
        self.videoManager.addText(timeValue, (timeValueX, timeValueY + timeTitleHeight + timeValueTopPad), self.defaultFont, timeValueScale, textColor, timeValueThickness)

        progTitle = 'PROGRESS'
        progTitleTopPad = 10
        progValueTopPad = progTitleTopPad + 15
        
        progValueP1 = str(currentReps[0]) + '/' + str(maxReps[0])
        progTitleP1X, progTitleP1Y, _, progTitleP1Height = self.getTextPosition(progTitle, self.defaultFont, progTitleScale, progTitleThickness, widthPositionFactor, heightPos='top')
        progValueP1X, progValueP1Y, _, _ = self.getTextPosition(progValueP1, self.defaultFont, progValueScale, progValueThickness, widthPositionFactor, heightPos='top')
        self.videoManager.addText(progTitle, (progTitleP1X, progTitleP1Y + progTitleTopPad), self.defaultFont, progTitleScale, textColor, progTitleThickness)
        self.videoManager.addText(progValueP1, (progValueP1X, progValueP1Y + progTitleP1Height + progValueTopPad), self.defaultFont, progValueScale, textColor, progValueThickness)

        progValueP2 = str(currentReps[1]) + '/' + str(maxReps[1])
        progTitleP2X, progTitleP2Y, _, progTitleP2Height = self.getTextPosition(progTitle, self.defaultFont, progTitleScale, progTitleThickness, widthPositionFactor, widthPos='right', heightPos='top')
        progValueP2X, progValueP2Y, _, _ = self.getTextPosition(progValueP2, self.defaultFont, progValueScale, progValueThickness, widthPositionFactor, widthPos='right', heightPos='top')
        self.videoManager.addText(progTitle, (progTitleP2X, progTitleP2Y + progTitleTopPad), self.defaultFont, progTitleScale, textColor, progTitleThickness)
        self.videoManager.addText(progValueP2, (progValueP2X, progValueP2Y + progTitleP2Height + progValueTopPad), self.defaultFont, progValueScale, textColor, progValueThickness)
        
        splitLine1Pt1 = (int(self.videoManager.frameWidth/2), 0)
        splitLine1Pt2 = (int(self.videoManager.frameWidth/2), timeTitleY - timeTitleHeight - 5)
        splitLine2Pt1 = (int(self.videoManager.frameWidth/2), timeValueY + timeValueHeight + 30)
        splitLine2Pt2 = (int(self.videoManager.frameWidth/2), int(self.videoManager.frameHeight))
        self.videoManager.addLine(splitLine1Pt1, splitLine1Pt2, (255, 255, 255), thickness=self.twoPlayerSplitLineThickness)
        self.videoManager.addLine(splitLine2Pt1, splitLine2Pt2, (255, 255, 255), thickness=self.twoPlayerSplitLineThickness)

        winnerText = 'WINNER'
        if self.player1.freezeRoundResult:
            self.addText(winnerText, textScale=3, textThickness=6, widthFactor=2)
        elif self.player2.freezeRoundResult:
            self.addText(winnerText, textScale=3, textThickness=6, widthFactor=2, widthPos='right')

    def showDetectionLabels(self, playerMode, isObjectInPosition, xLeft, yTop, xRight, yBottom, className):
        boxThickness = 6
        boxColor = (0,0,255)
        if isObjectInPosition:
            boxColor = (0, 255, 0)
        elif playerMode == 2:
            middlePos = int(round(self.videoManager.frameWidth/2))
            middlePad = int(round(self.twoPlayerSplitLineThickness/2))
            redBallPositionThreshold = middlePos - middlePad
            blueBallPositionThreshold = middlePos + middlePad
            if className == self.classesToDetect[0]: # red ball
                boxColor = (0, 0, 255)
                if xLeft > redBallPositionThreshold:
                    boxThickness = 0
                elif xRight > redBallPositionThreshold:
                    xRight = redBallPositionThreshold
            elif className == self.classesToDetect[1]: # blue ball
                boxColor = (255, 0, 0)
                if xRight < blueBallPositionThreshold:
                    boxThickness = 0
                elif xLeft < blueBallPositionThreshold:
                    xLeft = blueBallPositionThreshold
        if boxThickness > 0:
            self.videoManager.addRectangle((xLeft, yTop), (xRight, yBottom), boxColor, boxThickness)

    def handleObjectDetected(self, cols, rows, xLeft, yTop, xRight, yBottom, className):
        if self.player1.isActive and self.player1.labelDetections and className == self.classesToDetect[0]:
            xLeftDiff, yTopDiff, xRightDiff, yBottomDiff = self.getGameRectangleDiff(self.gameRectangles[0], xLeft, yTop, xRight, yBottom)
            self.player1.isObjectInSpot = xLeftDiff < self.trackingThreshold and yTopDiff < self.trackingThreshold and xRightDiff < self.trackingThreshold and yBottomDiff < self.trackingThreshold
            self.showDetectionLabels(self.playerMode, self.player1.isObjectInSpot, xLeft, yTop, xRight, yBottom, className)
            
        if self.player2.isActive and self.player2.labelDetections and className == self.classesToDetect[1]:
            xLeftDiff, yTopDiff, xRightDiff, yBottomDiff = self.getGameRectangleDiff(self.gameRectangles[1], xLeft, yTop, xRight, yBottom)
            self.player2.isObjectInSpot = xLeftDiff < self.trackingThreshold and yTopDiff < self.trackingThreshold and xRightDiff < self.trackingThreshold and yBottomDiff < self.trackingThreshold
            self.showDetectionLabels(self.playerMode, self.player2.isObjectInSpot, xLeft, yTop, xRight, yBottom, className)

    def updateCalibrationParams(self):
        calibrationComplete = False
        self.addText('Hold object in front of screen')
        if self.calibrationStep == 1: # calibrate for smallest object size
            if self.calibrationSubStep == 1:
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

    def updatePlayerParams(self, player, gameRectangle):
        isRoundComplete = player.runStep()
        if player.itemWon:
            if player.roundWon:
                self.audioManager.playAudio(self.audioManager.winLevelAudioKey)
            else:
                self.audioManager.playAudio(self.audioManager.winItemAudioKey)
        elif player.resetItem:
            gameRectangle = None
        return isRoundComplete, gameRectangle

    def updateGameParams(self, playerMode, elapsedTime):
        # TODO: break up this function, too many things going on
        # ====================================================================================================

        isRoundComplete = False
        
        # ----------------------------------------------------------------------------------------------------
        #   UPDATE PLAYER PARAMS
        # ----------------------------------------------------------------------------------------------------

        if self.player1.isActive:
            isRoundComplete, self.gameRectangles[0] = self.updatePlayerParams(self.player1, self.gameRectangles[0])

        if self.player2.isActive:
            isP2RoundComplete, self.gameRectangles[1] = self.updatePlayerParams(self.player2, self.gameRectangles[1])
            isRoundComplete = isRoundComplete or isP2RoundComplete
        
        # ----------------------------------------------------------------------------------------------------
        #   UPDATE GAME RECTANGLES
        # ----------------------------------------------------------------------------------------------------

        if playerMode == 1 and self.gameRectangles[0] == None:
            self.gameRectangles[0] = self.getGameRectangle(self.minObjectSize, (0,self.videoManager.frameWidth), (0,self.videoManager.frameHeight))
        elif playerMode == 2 and (self.gameRectangles[0] == None or self.gameRectangles[1] == None):
            middlePad = int(round(self.twoPlayerSplitLineThickness/2))
            if self.gameRectangles[0] == None:
                xRangeMax = int(round(self.videoManager.frameWidth/2)) - middlePad
                self.gameRectangles[0] = self.getGameRectangle(self.minObjectSize, (0, xRangeMax), (0,self.videoManager.frameHeight))
            
            if self.gameRectangles[1] == None:
                xRangeMin = int(round(self.videoManager.frameWidth/2)) + middlePad
                self.gameRectangles[1] = self.getGameRectangle(self.minObjectSize, (xRangeMin, self.videoManager.frameWidth), (0,self.videoManager.frameHeight))
        
        # ----------------------------------------------------------------------------------------------------
        #   ADD GAME RECTANGLES TO FRAME
        # ----------------------------------------------------------------------------------------------------

        if playerMode == 1 and not self.player1.freezeRoundResult:
            self.videoManager.addRectangle(self.gameRectangles[0].pt1.toTuple(), self.gameRectangles[0].pt2.toTuple(), ((0, 255, 255) if not self.player1.showResult else (0, 255, 0)), 6)
        elif playerMode == 2 and not (self.player1.freezeRoundResult or self.player2.freezeRoundResult):
            self.videoManager.addRectangle(self.gameRectangles[0].pt1.toTuple(), self.gameRectangles[0].pt2.toTuple(), ((0, 255, 255) if not self.player1.showResult else (0, 255, 0)), 6)
            self.videoManager.addRectangle(self.gameRectangles[1].pt1.toTuple(), self.gameRectangles[1].pt2.toTuple(), ((0, 255, 255) if not self.player2.showResult else (0, 255, 0)), 6)

        # ----------------------------------------------------------------------------------------------------
        #   FIND AND LABEL OBJECT DETECTIONS
        # ----------------------------------------------------------------------------------------------------

        objectDetectionHandler = lambda cols, rows, xLeft, yTop, xRight, yBottom, className : self.handleObjectDetected(cols, rows, xLeft, yTop, xRight, yBottom, className)

        if playerMode == 1:
            self.videoManager.findDetections(self.classesToDetect[0:1], objectDetectionHandler)
            self.showOnePlayerGameStats(elapsedTime, self.player1.maxRep, self.player1.currentRep)

        elif playerMode == 2:
            self.videoManager.findDetections(self.classesToDetect, objectDetectionHandler)
            self.showTwoPlayerGameStats(elapsedTime, [self.player1.maxRep, self.player2.maxRep], [self.player1.currentRep, self.player2.currentRep])

        return isRoundComplete

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
            objectDetectionHandler = lambda cols, rows, xLeft, yTop, xRight, yBottom, className : self.videoManager.addRectangle((xLeft, yTop), (xRight, yBottom), (0, 255, 255), 3)
            self.videoManager.findDetections(self.classesToDetect[0:1], objectDetectionHandler)
            if isCalibrationComplete:
                self.gameMode = self.gameModeGetPlayers
                print('Switching game mode:', self.gameMode)
        
        elif self.gameMode == self.gameModeGetPlayers:
            self.videoManager.readNewFrame()
            self.showPlayerModeMenu()
            if cmd == 49 or cmd == 50: # 1 or 2
                if cmd == 49: # 1
                    self.playerMode = 1
                    self.player1.reset(True)
                    self.player2.reset()
                elif cmd == 50: # 2
                    self.playerMode = 2
                    self.player1.reset(True)
                    self.player2.reset(True)
                self.gameMode = self.gameModeCountdown
                print('Switching game mode:', self.gameMode)
        
        elif self.gameMode == self.gameModeCountdown:
            self.videoManager.readNewFrame()
            isCountdownComplete = self.runGameCountdown()
            if isCountdownComplete:
                self.roundElapsedTime = 0
                self.roundStartTime = time.time()
                self.gameMode = self.gameModePlay
                print('Switching game mode:', self.gameMode)

        elif self.gameMode == self.gameModePlay:
            elapsedTime = int(time.time() - self.roundStartTime)
            self.videoManager.runDetection()
            isRoundComplete = self.updateGameParams(self.playerMode, elapsedTime)
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