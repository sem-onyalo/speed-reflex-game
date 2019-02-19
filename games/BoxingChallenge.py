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

    _defaultGameSettings = {
        "punchCoords": {},
        "combinations": []
    }

    # ##################################################
    #                    PROPERTIES                    
    # ##################################################

    punchCoords = {}
    combinations = []

    awaitPlayTimer = None
    awaitPlayMaxTime = 0
    calibrationTimer = None
    calibrationMaxTime = 0
    hitTargetTimer = None
    hitTargetMaxTime = 0
    gameModeAwaitingPlayTimer = None
    gameModeAwaitingPlayMaxTime = 0
    awaitCalibrationTimer = None
    awaitCalibrationMaxTime = 0

    currentComboIndex = 0
    currentPunchIndex = 0

    currentTarget = None
    isCurrentTargetHit = False
    hitTargetThreshold = 0
    punchBeingCalibrated = None

    debugSetting = 0

    # ##################################################
    #                    CONSTRUCTORS                   
    # ##################################################

    def __init__(self, videoManager, audioManager, playerReps):
        super().__init__(videoManager, audioManager, playerReps)
        self.loadGameSettings()
        self.hitTargetThreshold = 40
        self.awaitPlayMaxTime = 5
        self.hitTargetMaxTime = 0.5
        self.calibrationMaxTime = 7
        self.awaitCalibrationMaxTime = 5
        self.gameModeAwaitingPlayMaxTime = 10

    # ##################################################
    #                GAME SETTINGS METHODS              
    # ##################################################

    def loadGameSettings(self):
        gameSettings = self.getGameSettings(self._gameName, self._defaultGameSettings)
        self.punchCoords = self.loadPunchCoords(gameSettings["punchCoords"])
        self.combinations = self.loadCombinations(gameSettings["combinations"])

    # ##################################################
    #                   HELPER METHODS                  
    # ##################################################

    def loadPunchCoords(self, gameSettings):
        punchCoords = {}
        try:
            print(self._jab, 'coords: ((' + str(gameSettings[self._jab]['pt1']['x']) + ',', str(gameSettings[self._jab]['pt1']['y']) + '),', '(' + str(gameSettings[self._jab]['pt2']['x']) + ',', str(gameSettings[self._jab]['pt2']['y']) + '))')
            print(self._cross, 'coords: ((' + str(gameSettings[self._cross]['pt1']['x']) + ',', str(gameSettings[self._cross]['pt1']['y']) + '),', '(' + str(gameSettings[self._cross]['pt2']['x']) + ',', str(gameSettings[self._cross]['pt2']['y']) + '))')
            print(self._leftHook, 'coords: ((' + str(gameSettings[self._leftHook]['pt1']['x']) + ',', str(gameSettings[self._leftHook]['pt1']['y']) + '),', '(' + str(gameSettings[self._leftHook]['pt2']['x']) + ',', str(gameSettings[self._leftHook]['pt2']['y']) + '))')
            print(self._rightHook, 'coords: ((' + str(gameSettings[self._rightHook]['pt1']['x']) + ',', str(gameSettings[self._rightHook]['pt1']['y']) + '),', '(' + str(gameSettings[self._rightHook]['pt2']['x']) + ',', str(gameSettings[self._rightHook]['pt2']['y']) + '))')
            print(self._leftUppercut, 'coords: ((' + str(gameSettings[self._leftUppercut]['pt1']['x']) + ',', str(gameSettings[self._leftUppercut]['pt1']['y']) + '),', '(' + str(gameSettings[self._leftUppercut]['pt2']['x']) + ',', str(gameSettings[self._leftUppercut]['pt2']['y']) + '))')
            print(self._rightUppercut, 'coords: ((' + str(gameSettings[self._rightUppercut]['pt1']['x']) + ',', str(gameSettings[self._rightUppercut]['pt1']['y']) + '),', '(' + str(gameSettings[self._rightUppercut]['pt2']['x']) + ',', str(gameSettings[self._rightUppercut]['pt2']['y']) + '))')
            
            punchCoords[self._jab] = Rectangle.Rectangle(Point.Point(gameSettings[self._jab]['pt1']['x'], gameSettings[self._jab]['pt1']['y']), Point.Point(gameSettings[self._jab]['pt2']['x'], gameSettings[self._jab]['pt2']['y']))
            punchCoords[self._cross] = Rectangle.Rectangle(Point.Point(gameSettings[self._cross]['pt1']['x'], gameSettings[self._cross]['pt1']['y']), Point.Point(gameSettings[self._cross]['pt2']['x'], gameSettings[self._cross]['pt2']['y']))
            punchCoords[self._leftHook] = Rectangle.Rectangle(Point.Point(gameSettings[self._leftHook]['pt1']['x'], gameSettings[self._leftHook]['pt1']['y']), Point.Point(gameSettings[self._leftHook]['pt2']['x'], gameSettings[self._leftHook]['pt2']['y']))
            punchCoords[self._rightHook] = Rectangle.Rectangle(Point.Point(gameSettings[self._rightHook]['pt1']['x'], gameSettings[self._rightHook]['pt1']['y']), Point.Point(gameSettings[self._rightHook]['pt2']['x'], gameSettings[self._rightHook]['pt2']['y']))
            punchCoords[self._leftUppercut] = Rectangle.Rectangle(Point.Point(gameSettings[self._leftUppercut]['pt1']['x'], gameSettings[self._leftUppercut]['pt1']['y']), Point.Point(gameSettings[self._leftUppercut]['pt2']['x'], gameSettings[self._leftUppercut]['pt2']['y']))
            punchCoords[self._rightUppercut] = Rectangle.Rectangle(Point.Point(gameSettings[self._rightUppercut]['pt1']['x'], gameSettings[self._rightUppercut]['pt1']['y']), Point.Point(gameSettings[self._rightUppercut]['pt2']['x'], gameSettings[self._rightUppercut]['pt2']['y']))
        except:
            print('Error: could not retrieve punch coords from game settings')
            punchCoords = {}.fromkeys(self._punches)

        return punchCoords

    def loadCombinations(self, gameSettings):
        combinations = []
        if isinstance(gameSettings, list) and len(gameSettings) > 0:
            combinations = gameSettings
        else:
            combinations.append([self._jab, self._cross, self._jab, self._cross])

        return combinations

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

    def isPunchCoordsSet(self):
        for punch in self._punches:
            if (self.punchCoords[punch] == None):
                return False
        return True

    def resetPunchCoords(self):
        self.punchCoords = {}.fromkeys(self._punches)

    def changeTarget(self, currentTarget, currentAttempt):
        if currentTarget == None or currentAttempt == None:
            return False

        if self.hitTargetTimer != None:
            return self.hitTargetTimer.isElapsed()

        if not self.isCurrentTargetHit:
            xLeftDiff = abs(currentAttempt.pt1.x - currentTarget.pt1.x)
            yTopDiff = abs(currentAttempt.pt1.y - currentTarget.pt1.y)
            xRightDiff = abs(currentAttempt.pt2.x - currentTarget.pt2.x)
            yBottomDiff = abs(currentAttempt.pt2.y - currentTarget.pt2.y)
            self.isCurrentTargetHit = xLeftDiff < self.hitTargetThreshold and yTopDiff < self.hitTargetThreshold and xRightDiff < self.hitTargetThreshold and yBottomDiff < self.hitTargetThreshold

        if self.isCurrentTargetHit:
            self.hitTargetTimer = Timer.Timer(self.hitTargetMaxTime)

        return False

    def startCountdown_AwaitingPlay(self):
        # TODO: make method generic, not specific to 'gameModeAwaitingPlay'
        self.awaitPlayTimer = Timer.Timer(self.awaitPlayMaxTime)
        self.gameMode = self.gameModeAwaitingPlay

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
            return self.gameModeAwaitingPlay
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

    def play(self):
        self.videoManager.runDetection()

        if self.currentTarget == None:
            self.currentComboIndex = 0
            self.currentPunchIndex = 0
            self.currentTarget = self.punchCoords[self.combinations[self.currentComboIndex][self.currentPunchIndex]]
            
        currentDetections = self.videoManager.findDetections(self._classesToDetect)

        for currentDetection in currentDetections:
            if self.changeTarget(self.currentTarget, currentDetection):
                self.hitTargetTimer = None
                self.isCurrentTargetHit = False

                self.currentPunchIndex = self.currentPunchIndex + 1
                if self.currentPunchIndex >= len(self.combinations[self.currentComboIndex]):
                    self.currentPunchIndex = 0
                    self.currentComboIndex = self.currentComboIndex + 1
                    if self.currentComboIndex >= len(self.combinations):
                        self.currentTarget = None
                        return self.gameModeWin

                self.currentTarget = self.punchCoords[self.combinations[self.currentComboIndex][self.currentPunchIndex]]

        if self.isCurrentTargetHit:
            self.videoManager.addRectangle(self.currentTarget.pt1.toTuple(), self.currentTarget.pt2.toTuple(), self.green, 3)
        else:
            self.videoManager.addRectangle(self.currentTarget.pt1.toTuple(), self.currentTarget.pt2.toTuple(), self.yellow, 3)
            self.addTextToRectangle(self.combinations[self.currentComboIndex][self.currentPunchIndex], self.currentTarget)
            
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
            return self.gameModeAwaitingCalibration
        else:
            if self.debugSetting == 0 or cmd == 49: # 1
                self.debugSetting = 1
            elif cmd == 50: # 2
                self.debugSetting = 2

            self.videoManager.runDetection()
            if self.debugSetting == 1:
                self.addText('findDetections')
                self.videoManager.findDetections(self._classesToDetect, self.getDefaultObjectDetectedHandler(self.red))
            elif self.debugSetting == 2:
                self.addText('findBestAndClosestDetection')
                self.videoManager.findBestAndClosestDetection(self._classesToDetect[0], self.getLabelledObjectDetectedHandler())

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

        elif cmd == 48 or self.gameMode == self.gameModeDebug:
            newGameMode = self.debug(cmd)

        elif self.gameMode == self.gameModeAwaitingCalibration:
            newGameMode = self.awaitCalibration(cmd)
        
        elif self.gameMode == self.gameModeCalibration:
            newGameMode = self.calibrate()

        elif self.gameMode == self.gameModeAwaitingPlay:
            newGameMode = self.awaitPlay(cmd)

        elif self.gameMode == self.gameModePlay:
            newGameMode = self.play()

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