import datetime
import random
import time
from core import Player, Point, Rectangle, Timer
from games import Challenge

class BoxingChallenge(Challenge.Challenge):

    classesToDetect = ['boxing gloves']

    punches = ['jab', 'cross', 'left hook', 'right hook', 'left uppercut', 'right uppercut']

    punchCoords = {
        'jab': None,
        'cross': None,
        'left hook': None,
        'right hook': None,
        'left uppercut': None,
        'right uppercut': None
    }

    # Timer vars
    calibrationTimer = None
    punchCalibrationMaxTime = 10

    # ##################################################

    # ##################################################
    #                    CONSTRUCTORS                   
    # ##################################################

    def __init__(self, videoManager, audioManager, playerReps):
        super().__init__(videoManager, audioManager, playerReps)

    # ##################################################
    #                   HELPER METHODS                  
    # ##################################################

    def isPunchCoordsSet(self):
        for punch in self.punches:
            if (self.punchCoords[punch] == None):
                return False
        return True

    def resetPunchCoords(self):
        for punch in self.punches:
            self.punchCoords[punch] = None

    # ##################################################
    #                      METHODS                     
    # ##################################################

    def showAwaitingCalibrationMenu(self):
        text = "Press 'C' to calibrate"
        self.addText(text)

    def showAwaitingPlayMenu(self):
        text = "Press 'P' to play"
        self.addText(text)

    def runGameStep(self):
        continueRun = True
        newGameMode = self.gameMode
        cmd = self.videoManager.getKeyPress()

        if cmd == 27: # ESC
            continueRun = False

        elif self.gameMode == self.gameModeAwaitingCalibration:
            self.videoManager.readNewFrame()
            self.showAwaitingCalibrationMenu()
            if cmd == 67 or cmd == 99: # C or c
                newGameMode = self.gameModeCalibration
        
        elif self.gameMode == self.gameModeCalibration:
            self.videoManager.runDetection()
            currentPunch = None
            for punch in self.punches:
                if self.punchCoords[punch] == None:
                    currentPunch = punch
                    break

            if currentPunch == None and self.isPunchCoordsSet():
                newGameMode = self.gameModeAwaitingPlay
            else:
                self.addText(currentPunch)
                objectDetectionHandler = lambda cols, rows, xLeft, yTop, xRight, yBottom, className : self.videoManager.addRectangle((xLeft, yTop), (xRight, yBottom), (0, 255, 255), 3)
                self.videoManager.findBestDetection(self.classesToDetect[0], objectDetectionHandler)
                
                if self.calibrationTimer == None:
                    self.calibrationTimer = Timer.Timer(self.punchCalibrationMaxTime)
                elif self.calibrationTimer.isElapsed():
                    self.punchCoords[currentPunch] = (self.videoManager.xLeftPos, self.videoManager.xRightPos, self.videoManager.yTopPos, self.videoManager.yBottomPos)
                    self.calibrationTimer = None

        elif self.gameMode == self.gameModeAwaitingPlay:
            self.videoManager.readNewFrame()
            self.showAwaitingPlayMenu()
            if cmd == 80 or cmd == 112: # P or p
                newGameMode = self.gameModePlay

        # elif self.gameMode == self.gameModePlay:
        #     elapsedTime = int(time.time() - self.roundStartTime)
        #     self.videoManager.runDetection()
        #     isRoundComplete = self.updateGameParams(self.playerMode, elapsedTime)
        #     if isRoundComplete:
        #         self.gameMode = self.gameModeAwaitingPlayConfirm
        #         print('Switching game mode:', self.gameMode)

        else:
            raise RuntimeError('Game mode error, current game mode is', self.gameMode)
        
        if newGameMode != self.gameMode:
            print('Switching game mode', self.gameMode, '->', newGameMode)
            self.gameMode = newGameMode
            
        self.videoManager.showImage()
        return continueRun