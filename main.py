#!/usr/bin/env python

import argparse
import cv2 as cv
import random
import time

_gameName = 'Speed Reflex Game'
_winGameText = 'YOU WIN!'

netModels = [
    {
        'modelPath': 'models/mobilenet_ssd_v1_balls/transformed_frozen_inference_graph.pb',
        'configPath': 'models/mobilenet_ssd_v1_balls/ssd_mobilenet_v1_balls_2018_05_20.pbtxt',
        'classNames': {
            0: 'background', 1: 'red ball', 2: 'blue ball'
        }
    }
]

class ObjectDetector:
    img = None
    netModel = None
    detections = None
    scoreThreshold = None
    trackingThreshold = None
    xLeftDetection = None
    xRightDetection = None
    yTopDetection = None
    yBottomDetection = None
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
        return self.xRightDetection - self.xLeftDetection if self.xRightDetection != None and self.xLeftDetection != None else None

    def getYCoordDetectionDiff(self):
        return self.yBottomDetection - self.yTopDetection if self.yBottomDetection != None and self.yTopDetection != None else None

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

    def labelDetections(self, className, trackingFunc, boxColorFunc, label=None):
        rows = self.img.shape[0]
        cols = self.img.shape[1]
        isObjectInPosition = False
        self.xLeftDetection = None
        self.xRightDetection = None
        self.yTopDetection = None
        self.yBottomDetection = None
        for detection in self.detections[0,0,:,:]:
            score = float(detection[2])
            class_id = int(detection[1])
            if score > self.scoreThreshold and className == self.netModel['classNames'][class_id]:
                xLeft = int(detection[3] * cols) # marginLeft
                yTop = int(detection[4] * rows) # marginTop
                xRight = int(detection[5] * cols)
                yBottom = int(detection[6] * rows)
                isObjectInPosition = trackingFunc(cols, rows, xLeft, yTop, xRight, yBottom)
                boxColor = boxColorFunc(cols, rows, xLeft, yTop, xRight, yBottom)
                cv.rectangle(self.img, (xLeft, yTop), (xRight, yBottom), boxColor, thickness=6)
                # set detection points
                self.xLeftDetection = xLeft
                self.xRightDetection = xRight
                self.yTopDetection = yTop
                self.yBottomDetection = yBottom
        if label != None:
            xPadding = 20
            if label == _winGameText:
                xPadding = 200
            cv.putText(self.img, label, (int(cols/2) - xPadding, int(rows/2)), cv.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), thickness=7)

        return isObjectInPosition

class KeepItInTheMiddle:
    trackingThreshold = 50
    maxTime = 5
    showResultMaxTime = 3
    startTime = None
    showResult = False
    startShowResultTime = None
    isObjectFound = False
    isWinning = False
    classToDetect = ""

    objectDetector = None

    def __init__(self, objectDetector, classToDetect):
        self.objectDetector = objectDetector
        self.classToDetect = classToDetect

    def updateGameParams(self):
        gameLabel = None
        if self.isWinning and self.isObjectFound and self.startTime is not None:
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
                    self.isObjectFound = False
                    gameLabel = None
            else:
                if elapsedTime > self.maxTime:
                    self.startShowResultTime = time.time()
                    self.showResult = True
                    gameLabel = _winGameText
                else:
                    gameLabel = str(int(elapsedTime)) if elapsedTime >= 1 else None
        elif self.isWinning and not self.isObjectFound:
            self.isWinning = False
            self.startTime = None
        elif not self.isWinning and self.isObjectFound:
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
        
        # Name: boxColorFunc 
        # Description: Determines what the color of the box around the object should be
        # Code:
        # boxColorFunc(cols, rows, xLeft, yTop, xRight, yBottom):
        #   isObjectInPosition = trackingFunc(cols, rows, xLeft, yTop, xRight, yBottom)
        #   boxColor = (0, 255, 0) if isObjectInPosition else (0, 0, 255)
        #   return boxColor
        boxColorFunc = lambda cols, rows, xLeft, yTop, xRight, yBottom : (0, 255, 0) if trackingFunc(cols, rows, xLeft, yTop, xRight, yBottom) else (0, 0, 255)
        
        self.isObjectFound = self.objectDetector.labelDetections(self.classToDetect, trackingFunc, boxColorFunc, gameLabel)
        return self.objectDetector.getImage()

