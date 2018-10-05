#!/usr/bin/env python

import argparse
import cv2 as cv
import datetime
import pyaudio
import random
import threading
import time
import wave

_gameName = 'Speed Reflex Game'
_winGameText = 'YOU WIN!'
_winItemAudioKey = "winItem"
_winLevelAudioKey = "winLevel"

netModels = [
    {
        'modelPath': 'models/mobilenet_ssd_v1_balls/transformed_frozen_inference_graph.pb',
        'configPath': 'models/mobilenet_ssd_v1_balls/ssd_mobilenet_v1_balls_2018_05_20.pbtxt',
        'classNames': {
            0: 'background', 1: 'red ball', 2: 'blue ball'
        }
    }
]

class AudioHelper:
    audioFiles = {
        "winItem": "audio/220184__gameaudio__win-spacey.wav",
        "winLevel": "audio/258142__tuudurt__level-win.wav"
    }
    audioStatus = {
        "winItem": False,
        "winLevel": False
    }

    def _playAudio(self, audioName):
        self.audioStatus[audioName] = True
        wf = wave.open(self.audioFiles[audioName], 'rb')
        pa = pyaudio.PyAudio()
        stream = pa.open(format = pa.get_format_from_width(wf.getsampwidth()),
                        channels = wf.getnchannels(),
                        rate = wf.getframerate(),
                        output = True)

        chunk = 1024
        data = wf.readframes(chunk)
        while len(data) > 0:
            stream.write(data)
            data = wf.readframes(chunk)

        stream.stop_stream()
        stream.close()
        pa.terminate()
        self.audioStatus[audioName] = False

    def playAudio(self, name):
        playAudioThread = threading.Thread(target=self._playAudio, args=[name])
        playAudioThread.start()

class ObjectDetector:
    imgMargin = 60
    img = None
    netModel = None
    detections = None
    scoreThreshold = None
    trackingThreshold = None
    xLeftPos = None
    xRightPos = None
    yTopPos = None
    yBottomPos = None
    frameWidth = 0
    frameHeight = 0

    def __init__(self, netModel, scoreThreshold, trackingThreshold):
        self.netModel = netModel
        self.scoreThreshold = scoreThreshold
        self.trackingThreshold = trackingThreshold
        self.cvNet = cv.dnn.readNetFromTensorflow(self.netModel['modelPath'], self.netModel['configPath'])
        self.create_capture()

    def getImage(self):
        return self.img

    def getXCoordDetectionDiff(self):
        return self.xRightPos - self.xLeftPos if self.xRightPos != None and self.xLeftPos != None else None

    def getYCoordDetectionDiff(self):
        return self.yBottomPos - self.yTopPos if self.yBottomPos != None and self.yTopPos != None else None

    def create_capture(self, source = 0):
        self.cap = cv.VideoCapture(source)
        if self.cap is None or not self.cap.isOpened():
            raise RuntimeError('Warning: unable to open video source: ', source)
        self.frameWidth = int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH))
        self.frameHeight = int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))

    def runDetection(self):
        _, self.img = self.cap.read()
        self.cvNet.setInput(cv.dnn.blobFromImage(self.img, 1.0/127.5, (300, 300), (127.5, 127.5, 127.5), swapRB=True, crop=False))
        self.detections = self.cvNet.forward()

    def labelDetections(self, className, trackingFunc, label=None):
        rows = self.img.shape[0]
        cols = self.img.shape[1]
        isObjectInPosition = False
        self.xLeftPos = None
        self.xRightPos = None
        self.yTopPos = None
        self.yBottomPos = None
        for detection in self.detections[0,0,:,:]:
            score = float(detection[2])
            class_id = int(detection[1])
            if score > self.scoreThreshold and className == self.netModel['classNames'][class_id]:
                self.xLeftPos = int(detection[3] * cols) # marginLeft
                self.yTopPos = int(detection[4] * rows) # marginTop
                self.xRightPos = int(detection[5] * cols)
                self.yBottomPos = int(detection[6] * rows)
                isObjectInPosition = trackingFunc(cols, rows, self.xLeftPos, self.yTopPos, self.xRightPos, self.yBottomPos)
                boxColor = (0, 255, 0) if isObjectInPosition else (0, 0, 255)
                cv.rectangle(self.img, (self.xLeftPos, self.yTopPos), (self.xRightPos, self.yBottomPos), boxColor, thickness=6)
        if label != None:
            xPadding = 20
            if label == _winGameText:
                xPadding = 200
            cv.putText(self.img, label, (int(cols/2) - xPadding, int(rows/2)), cv.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), thickness=7)

        # cv.line(self.img, (0,self.imgMargin), (cols,self.imgMargin), (0, 0, 255), thickness=2)
        # cv.line(self.img, (0,rows-self.imgMargin), (cols,rows-self.imgMargin), (0, 0, 255), thickness=2)
        return isObjectInPosition

