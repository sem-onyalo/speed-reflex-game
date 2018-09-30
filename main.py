#!/usr/bin/env python

import argparse
import cv2 as cv
import time

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

    def __init__(self, netModel, scoreThreshold, trackingThreshold):
        self.netModel = netModel
        self.scoreThreshold = scoreThreshold
        self.trackingThreshold = trackingThreshold
        self.cvNet = cv.dnn.readNetFromTensorflow(self.netModel['modelPath'], self.netModel['configPath'])
        self.cap = self.create_capture()

    def getImage(self):
        return self.img

    def create_capture(self, source = 0):
        cap = cv.VideoCapture(source)
        if cap is None or not cap.isOpened():
            print('Warning: unable to open video source: ', source)
        return cap

    def runDetection(self):
        _, self.img = self.cap.read()
        self.cvNet.setInput(cv.dnn.blobFromImage(self.img, 1.0/127.5, (300, 300), (127.5, 127.5, 127.5), swapRB=True, crop=False))
        self.detections = self.cvNet.forward()

    def runObjectTracking(self, className, label):
        rows = self.img.shape[0]
        cols = self.img.shape[1]
        isObjectInPosition = False
        for detection in self.detections[0,0,:,:]:
            score = float(detection[2])
            class_id = int(detection[1])
            if score > self.scoreThreshold and className == self.netModel['classNames'][class_id]:
                xRight = int(detection[5] * cols)
                yBottom = int(detection[6] * rows)
                marginLeft = int(detection[3] * cols) # xLeft
                marginRight = cols - xRight # cols - xRight
                marginTop = int(detection[4] * rows) # yTop
                marginBottom = rows - yBottom # rows - yBottom
                xMarginDiff = abs(marginLeft - marginRight)
                yMarginDiff = abs(marginTop - marginBottom)
                isObjectInPosition = (xMarginDiff < self.trackingThreshold and yMarginDiff < self.trackingThreshold)
                boxColor = (0, 255, 0) if isObjectInPosition else (0, 0, 255)
                cv.rectangle(self.img, (marginLeft, marginTop), (xRight, yBottom), boxColor, thickness=6)
                # cv.putText(self.img, str(xLeft) + ' ' + str(xRight) + ' ' + str(yTop) + ' ' + str(yBottom), (10,50), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
        if label is not None:
            xPadding = 20
            if label == 'YOU WIN!':
                xPadding = 200
            cv.putText(self.img, label, (int(cols/2) - xPadding, int(rows/2)), cv.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), thickness=7)

        return isObjectInPosition

class KeepItInTheMiddle:
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

    def runGameStep(self):
        self.objectDetector.runDetection()

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

        self.isObjectFound = self.objectDetector.runObjectTracking(self.classToDetect, gameLabel)

        return self.objectDetector.getImage()
        
def run_game(netModel, classToDetect, scoreThreshold, trackingThreshold):
    objectDetector = ObjectDetector(netModel, scoreThreshold, trackingThreshold)
    game = KeepItInTheMiddle(objectDetector, classToDetect)
    while True:
        img = game.runGameStep()
        cv.imshow('Speed Reflex Game', img)
        ch = cv.waitKey(1)
        if ch == 27:
            break
    print('exiting...')
    cv.destroyAllWindows()

if __name__ == '__main__':
    netModelIdx = 0
    scoreThreshold = 0.3
    trackingThreshold = 50
    detectClassName = "red ball"

    parser = argparse.ArgumentParser()
    parser.add_argument("objective", type=int, help="The game objective to play:\n \
        1 - Keep It In The Middle\n \
        2 - Keep It In The Spot")
    args = parser.parse_args()

    if args.objective > 2 or args.objective < 1:
        print("That objective doesn't exist")
    else:
        run_game(netModels[netModelIdx], detectClassName, scoreThreshold, trackingThreshold)