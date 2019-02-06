import datetime
import random
import time
from core import Player, Point, Rectangle, Timer
from games import Challenge

class BoxingChallenge(Challenge.Challenge):

    # ##################################################
    #                     CONSTANTS                    
    # ##################################################

    classesToDetect = ['boxing gloves']
    punches = ['jab', 'cross', 'left hook', 'right hook', 'left uppercut', 'right uppercut']

    # ##################################################
    #                    PROPERTIES                    
    # ##################################################

    calibrationTimer = None
    calibrationMaxTime = 0
    hitTargetTimer = None
    hitTargetMaxTime = 0

    punchCoords = {}
    combinations = []
    currentTarget = None
    currentPunchIndex = 0
    isCurrentTargetHit = False
    hitTargetThreshold = 0

    # ##################################################
    #                    CONSTRUCTORS                   
    # ##################################################

    def __init__(self, videoManager, audioManager, playerReps):
        super().__init__(videoManager, audioManager, playerReps)
        self.punchCoords = {}.fromkeys(self.punches)
        self.initCombinations()
        self.hitTargetThreshold = 20
        self.calibrationMaxTime = 10
        self.hitTargetMaxTime = 0.5

    # ##################################################
    #                   HELPER METHODS                  
    # ##################################################

    def initCombinations(self):
        self.combinations.append([
            self.punches[0], self.punches[1], self.punches[0], self.punches[1]
        ])

    def isPunchCoordsSet(self):
        for punch in self.punches:
            if (self.punchCoords[punch] == None):
                return False
        return True

    def resetPunchCoords(self):
        for punch in self.punches:
            self.punchCoords[punch] = None

    def getDefaultObjectDetectionHandler(self, color, thickness=3):
        objectDetectionHandler = lambda cols, rows, xLeft, yTop, xRight, yBottom, className : self.videoManager.addRectangle((xLeft, yTop), (xRight, yBottom), color, thickness)
        return objectDetectionHandler

    # ##################################################
    #                    MENU METHODS                   
    # ##################################################

    def showAwaitingCalibrationMenu(self):
        text = "Press 'C' to calibrate"
        self.addText(text)

    def showAwaitingPlayMenu(self):
        text = "Press 'P' to play"
        self.addText(text)

    # ##################################################
    #                 GAME MODE METHODS                 
    # ##################################################

    def awaitCalibration(self, cmd):
        self.videoManager.readNewFrame()
        self.showAwaitingCalibrationMenu()
        if cmd == 67 or cmd == 99: # C or c
            return self.gameModeCalibration
        else:
            return self.gameMode

    def calibrate(self):
        self.videoManager.runDetection()
        currentPunch = None
        for punch in self.punches:
            if self.punchCoords[punch] == None:
                currentPunch = punch
                break

        if currentPunch == None and self.isPunchCoordsSet():
            return self.gameModeAwaitingPlay
        else:
            self.addText(currentPunch)
            # TODO: change to "find best and closest detection"
            self.videoManager.findBestDetection(self.classesToDetect[0], self.getDefaultObjectDetectionHandler((0, 0, 255)))
            
            if self.calibrationTimer == None:
                self.calibrationTimer = Timer.Timer(self.calibrationMaxTime)
            elif self.calibrationTimer.isElapsed():
                self.punchCoords[currentPunch] = Rectangle.Rectangle(Point.Point(self.videoManager.xLeftPos, self.videoManager.yTopPos), Point.Point(self.videoManager.xRightPos, self.videoManager.yBottomPos))
                self.calibrationTimer = None

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
        # rect = Rectangle.Rectangle(Point.Point(xLeft,yTop), Point.Point(xRight,yBottom))
        # self.videoManager.addRectangle(rect.pt1.toTuple(), rect.pt2.toTuple(), (0, 255, 255), 6)

        # ---------------------------------------------------------------------------------------------
        
        # xLeftDiff, yTopDiff, xRightDiff, yBottomDiff = self.getGameRectangleDiff(self.gameRectangles[0], xLeft, yTop, xRight, yBottom)
        # self.player1.isObjectInSpot = xLeftDiff < self.hitTargetThreshold and yTopDiff < self.hitTargetThreshold and xRightDiff < self.hitTargetThreshold and yBottomDiff < self.hitTargetThreshold
        # self.showDetectionLabels(self.playerMode, self.player1.isObjectInSpot, xLeft, yTop, xRight, yBottom, className)

        # ---------------------------------------------------------------------------------------------
        
        # if self.currentPunchIndex == None:
        #     self.currentPunchIndex = 0
        # else:

        # iii = 0
        # for combo in self.combinations[iii]:
        #     for punch in range(len(combo)):

        return self.gameMode

    # ##################################################

    # def changeTarget(self, currentAttempt):
    #     currentTarget = self.currentTarget

    #     if currentTarget == None or currentAttempt == None:
    #         return False

    #     if self.hitTargetTimer != None:
    #         if self.hitTargetTimer.isElapsed():
    #             self.hitTargetTimer = None
    #             self.isCurrentTargetHit = False
    #             return True
    #         else:
    #             return False

    #     if not self.isCurrentTargetHit:
    #         xLeftDiff = abs(currentAttempt.pt1.x - currentTarget.pt1.x)
    #         yTopDiff = abs(currentAttempt.pt1.y - currentTarget.pt1.y)
    #         xRightDiff = abs(currentAttempt.pt2.x - currentTarget.pt2.x)
    #         yBottomDiff = abs(currentAttempt.pt2.y - currentTarget.pt2.y)
    #         self.isCurrentTargetHit = xLeftDiff < self.hitTargetThreshold and yTopDiff < self.hitTargetThreshold and xRightDiff < self.hitTargetThreshold and yBottomDiff < self.hitTargetThreshold

    #     if self.isCurrentTargetHit:
    #         self.hitTargetTimer = Timer.Timer(self.hitTargetMaxTime)

    #     return False

    # def showDetectionLabels(self, playerMode, isObjectInPosition, xLeft, yTop, xRight, yBottom, className):
    #     boxThickness = 6
    #     boxColor = (0,0,255)
    #     if isObjectInPosition:
    #         boxColor = (0, 255, 0)
    #     elif playerMode == 2:
    #         middlePos = int(round(self.videoManager.frameWidth/2))
    #         middlePad = int(round(self.twoPlayerSplitLineThickness/2))
    #         redBallPositionThreshold = middlePos - middlePad
    #         blueBallPositionThreshold = middlePos + middlePad
    #         if className == self.classesToDetect[0]: # red ball
    #             boxColor = (0, 0, 255)
    #             if xLeft > redBallPositionThreshold:
    #                 boxThickness = 0
    #             elif xRight > redBallPositionThreshold:
    #                 xRight = redBallPositionThreshold
    #         elif className == self.classesToDetect[1]: # blue ball
    #             boxColor = (255, 0, 0)
    #             if xRight < blueBallPositionThreshold:
    #                 boxThickness = 0
    #             elif xLeft < blueBallPositionThreshold:
    #                 xLeft = blueBallPositionThreshold
    #     if boxThickness > 0:
    #         self.videoManager.addRectangle((xLeft, yTop), (xRight, yBottom), boxColor, boxThickness)

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

        else:
            raise RuntimeError('Game mode error, current game mode is', self.gameMode)
        
        if newGameMode != self.gameMode:
            print('Switching game mode', self.gameMode, '->', newGameMode)
            self.gameMode = newGameMode
            
        self.videoManager.showImage()
        return continueRun