class KeepItInTheMiddle:
    trackingThreshold = 50
    maxTime = 5
    showResultMaxTime = 3
    startTime = None
    showResult = False
    startShowResultTime = None
    isObjectInPosition = False
    isWinning = False

    objectDetector = None
    classToDetect = ""

    def __init__(self, objectDetector, classToDetect):
        self.objectDetector = objectDetector
        self.classToDetect = classToDetect

    def updateGameParams(self):
        gameLabel = None
        if self.isWinning and self.isObjectInPosition and self.startTime is not None:
            currentTime = time.time()
            elapsedTime = currentTime - self.startTime
            if self.showResult and self.startShowResultTime is not None:
                gameLabel = _winGameText
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
                    gameLabel = _winGameText
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
        self.objectDetector.runDetection()
        gameLabel = self.updateGameParams()
        
        # Name: trackingFunc 
        # Description: Determines whether the object is in the middle of the screen
        # Code:
        # trackingFunc(cols, rows, xLeft, yTop, xRight, yBottom):
        #   marginRight = cols - xRight
        #   marginBottom = rows - yBottom
        #   xMarginDiff = abs(xLeft - marginRight)
        #   yMarginDiff = abs(yTop - marginBottom)
        #   isObjectInPosition = (xMarginDiff < self.trackingThreshold and yMarginDiff < self.trackingThreshold)
        #   return isObjectInPosition
        trackingFunc = lambda cols, rows, xLeft, yTop, xRight, yBottom : abs(xLeft - (cols - xRight)) < self.trackingThreshold and abs(yTop - (rows - yBottom)) < self.trackingThreshold
        
        self.isObjectInPosition = self.objectDetector.labelDetections(self.classToDetect, trackingFunc, gameLabel)
        return self.objectDetector.getImage()

