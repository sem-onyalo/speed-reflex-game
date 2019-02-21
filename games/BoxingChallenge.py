import datetime
import json
import os
import random
import time
from core import Player, Point, Rectangle, Timer
from games import Challenge

class BoxingChallenge(Challenge.Challenge):

    # ##################################################
    #                     CONSTANTS                    
    # ##################################################

    _gameName = "boxingChallenge"

    _jab = "jab"
    _cross = "cross"
    _leftHook = "left hook"
    _rightHook = "right hook"
    _leftUppercut = "left uppercut"
    _rightUppercut = "right uppercut"
    _classesToDetect = ['boxing gloves']

    _punches = [_jab, _cross, _leftHook, _rightHook, _leftUppercut, _rightUppercut]

    _hitTargetType_MinMaxRegion = 1
    _hitTargetType_MinRegion = 2

    _defaultGameSettings = {
        "preferences": {
            "hitTargetType": 1,
            "hitTargetThreshold": 0,
            "detectionScoreThreshold": 0,
            "showTargetThresholdBoundingBox": False,
            "showClassDetectionBoundingBoxesDuringGamePlay": False,
            "freezeBoundingBoxesAndWaitForUserInputWhenTargetHit": False
        },
        "timerVars": {
            "awaitPlayMaxTime": 5,
            "hitTargetMaxTime": 0.5,
            "calibrationMaxTime": 7,
            "awaitCalibrationMaxTime": 5,
            "gameModeAwaitingPlayMaxTime": 10
        },
        "punchCoords": {},
        "combinations": []
    }

    # ##################################################
    #                    PROPERTIES                    
    # ##################################################

    gameSettings = {}
    punchCoords = {}
    combinations = []

    awaitPlayMaxTime = 0
    hitTargetMaxTime = 0
    calibrationMaxTime = 0
    awaitCalibrationMaxTime = 0
    gameModeAwaitingPlayMaxTime = 0

    awaitPlayTimer = None
    hitTargetTimer = None
    calibrationTimer = None
    awaitCalibrationTimer = None
    gameModeAwaitingPlayTimer = None
    
    currentComboIndex = 0
    currentPunchIndex = 0

    currentTarget = None
    successfulAttempt = None
    punchBeingCalibrated = None

    isCurrentTargetHit = False
    hitTargetThreshold = 0

    debugSetting = 0

    # ##################################################
    #                    CONSTRUCTORS                   
    # ##################################################

    def __init__(self, videoManager, audioManager, playerReps):
        super().__init__(videoManager, audioManager, playerReps)
        self.loadGameSettings()

    # ##################################################
    #                GAME SETTINGS METHODS              
    # ##################################################

    def loadGameSettings(self):
        print('\nLoading game settings')
        self.gameSettings = self.getGameSettings(self._gameName, self._defaultGameSettings)
        self.loadPunchCoords(self.gameSettings["punchCoords"])
        self.loadCombinations(self.gameSettings["combinations"])
        self.loadTimerVars(self.gameSettings["timerVars"])
        self.loadThresholdSettings(self.gameSettings["preferences"])
        print('Load complete\n\n')

    def loadThresholdSettings(self, gameSettings):
        if "hitTargetThreshold" in gameSettings and gameSettings["hitTargetThreshold"] > 0:
            self.hitTargetThreshold = int(gameSettings["hitTargetThreshold"])
        else:
            self.hitTargetThreshold = self.videoManager.trackingThreshold

        if "detectionScoreThreshold" in gameSettings and gameSettings["detectionScoreThreshold"] > 0:
            self.videoManager.scoreThreshold = float(gameSettings["detectionScoreThreshold"])

        print('scoreThreshold:', self.videoManager.scoreThreshold, 'hitTargetThreshold:', self.hitTargetThreshold)

    def loadTimerVars(self, gameSettings):
        self.awaitPlayMaxTime = gameSettings["awaitPlayMaxTime"]
        self.hitTargetMaxTime = gameSettings["hitTargetMaxTime"]
        self.calibrationMaxTime = gameSettings["calibrationMaxTime"]
        self.awaitCalibrationMaxTime = gameSettings["awaitCalibrationMaxTime"]
        self.gameModeAwaitingPlayMaxTime = gameSettings["gameModeAwaitingPlayMaxTime"]
        print('awaitPlayMaxTime:', self.awaitPlayMaxTime, 'hitTargetMaxTime:', self.hitTargetMaxTime, 'calibrationMaxTime:', self.calibrationMaxTime, 'awaitCalibrationMaxTime:', self.awaitCalibrationMaxTime, 'gameModeAwaitingPlayMaxTime:', self.gameModeAwaitingPlayMaxTime)

    def loadPunchCoords(self, gameSettings):
        try:
            print(self._jab, 'coords: ((' + str(gameSettings[self._jab]['pt1']['x']) + ',', str(gameSettings[self._jab]['pt1']['y']) + '),', '(' + str(gameSettings[self._jab]['pt2']['x']) + ',', str(gameSettings[self._jab]['pt2']['y']) + '))')
            print(self._cross, 'coords: ((' + str(gameSettings[self._cross]['pt1']['x']) + ',', str(gameSettings[self._cross]['pt1']['y']) + '),', '(' + str(gameSettings[self._cross]['pt2']['x']) + ',', str(gameSettings[self._cross]['pt2']['y']) + '))')
            print(self._leftHook, 'coords: ((' + str(gameSettings[self._leftHook]['pt1']['x']) + ',', str(gameSettings[self._leftHook]['pt1']['y']) + '),', '(' + str(gameSettings[self._leftHook]['pt2']['x']) + ',', str(gameSettings[self._leftHook]['pt2']['y']) + '))')
            print(self._rightHook, 'coords: ((' + str(gameSettings[self._rightHook]['pt1']['x']) + ',', str(gameSettings[self._rightHook]['pt1']['y']) + '),', '(' + str(gameSettings[self._rightHook]['pt2']['x']) + ',', str(gameSettings[self._rightHook]['pt2']['y']) + '))')
            print(self._leftUppercut, 'coords: ((' + str(gameSettings[self._leftUppercut]['pt1']['x']) + ',', str(gameSettings[self._leftUppercut]['pt1']['y']) + '),', '(' + str(gameSettings[self._leftUppercut]['pt2']['x']) + ',', str(gameSettings[self._leftUppercut]['pt2']['y']) + '))')
            print(self._rightUppercut, 'coords: ((' + str(gameSettings[self._rightUppercut]['pt1']['x']) + ',', str(gameSettings[self._rightUppercut]['pt1']['y']) + '),', '(' + str(gameSettings[self._rightUppercut]['pt2']['x']) + ',', str(gameSettings[self._rightUppercut]['pt2']['y']) + '))')
            
            self.punchCoords[self._jab] = Rectangle.Rectangle(Point.Point(gameSettings[self._jab]['pt1']['x'], gameSettings[self._jab]['pt1']['y']), Point.Point(gameSettings[self._jab]['pt2']['x'], gameSettings[self._jab]['pt2']['y']))
            self.punchCoords[self._cross] = Rectangle.Rectangle(Point.Point(gameSettings[self._cross]['pt1']['x'], gameSettings[self._cross]['pt1']['y']), Point.Point(gameSettings[self._cross]['pt2']['x'], gameSettings[self._cross]['pt2']['y']))
            self.punchCoords[self._leftHook] = Rectangle.Rectangle(Point.Point(gameSettings[self._leftHook]['pt1']['x'], gameSettings[self._leftHook]['pt1']['y']), Point.Point(gameSettings[self._leftHook]['pt2']['x'], gameSettings[self._leftHook]['pt2']['y']))
            self.punchCoords[self._rightHook] = Rectangle.Rectangle(Point.Point(gameSettings[self._rightHook]['pt1']['x'], gameSettings[self._rightHook]['pt1']['y']), Point.Point(gameSettings[self._rightHook]['pt2']['x'], gameSettings[self._rightHook]['pt2']['y']))
            self.punchCoords[self._leftUppercut] = Rectangle.Rectangle(Point.Point(gameSettings[self._leftUppercut]['pt1']['x'], gameSettings[self._leftUppercut]['pt1']['y']), Point.Point(gameSettings[self._leftUppercut]['pt2']['x'], gameSettings[self._leftUppercut]['pt2']['y']))
            self.punchCoords[self._rightUppercut] = Rectangle.Rectangle(Point.Point(gameSettings[self._rightUppercut]['pt1']['x'], gameSettings[self._rightUppercut]['pt1']['y']), Point.Point(gameSettings[self._rightUppercut]['pt2']['x'], gameSettings[self._rightUppercut]['pt2']['y']))
        except:
            print('Error: could not retrieve punch coords from game settings')
            self.punchCoords = {}.fromkeys(self._punches)

    def loadCombinations(self, gameSettings):
        if isinstance(gameSettings, list) and len(gameSettings) > 0:
            self.combinations = gameSettings
        else:
            self.combinations.append([self._jab, self._cross, self._jab, self._cross])

    def savePunchCoords(self, punchCoords):
        gameSettings = self.getGameSettings(self._gameName, self._defaultGameSettings)

        gameSettings["punchCoords"] = {
            self._jab: {
                "pt1": {
                    "x": punchCoords[self._jab].pt1.x,
                    "y": punchCoords[self._jab].pt1.y
                },
                "pt2": {
                    "x": punchCoords[self._jab].pt2.x,
                    "y": punchCoords[self._jab].pt2.y
                }
            },
            self._cross: {
                "pt1": {
                    "x": punchCoords[self._cross].pt1.x,
                    "y": punchCoords[self._cross].pt1.y
                },
                "pt2": {
                    "x": punchCoords[self._cross].pt2.x,
                    "y": punchCoords[self._cross].pt2.y
                }
            },
            self._leftHook: {
                "pt1": {
                    "x": punchCoords[self._leftHook].pt1.x,
                    "y": punchCoords[self._leftHook].pt1.y
                },
                "pt2": {
                    "x": punchCoords[self._leftHook].pt2.x,
                    "y": punchCoords[self._leftHook].pt2.y
                }
            },
            self._rightHook: {
                "pt1": {
                    "x": punchCoords[self._rightHook].pt1.x,
                    "y": punchCoords[self._rightHook].pt1.y
                },
                "pt2": {
                    "x": punchCoords[self._rightHook].pt2.x,
                    "y": punchCoords[self._rightHook].pt2.y
                }
            },
            self._leftUppercut: {
                "pt1": {
                    "x": punchCoords[self._leftUppercut].pt1.x,
                    "y": punchCoords[self._leftUppercut].pt1.y
                },
                "pt2": {
                    "x": punchCoords[self._leftUppercut].pt2.x,
                    "y": punchCoords[self._leftUppercut].pt2.y
                }
            },
            self._rightUppercut: {
                "pt1": {
                    "x": punchCoords[self._rightUppercut].pt1.x,
                    "y": punchCoords[self._rightUppercut].pt1.y
                },
                "pt2": {
                    "x": punchCoords[self._rightUppercut].pt2.x,
                    "y": punchCoords[self._rightUppercut].pt2.y
                }
            }
        }

        self.setGameSettings(self._gameName, gameSettings)

    # ##################################################
    #                   HELPER METHODS                  
    # ##################################################

    def isPunchCoordsSet(self):
        for punch in self._punches:
            if (self.punchCoords[punch] == None):
                return False
        return True

    def resetPunchCoords(self):
        self.punchCoords = {}.fromkeys(self._punches)

    def isTargetHit(self, currentTarget, currentAttempt, hitTargetThreshold):
        if currentTarget == None or currentAttempt == None:
            return False
        elif self.isCurrentTargetHit:
            return True
        else:
            if self.gameSettings["preferences"]["hitTargetType"] == self._hitTargetType_MinMaxRegion:
                xLeftDiff = abs(currentAttempt.pt1.x - currentTarget.pt1.x)
                yTopDiff = abs(currentAttempt.pt1.y - currentTarget.pt1.y)
                xRightDiff = abs(currentAttempt.pt2.x - currentTarget.pt2.x)
                yBottomDiff = abs(currentAttempt.pt2.y - currentTarget.pt2.y)
                return xLeftDiff < hitTargetThreshold and yTopDiff < hitTargetThreshold and xRightDiff < hitTargetThreshold and yBottomDiff < hitTargetThreshold
            if self.gameSettings["preferences"]["hitTargetType"] == self._hitTargetType_MinRegion:
                isWithinPt1 = currentAttempt.pt1.x > (currentTarget.pt1.x - hitTargetThreshold) and currentAttempt.pt1.y > (currentTarget.pt1.y - hitTargetThreshold)
                isWithinPt2 = currentAttempt.pt2.x < (currentTarget.pt2.x + hitTargetThreshold) and currentAttempt.pt2.y < (currentTarget.pt2.y + hitTargetThreshold)
                return isWithinPt1 and isWithinPt2
            else:
                raise RuntimeError('Game settings error: hit target type', self.gameSettings["preferences"]["hitTargetType"], 'is invalid')

    def startCountdown_AwaitingPlay(self):
        # TODO: make method generic, not specific to 'gameModeAwaitingPlay'
        self.awaitPlayTimer = Timer.Timer(self.awaitPlayMaxTime)
        self.gameMode = self.gameModeAwaitingPlay

    def showTargetThresholdBoundingBoxes(self, currentTarget, hitTargetThreshold):
        outerThreshPt1 = Point.Point(currentTarget.pt1.x - hitTargetThreshold, currentTarget.pt1.y - hitTargetThreshold)
        outerThreshPt2 = Point.Point(currentTarget.pt2.x + hitTargetThreshold, currentTarget.pt2.y + hitTargetThreshold)
        self.videoManager.addRectangle(outerThreshPt1.toTuple(), outerThreshPt2.toTuple(), self.purple, 3)
        if self.gameSettings["preferences"]["hitTargetType"] == self._hitTargetType_MinMaxRegion:
            innerThreshPt1 = Point.Point(currentTarget.pt1.x + hitTargetThreshold, currentTarget.pt1.y + hitTargetThreshold)
            innerThreshPt2 = Point.Point(currentTarget.pt2.x - hitTargetThreshold, currentTarget.pt2.y - hitTargetThreshold)
            self.videoManager.addRectangle(innerThreshPt1.toTuple(), innerThreshPt2.toTuple(), self.purple, 3)

    def showTarget(self, target, text):
        self.videoManager.addRectangle(target.pt1.toTuple(), target.pt2.toTuple(), self.yellow, 3)
        self.addTextToRectangle(text, target)

    # ##################################################
    #              OBJECT DETECTED HANDLERS             
    # ##################################################

    def getDefaultObjectDetectedHandler(self, color, thickness=3):
        objectDetectedHandler = lambda cols, rows, xLeft, yTop, xRight, yBottom, className : self.videoManager.addRectangle((xLeft, yTop), (xRight, yBottom), color, thickness)
        return objectDetectedHandler

    def getLabelledObjectDetectedHandler(self):
        objectDetectedHandler = lambda cols, rows, xLeft, yTop, xRight, yBottom, className, score : self.labelAndBoundDetectedObjects(cols, rows, xLeft, yTop, xRight, yBottom, className, score)
        return objectDetectedHandler

    def getBestObjectDetectedHandler(self):
        objectDetectedHandler = lambda cols, rows, xLeft, yTop, xRight, yBottom, className, score : self.labelBestDetectedObject(cols, rows, xLeft, yTop, xRight, yBottom, className, score)
        return objectDetectedHandler

    def labelAndBoundDetectedObjects(self, cols, rows, xLeft, yTop, xRight, yBottom, className, score):
        label = className + ": " + str(int(round(score * 100))) + '%'
        self.videoManager.addRectangle((xLeft, yTop), (xRight, yBottom), self.yellow, 3)
        self.videoManager.addLabel(label, xLeft, yTop)

    def labelBestDetectedObject(self, cols, rows, xLeft, yTop, xRight, yBottom, className, scoreIsIgnoredForNow):
        self.videoManager.addRectangle((xLeft, yTop), (xRight, yBottom), self.yellow, 3)

    # ##################################################
    #                    MENU METHODS                   
    # ##################################################

    def showAwaitingCalibrationMenu(self):
        text = "Press 'C' to calibrate"
        self.addText(text)

    def showAwaitingCalibrationOrPlayMenu(self):
        text = "Press 'P' to play, 'C' to calibrate"
        self.addText(text)

    def showAwaitingPlayMenu(self):
        text = "Press 'P' to play"
        self.addText(text)

    def showPlayAgainMenu(self):
        text = "Play again (Y/N)?"
        self.addText(text)

    # ##################################################
    #                 GAME MODE METHODS                 
    # ##################################################

    def awaitCalibration(self, cmd):
        self.videoManager.readNewFrame()

        if self.awaitCalibrationTimer != None:
            if self.awaitCalibrationTimer.isElapsed():
                self.awaitCalibrationTimer = None
                return self.gameModeCalibration
            else:
                self.addText(str(self.awaitCalibrationTimer.getElapsed()))
        elif not self.isPunchCoordsSet():
            self.showAwaitingCalibrationMenu()
            if cmd == 67 or cmd == 99: # C or c
                self.awaitCalibrationTimer = Timer.Timer(self.awaitCalibrationMaxTime)
        else:
            self.showAwaitingCalibrationOrPlayMenu()
            if cmd == 80 or cmd == 112: # P or p
                self.startCountdown_AwaitingPlay()
            elif cmd == 67 or cmd == 99: # C or c
                self.resetPunchCoords()
                self.awaitCalibrationTimer = Timer.Timer(self.awaitCalibrationMaxTime)
        
        return self.gameMode

    def calibrate(self):
        self.videoManager.runDetection()

        if self.punchBeingCalibrated == None:
            for punch in self._punches:
                if self.punchCoords[punch] == None:
                    self.punchBeingCalibrated = punch
                    break

        if self.punchBeingCalibrated == None:
            self.savePunchCoords(self.punchCoords)
            return self.gameModeAwaitingCalibration
        else:
            self.addText(self.punchBeingCalibrated)

            if self.calibrationTimer != None and self.calibrationTimer.isElapsed():
                self.calibrationTimer = None
                if self.punchCoords[self.punchBeingCalibrated] == None:
                    print(self.gameMode + ':', 'Resetting timer and re-attempting to retrieve detection for', self.punchBeingCalibrated)
                else:
                    print(self.gameMode + ':', self.punchBeingCalibrated, 'coords: ((' + str(self.punchCoords[self.punchBeingCalibrated].pt1.x) + ',', str(self.punchCoords[self.punchBeingCalibrated].pt1.y) + '),', '(' + str(self.punchCoords[self.punchBeingCalibrated].pt2.x) + ',', str(self.punchCoords[self.punchBeingCalibrated].pt2.y) + '))')
                    self.punchBeingCalibrated = None

            if self.calibrationTimer == None:
                self.calibrationTimer = Timer.Timer(self.calibrationMaxTime)

            bestDetection = self.videoManager.findBestAndClosestDetection(self._classesToDetect[0], self.getBestObjectDetectedHandler())

            # TODO: add algorithm to choose best detection out of all attempts, not just last best detection
            if bestDetection != None:
                self.punchCoords[self.punchBeingCalibrated] = bestDetection

            return self.gameMode

    def awaitPlay(self, cmd):
        self.videoManager.readNewFrame()
        if self.awaitPlayTimer != None:
            if self.awaitPlayTimer.isElapsed():
                self.awaitPlayTimer = None
                return self.gameModePlay
            else:
                self.addText(str(self.awaitPlayTimer.getElapsed()))
        else:
            self.showAwaitingPlayMenu()
            if cmd == 80 or cmd == 112: # P or p
                self.startCountdown_AwaitingPlay()

        return self.gameMode

    def play(self, cmd):
        if cmd == 120: # x
            self.isCurrentTargetHit = False
            self.currentComboIndex = 0
            self.currentPunchIndex = 0
            self.successfulAttempt = None
            self.hitTargetTimer = None
            self.currentTarget = None
            return self.gameModeAwaitingCalibration

        elif self.currentTarget == None:
            self.currentComboIndex = 0
            self.currentPunchIndex = 0
            self.currentTarget = self.punchCoords[self.combinations[self.currentComboIndex][self.currentPunchIndex]]
        
        elif self.hitTargetTimer != None and self.hitTargetTimer.isElapsed():
            self.hitTargetTimer = None
            self.successfulAttempt = None
            self.isCurrentTargetHit = False

            self.currentPunchIndex = self.currentPunchIndex + 1
            if self.currentPunchIndex >= len(self.combinations[self.currentComboIndex]):
                self.currentPunchIndex = 0
                self.currentComboIndex = self.currentComboIndex + 1
                if self.currentComboIndex >= len(self.combinations):
                    self.currentTarget = None
                    return self.gameModeWin

            self.currentTarget = self.punchCoords[self.combinations[self.currentComboIndex][self.currentPunchIndex]]

        self.videoManager.runDetection()
        if self.isCurrentTargetHit:
            self.videoManager.addRectangle(self.currentTarget.pt1.toTuple(), self.currentTarget.pt2.toTuple(), self.green, 3)
            if self.gameSettings["preferences"]["freezeBoundingBoxesAndWaitForUserInputWhenTargetHit"]:
                self.videoManager.addRectangle(self.successfulAttempt.pt1.toTuple(), self.successfulAttempt.pt2.toTuple(), self.red, 3)
                if self.gameSettings["preferences"]["showTargetThresholdBoundingBox"]:
                    self.showTargetThresholdBoundingBoxes(self.currentTarget, self.hitTargetThreshold)
                if cmd == 110: # n
                    self.hitTargetTimer = Timer.Timer(self.hitTargetMaxTime)
        else:
            currentDetections = self.videoManager.findDetections(self._classesToDetect)
            for currentDetection in currentDetections:
                self.isCurrentTargetHit = self.isTargetHit(self.currentTarget, currentDetection, self.hitTargetThreshold)
                if self.isCurrentTargetHit:
                    self.successfulAttempt = currentDetection
                    if not self.gameSettings["preferences"]["freezeBoundingBoxesAndWaitForUserInputWhenTargetHit"]:
                        self.hitTargetTimer = Timer.Timer(self.hitTargetMaxTime)
                        break

                if self.gameSettings["preferences"]["showClassDetectionBoundingBoxesDuringGamePlay"]:
                    self.videoManager.addRectangle(currentDetection.pt1.toTuple(), currentDetection.pt2.toTuple(), self.red, 3)

            if self.gameSettings["preferences"]["showTargetThresholdBoundingBox"]:
                self.showTargetThresholdBoundingBoxes(self.currentTarget, self.hitTargetThreshold)

            self.showTarget(self.currentTarget, self.combinations[self.currentComboIndex][self.currentPunchIndex])
            
        return self.gameMode

    def win(self, cmd):
        self.videoManager.readNewFrame()
        self.showPlayAgainMenu()
        
        if self.gameModeAwaitingPlayTimer == None:
            self.gameModeAwaitingPlayTimer = Timer.Timer(self.gameModeAwaitingPlayMaxTime)

        if self.gameModeAwaitingPlayTimer.isElapsed() or cmd == 89 or cmd == 121: # Y or y
            self.gameModeAwaitingPlayTimer = None
            return self.gameModePlay
        elif cmd == 78 or cmd == 110: # N or n
            return self.gameModeStop
        else:
            return self.gameMode

    def debug(self, cmd):
        if cmd == 120: # x
            self.debugSetting = 0
            self.currentPunchIndex = 0
            self.calibrationTimer = None
            self.punchBeingCalibrated = None
            return self.gameModeAwaitingCalibration
        else:
            if self.debugSetting == 0 or cmd == 49: # 1
                self.debugSetting = 1
            elif cmd == 50: # 2
                self.debugSetting = 2
            elif cmd == 51: # 3
                self.debugSetting = 3

            self.videoManager.runDetection()
            if self.debugSetting == 1:
                self.addText('findDetections')
                self.videoManager.findDetections(self._classesToDetect, self.getDefaultObjectDetectedHandler(self.red))
            elif self.debugSetting == 2:
                self.addText('findBestAndClosestDetection')
                self.videoManager.findBestAndClosestDetection(self._classesToDetect[0], self.getLabelledObjectDetectedHandler())
            elif self.debugSetting == 3:
                self.addText('cycleThroughPunches')
                if self.punchBeingCalibrated == None:
                    self.currentPunchIndex = 0
                    self.punchBeingCalibrated = self.punchCoords[self._punches[self.currentPunchIndex]]

                if cmd == 110: # n
                    self.currentPunchIndex = self.currentPunchIndex + 1
                    if self.currentPunchIndex >= len(self._punches):
                        self.currentPunchIndex = 0
                    self.punchBeingCalibrated = self.punchCoords[self._punches[self.currentPunchIndex]]
                
                self.showTarget(self.punchBeingCalibrated, self._punches[self.currentPunchIndex])
                if self.gameSettings["preferences"]["showTargetThresholdBoundingBox"]:
                    self.showTargetThresholdBoundingBoxes(self.punchBeingCalibrated, self.hitTargetThreshold)
                if self.gameSettings["preferences"]["showClassDetectionBoundingBoxesDuringGamePlay"]:
                    currentDetections = self.videoManager.findDetections(self._classesToDetect)
                    for currentDetection in currentDetections:
                        self.videoManager.addRectangle(currentDetection.pt1.toTuple(), currentDetection.pt2.toTuple(), self.red, 3)

            return self.gameModeDebug

    # ##################################################
    #                 GAME PLAY METHODS                 
    # ##################################################

    def runGameStep(self):
        continueRun = True
        newGameMode = self.gameMode
        cmd = self.videoManager.getKeyPress()

        if cmd == 27: # ESC
            continueRun = False

        if cmd == 114: # r:
            self.loadGameSettings()

        elif cmd == 48 or self.gameMode == self.gameModeDebug: # 0
            newGameMode = self.debug(cmd)

        elif self.gameMode == self.gameModeAwaitingCalibration:
            newGameMode = self.awaitCalibration(cmd)
        
        elif self.gameMode == self.gameModeCalibration:
            newGameMode = self.calibrate()

        elif self.gameMode == self.gameModeAwaitingPlay:
            newGameMode = self.awaitPlay(cmd)

        elif self.gameMode == self.gameModePlay:
            newGameMode = self.play(cmd)

        elif self.gameMode == self.gameModeWin:
            newGameMode = self.win(cmd)

        elif self.gameMode == self.gameModeStop:
            continueRun = False

        else:
            raise RuntimeError('Game mode error, current game mode is', self.gameMode)
        
        if newGameMode != self.gameMode:
            print('Switching game mode', self.gameMode, '->', newGameMode)
            self.gameMode = newGameMode
            
        self.videoManager.showImage()
        return continueRun