class KeepItInTheSpot:
    objectDetector = None
    classToDetect = ""
    minObjectSize = None
    maxObjectSize = None
    isCalibrated = False
    calibrationStep = 1
    calibrationSubStep = 1
    calibrationStartTime = None
    calibrationMaxTime = 3
    changeSpotStartTime = time.time()
    changeSpotMaxTime = 5

    def __init__(self, objectDetector, classToDetect):
        self.objectDetector = objectDetector
        self.classToDetect = classToDetect

    def getRectanglePts(self):
        size = self.minObjectSize # size = random.randint(self.minObjectSize, self.maxObjectSize)
        widthPt = random.randint(0, self.objectDetector.frameWidth)
        heightPt = random.randint(0, self.objectDetector.frameHeight)
        if widthPt + size > self.objectDetector.frameWidth:
            xRight = widthPt
            xLeft = widthPt - size
        else:
            xLeft = widthPt
            xRight = widthPt + size
        if heightPt + size > self.objectDetector.frameHeight:
            yBottom = heightPt
            yTop = heightPt - size
        else:
            yTop = heightPt
            yBottom = heightPt + size
        rectPt1 = (xLeft, yTop)
        rectPt2 = (xRight, yBottom)
        return rectPt1, rectPt2

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
                        
        elif self.calibrationStep == 2: # calibrate for largest object size
            if self.calibrationSubStep == 1:
                print('Hold object closest from screen')
                self.calibrationStartTime = time.time()
                self.calibrationSubStep = self.calibrationSubStep + 1
            elif self.calibrationSubStep == 2:
                currentTime = time.time()
                if currentTime - self.calibrationStartTime > self.calibrationMaxTime:
                    xCoordDiff = self.objectDetector.getXCoordDetectionDiff()
                    yCoordDiff = self.objectDetector.getYCoordDetectionDiff()
                    if xCoordDiff != None and yCoordDiff != None:
                        self.maxObjectSize = min(int(xCoordDiff), int(yCoordDiff))
                        print('Max obj size:', self.maxObjectSize)
                        self.calibrationStep = self.calibrationStep + 1
                        self.calibrationSubStep = 1
                    else:
                        raise RuntimeError('Calibration failed at step', self.calibrationStep, self.calibrationSubStep)

        elif self.calibrationStep == 3: # calculate calibration parmas
            self.calibrationSubStep = 1
            self.calibrationStep = 1
            self.isCalibrated = True

    def updateGameParams(self):
        currentSpotTime = time.time()
        if currentSpotTime - self.changeSpotStartTime > self.changeSpotMaxTime:
            self.rectPt1, self.rectPt2 = self.getRectanglePts()
            self.changeSpotStartTime = time.time()
        elif self.rectPt1 == None or self.rectPt2 == None:
            self.rectPt1, self.rectPt2 = self.getRectanglePts()
        cv.rectangle(self.objectDetector.getImage(), self.rectPt1, self.rectPt2, (0, 255, 255), thickness=6)

    def runGameStep(self):
        self.objectDetector.runDetection()

        trackingFunc = lambda cols, rows, xLeft, yTop, xRight, yBottom : False
        boxColorFunc = lambda cols, rows, xLeft, yTop, xRight, yBottom : (0, 255, 255)
        self.objectDetector.labelDetections(self.classToDetect, trackingFunc, boxColorFunc)
        
        if self.isCalibrated:
            self.updateGameParams()
        else:
            self.updateCalibrationParams()

        return self.objectDetector.getImage()

def initGame(netModel, classToDetect, scoreThreshold, trackingThreshold, gameId):
    objectDetector = ObjectDetector(netModel, scoreThreshold, trackingThreshold)
    game = None
    if gameId == 1:
        game = KeepItInTheMiddle(objectDetector, classToDetect)
    elif gameId == 2:
        game = KeepItInTheSpot(objectDetector, classToDetect)
    else:
        print('That is not a valid game objective')
    return game

if __name__ == '__main__':
    netModelIdx = 0
    scoreThreshold = 0.3
    trackingThreshold = 50
    detectClassName = "red ball"

    parser = argparse.ArgumentParser()
    parser.add_argument("objective", type=int, help="The game objective to play: \
        1 - Keep It In The Middle \
        2 - Keep It In The Spot")
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
    