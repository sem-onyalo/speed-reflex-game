import datetime
import random
import time
from core import Player, Point, Rectangle
from games import Challenge

class BoxingChallenge(Challenge.Challenge):
    # Game mode constants
    gameModeAwaitingCalibration = 'AWCL'
    gameModeAwaitingPlayConfirm = 'AWPL'
    gameModeCalibration = 'CLBT'
    gameModePlay = 'PLAY'

    # ##################################################



    # ##################################################
    #                      METHODS                    
    # ##################################################

    def __init__(self, videoManager, audioManager, playerReps):
        super().__init__(videoManager, audioManager, playerReps)

    def showAwaitingCalibrationMenu(self):
        text = "Press 'C' to calibrate"
        self.addText(text)

    def runGameStep(self):
        continueRun = True
        cmd = self.videoManager.getKeyPress()

        if cmd == 27: # ESC
            continueRun = False

        elif self.gameMode == self.gameModeAwaitingCalibration:
            self.videoManager.readNewFrame()
            self.showAwaitingCalibrationMenu()
            if cmd == 67 or cmd == 99: # C or c
                self.gameMode = self.gameModeCalibration
                print('Switching game mode:', self.gameMode)
        
        # elif self.gameMode == self.gameModeCalibration:
        #     self.videoManager.runDetection()
        #     isCalibrationComplete = self.updateCalibrationParams()
        #     objectDetectionHandler = lambda cols, rows, xLeft, yTop, xRight, yBottom, className : self.videoManager.addRectangle((xLeft, yTop), (xRight, yBottom), (0, 255, 255), 3)
        #     self.videoManager.findDetections(self.classesToDetect[0:1], objectDetectionHandler)
        #     if isCalibrationComplete:
        #         self.gameMode = self.gameModeGetPlayers
        #         print('Switching game mode:', self.gameMode)
        
        # elif self.gameMode == self.gameModeGetPlayers:
        #     self.videoManager.readNewFrame()
        #     self.showPlayerModeMenu()
        #     if cmd == 49 or cmd == 50: # 1 or 2
        #         if cmd == 49: # 1
        #             self.playerMode = 1
        #             self.player1.reset(True)
        #             self.player2.reset()
        #         elif cmd == 50: # 2
        #             self.playerMode = 2
        #             self.player1.reset(True)
        #             self.player2.reset(True)
        #         self.gameMode = self.gameModeCountdown
        #         print('Switching game mode:', self.gameMode)
        
        # elif self.gameMode == self.gameModeCountdown:
        #     self.videoManager.readNewFrame()
        #     isCountdownComplete = self.runGameCountdown()
        #     if isCountdownComplete:
        #         self.roundElapsedTime = 0
        #         self.roundStartTime = time.time()
        #         self.gameMode = self.gameModePlay
        #         print('Switching game mode:', self.gameMode)

        # elif self.gameMode == self.gameModePlay:
        #     elapsedTime = int(time.time() - self.roundStartTime)
        #     self.videoManager.runDetection()
        #     isRoundComplete = self.updateGameParams(self.playerMode, elapsedTime)
        #     if isRoundComplete:
        #         self.gameMode = self.gameModeAwaitingPlayConfirm
        #         print('Switching game mode:', self.gameMode)

        # elif self.gameMode == self.gameModeAwaitingPlayConfirm:
        #     self.videoManager.readNewFrame()
        #     self.showPlayOrExitMenu()
        #     if cmd == 78 or cmd == 110: # N or n
        #         continueRun = False
        #     elif cmd == 89 or cmd == 121: # Y or y
        #         self.gameMode = self.gameModeGetPlayers
        #         print('Switching game mode:', self.gameMode)

        # else:
        #     raise RuntimeError('Game mode error, current game mode is', self.gameMode)
        
        self.videoManager.showImage()
        return continueRun