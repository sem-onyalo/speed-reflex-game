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

def create_capture(source = 0):
    cap = cv.VideoCapture(source)
    if cap is None or not cap.isOpened():
        print('Warning: unable to open video source: ', source)
    return cap

def track_object(img, detections, score_threshold, classNames, className, tracking_threshold, label):
    rows = img.shape[0]
    cols = img.shape[1]
    isObjectInPosition = False
    for detection in detections:
        score = float(detection[2])
        class_id = int(detection[1])
        if score > score_threshold and className == classNames[class_id]:
            xRight = int(detection[5] * cols)
            yBottom = int(detection[6] * rows)
            marginLeft = int(detection[3] * cols) # xLeft
            marginRight = cols - xRight # cols - xRight
            marginTop = int(detection[4] * rows) # yTop
            marginBottom = rows - yBottom # rows - yBottom
            xMarginDiff = abs(marginLeft - marginRight)
            yMarginDiff = abs(marginTop - marginBottom)
            isObjectInPosition = (xMarginDiff < tracking_threshold and yMarginDiff < tracking_threshold)
            boxColor = (0, 255, 0) if isObjectInPosition else (0, 0, 255)
            cv.rectangle(img, (marginLeft, marginTop), (xRight, yBottom), boxColor, thickness=6)
            # cv.putText(img, str(xLeft) + ' ' + str(xRight) + ' ' + str(yTop) + ' ' + str(yBottom), (10,50), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
    if label is not None:
        xPadding = 20
        if label == 'YOU WIN!':
            xPadding = 200
        cv.putText(img, label, (int(cols/2) - xPadding, int(rows/2)), cv.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), thickness=7)

    return isObjectInPosition
        
def run_game(netModel, classNameToDetect, scoreThreshold, trackingThreshold):
    maxTime = 5
    showResultMaxTime = 3
    startTime = None
    showResult = False
    startShowResultTime = None
    isObjectFound = False
    isWinning = False

    cvNet = cv.dnn.readNetFromTensorflow(netModel['modelPath'], netModel['configPath'])
    cap = create_capture()
    while True:
        _, img = cap.read()
        cvNet.setInput(cv.dnn.blobFromImage(img, 1.0/127.5, (300, 300), (127.5, 127.5, 127.5), swapRB=True, crop=False))
        detections = cvNet.forward()
        # calculate timer and set label
        gameLabel = None
        if isWinning and isObjectFound and startTime is not None:
            currentTime = time.time()
            elapsedTime = currentTime - startTime
            if showResult and startShowResultTime is not None:
                gameLabel = _winGameText
                currentShowResultTime = time.time()
                elapsedShowResultTime = currentShowResultTime - startShowResultTime
                if elapsedShowResultTime > showResultMaxTime:
                    # reset game
                    startShowResultTime = None
                    startTime = None
                    showResult = False
                    isWinning = False
                    isObjectFound = False
                    gameLabel = None
            else:
                if elapsedTime > maxTime:
                    startShowResultTime = time.time()
                    showResult = True
                    gameLabel = _winGameText
                else:
                    gameLabel = str(int(elapsedTime)) if elapsedTime >= 1 else None
        elif isWinning and not isObjectFound:
            isWinning = False
            startTime = None
        elif not isWinning and isObjectFound:
            startTime = time.time()
            isWinning = True

        isObjectFound = track_object(img, detections[0,0,:,:], scoreThreshold, netModel['classNames'], classNameToDetect, trackingThreshold, gameLabel)
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
    run_game(netModels[netModelIdx], detectClassName, scoreThreshold, trackingThreshold)