class MoveItToTheSpot:
    trackingThreshold = 20
    isObjectInPosition = False
    showResult = False
    minObjectSize = None
    maxObjectSize = None
    isCalibrated = False
    calibrationStep = 1
    calibrationSubStep = 1
    calibrationStartTime = None
    calibrationMaxTime = 3
    rectPt1 = None
    rectPt2 = None
    currentRep = 0
    maxRep = 5
    repStartTime = None
    repShowResultStartTime = None
    repShowResultMaxTime = 7
    winLevel = False
    winLevelElapsedTime = 0
    audioHelper = None

    objectDetector = None
    classToDetect = ""

    def __init__(self, objectDetector, classToDetect):
        self.objectDetector = objectDetector
        self.classToDetect = classToDetect
        self.audioHelper = AudioHelper()

    def getRectanglePts(self):
        maxWidth = self.objectDetector.frameWidth
        minHeight = self.objectDetector.imgMargin
        maxHeight = self.objectDetector.frameHeight - self.objectDetector.imgMargin
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
        elapsedTimeStr = str(datetime.timedelta(seconds=elapsedTime))
        elapsedTimeStr = elapsedTimeStr[(elapsedTimeStr.index(':') + 1):]
        return elapsedTimeStr

    def updateCalibrationParams(self):
        if self.calibrationStep == 1: # calibrate for smallest object size
            if self.calibrationSubStep == 1:
                print('Hold object farthest from screen')
                self.calibrationStartTime = time.time()
                self.calibrationSubStep = self.calibrationSubStep + 1
            elif self.calibrationSubStep == 2:
                currentTime = time.time()
                if currentTime - self.calibrationStartTime > self.calibrationMaxTime:
                    xCoordDiff = self.objectDetector.getXCoordDetectionDiff()
                    yCoordDiff = self.objectDetector.getYCoordDetectionDiff()
                    if xCoordDiff != None and yCoordDiff != None:
                        self.minObjectSize = min(int(xCoordDiff), int(yCoordDiff))
                        print('Min obj size:', self.minObjectSize)
                        self.calibrationStep = self.calibrationStep + 1
                        self.calibrationSubStep = 1
                    else:
                        raise RuntimeError('Calibration failed at step', self.calibrationStep, self.calibrationSubStep)
                        
        # elif self.calibrationStep == 2: # calibrate for largest object size
        #     if self.calibrationSubStep == 1:
        #         print('Hold object closest from screen')
        #         self.calibrationStartTime = time.time()
        #         self.calibrationSubStep = self.calibrationSubStep + 1
        #     elif self.calibrationSubStep == 2:
        #         currentTime = time.time()
        #         if currentTime - self.calibrationStartTime > self.calibrationMaxTime:
        #             xCoordDiff = self.objectDetector.getXCoordDetectionDiff()
        #             yCoordDiff = self.objectDetector.getYCoordDetectionDiff()
        #             if xCoordDiff != None and yCoordDiff != None:
        #                 self.maxObjectSize = min(int(xCoordDiff), int(yCoordDiff))
        #                 print('Max obj size:', self.maxObjectSize)
        #                 self.calibrationStep = self.calibrationStep + 1
        #                 self.calibrationSubStep = 1
        #             else:
        #                 raise RuntimeError('Calibration failed at step', self.calibrationStep, self.calibrationSubStep)

        elif self.calibrationStep == 2: # calculate calibration parmas
            self.calibrationSubStep = 1
            self.calibrationStep = 1
            self.isCalibrated = True

    def updateGameParams(self):
        labelDetections = True
        boxColor = (0, 255, 255)
        textColor = (255, 0, 0)
        textSize = 1.5
        textThickness = 3
        textFont = cv.FONT_HERSHEY_SIMPLEX
        elapsedTime = int(time.time() - self.repStartTime) if self.repStartTime != None else 0
        elapsedTimeStr = self.getElapsedTimeStr(elapsedTime)
        if self.rectPt1 == None or self.rectPt2 == None: # initial state, on first run
            self.repStartTime = time.time()
            self.rectPt1, self.rectPt2 = self.getRectanglePts()
        elif self.showResult:
            boxColor = (0, 255, 0)
            if self.winLevel:
                elapsedTime = self.winLevelElapsedTime
                elapsedTimeStr = self.getElapsedTimeStr(elapsedTime)
                if not self.audioHelper.audioStatus[_winLevelAudioKey]:
                    self.rectPt1, self.rectPt2 = self.getRectanglePts()
                    self.repStartTime = time.time()
                    self.winLevelElapsedTime = 0
                    self.showResult = False
                    self.winLevel = False
                    self.currentRep = 0
                else:
                    labelDetections = False
            elif not self.audioHelper.audioStatus[_winItemAudioKey]:
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
                self.winLevel = True
                self.winLevelElapsedTime = elapsedTime
                self.audioHelper.playAudio(_winLevelAudioKey)
            else:
                self.audioHelper.playAudio(_winItemAudioKey)

        cv.rectangle(self.objectDetector.getImage(), self.rectPt1, self.rectPt2, boxColor, thickness=6)
        cv.putText(self.objectDetector.getImage(), str(self.currentRep) + '/' + str(self.maxRep), (self.objectDetector.frameWidth - 150, 100), textFont, textSize, textColor, textThickness, lineType=cv.LINE_AA)
        cv.putText(self.objectDetector.getImage(), elapsedTimeStr, (20, 100), textFont, textSize, textColor, textThickness, lineType=cv.LINE_AA)
        return labelDetections

    def runGameStep(self):
        labelDetections = True
        self.objectDetector.runDetection()

        if self.isCalibrated:
            labelDetections = self.updateGameParams()

            # Name: trackingFunc 
            # Description: Determines whether the object is in the predetermined random spot
            # Code:
            # trackingFunc(cols, rows, xLeft, yTop, xRight, yBottom):
            #   xLeftDiff = abs(xLeft - self.objectDetector.xLeftPos)
            #   yTopDiff = abs(yTop - self.objectDetector.yTopPos)
            #   xRightDiff = abs(xRight - self.objectDetector.xRightPos)
            #   yBottomDiff = abs(yBottom - self.objectDetector.yBottomPos)
            #   isObjectInPosition = xLeftDiff < self.trackingThreshold and yTopDiff < self.trackingThreshold and xRightDiff < self.trackingThreshold and yBottomDiff < self.trackingThreshold
            #   return isObjectInPosition
            trackingFunc = lambda cols, rows, xLeft, yTop, xRight, yBottom : abs(xLeft - self.rectPt1[0]) < self.trackingThreshold and abs(yTop - self.rectPt1[1]) < self.trackingThreshold and abs(xRight - self.rectPt2[0]) < self.trackingThreshold and abs(yBottom - self.rectPt2[1]) < self.trackingThreshold
        else:
            self.updateCalibrationParams()
            trackingFunc = lambda cols, rows, xLeft, yTop, xRight, yBottom : False
        
        if labelDetections:
            self.isObjectInPosition = self.objectDetector.labelDetections(self.classToDetect, trackingFunc)
        
        return self.objectDetector.getImage()

def initGame(netModel, classToDetect, scoreThreshold, trackingThreshold, gameId):
    objectDetector = ObjectDetector(netModel, scoreThreshold, trackingThreshold)
    
    if gameId == 1:
        return KeepItInTheMiddle(objectDetector, classToDetect)
    elif gameId == 2:
        return MoveItToTheSpot(objectDetector, classToDetect)
    else:
        print('That is not a valid game objective')

if __name__ == '__main__':
    netModelIdx = 0
    scoreThreshold = 0.3
    trackingThreshold = 50
    detectClassName = "red ball"

    parser = argparse.ArgumentParser()
    parser.add_argument("objective", type=int, help="The game objective to play: \
        1 - Keep It In The Middle \
        2 - Move It To The Spot")
    args = parser.parse_args()

    game = initGame(netModels[netModelIdx], detectClassName, scoreThreshold, trackingThreshold, args.objective)
    
    if game != None:
        while True:
            img = game.runGameStep()
            cv.imshow(_gameName, img)
            ch = cv.waitKey(1)
            if ch == 27:
                break

    print('exiting...')
    cv.destroyAllWindows()
    