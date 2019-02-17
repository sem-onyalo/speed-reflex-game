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

    _jab = "jab"
    _cross = "cross"
    _leftHook = "left hook"
    _rightHook = "right hook"
    _leftUppercut = "left uppercut"
    _rightUppercut = "right uppercut"
    _gameSettingsFileName = "game.settings.json"
    _classesToDetect = ['boxing gloves']

    _punches = [_jab, _cross, _leftHook, _rightHook, _leftUppercut, _rightUppercut]

    # ##################################################
    #                    PROPERTIES                    
    # ##################################################

    punchCoords = {}
    combinations = []

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

    # ##################################################
    #                    CONSTRUCTORS                   
    # ##################################################

    def __init__(self, videoManager, audioManager, playerReps):
        super().__init__(videoManager, audioManager, playerReps)
        self.loadPunchCoords()
        self.loadCombinations()
        self.hitTargetThreshold = 40
        self.calibrationMaxTime = 7
        self.hitTargetMaxTime = 0.5
        self.awaitCalibrationMaxTime = 3
        self.gameModeAwaitingPlayMaxTime = 10

    # ##################################################
    #                   HELPER METHODS                  
    # ##################################################

    def loadPunchCoords(self):
        try:
            with open(self._gameSettingsFileName, "r") as file:
                gameSettings = json.loads(file.read())

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

    def loadCombinations(self):
        self.combinations.append([
            self._punches[0], self._punches[1], self._punches[0], self._punches[1] # self._jab, self._cross, self._jab, self._cross
        ])

    def savePunchCoords(self, punchCoords):
        gameSettings = {
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

        with open(self._gameSettingsFileName, "w") as file:
            file.write(json.dumps(gameSettings))

    def isPunchCoordsSet(self):
        for punch in self._punches:
            if (self.punchCoords[punch] == None):
                return False
        return True

    def resetPunchCoords(self):
        self.punchCoords = {}.fromkeys(self._punches)

    def getDefaultObjectDetectionHandler(self, color, thickness=3):
        objectDetectionHandler = lambda cols, rows, xLeft, yTop, xRight, yBottom, className : self.videoManager.addRectangle((xLeft, yTop), (xRight, yBottom), color, thickness)
        return objectDetectionHandler

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
                return self.gameModePlay
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

            # TODO: change to "find best and closest detection"
            bestDetection = self.videoManager.findBestDetection(self._classesToDetect[0], self.getDefaultObjectDetectionHandler((0, 0, 255)))

            # TODO: add algorithm to choose best detection out of all attempts, not just last best detection
            if bestDetection != None:
                self.punchCoords[self.punchBeingCalibrated] = bestDetection

            return self.gameMode

    def awaitPlay(self, cmd):
        self.videoManager.readNewFrame()
        self.showAwaitingPlayMenu()
        if cmd == 80 or cmd == 112: # P or p
            return self.gameModePlay
        else:
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
                    self.currentTarget = None
                    return self.gameModeWin
                    # self.currentComboIndex = self.currentComboIndex + 1
                    # if self.currentComboIndex >= len(self.combinations):
                    #     return self.gameModeWin

                self.currentTarget = self.punchCoords[self.combinations[self.currentComboIndex][self.currentPunchIndex]]

        if self.isCurrentTargetHit:
            self.videoManager.addRectangle(self.currentTarget.pt1.toTuple(), self.currentTarget.pt2.toTuple(), (0, 255, 0), 3)
        else:
            self.videoManager.addRectangle(self.currentTarget.pt1.toTuple(), self.currentTarget.pt2.toTuple(), (0, 255, 255), 3)
            
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

    # ##################################################
    #                 GAME PLAY METHODS                 
    # ##################################################

    def runGameStep(self):
        continueRun = True
        newGameMode = self.gameMode
        cmd = self.videoManager.getKeyPress()

        if cmd == 27: # ESC
            continueRun = False

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