#!/usr/bin/env python

import argparse
import cv2 as cv
import time

netModels = [
    {
        'modelPath': 'models/mobilenet_ssd_v1_coco/frozen_inference_graph.pb',
        'configPath': 'models/mobilenet_ssd_v1_coco/ssd_mobilenet_v1_coco_2017_11_17.pbtxt',
        'classNames': { 
            0: 'background', 1: 'person', 2: 'bicycle', 3: 'car', 4: 'motorcycle', 5: 'airplane',
            6: 'bus', 7: 'train', 8: 'truck', 9: 'boat', 10: 'traffic light', 11: 'fire hydrant',
            13: 'stop sign', 14: 'parking meter', 15: 'bench', 16: 'bird', 17: 'cat',
            18: 'dog', 19: 'horse', 20: 'sheep', 21: 'cow', 22: 'elephant', 23: 'bear',
            24: 'zebra', 25: 'giraffe', 27: 'backpack', 28: 'umbrella', 31: 'handbag',
            32: 'tie', 33: 'suitcase', 34: 'frisbee', 35: 'skis', 36: 'snowboard',
            37: 'sports ball', 38: 'kite', 39: 'baseball bat', 40: 'baseball glove',
            41: 'skateboard', 42: 'surfboard', 43: 'tennis racket', 44: 'bottle',
            46: 'wine glass', 47: 'cup', 48: 'fork', 49: 'knife', 50: 'spoon',
            51: 'bowl', 52: 'banana', 53: 'apple', 54: 'sandwich', 55: 'orange',
            56: 'broccoli', 57: 'carrot', 58: 'hot dog', 59: 'pizza', 60: 'donut',
            61: 'cake', 62: 'chair', 63: 'couch', 64: 'potted plant', 65: 'bed',
            67: 'dining table', 70: 'toilet', 72: 'tv', 73: 'laptop', 74: 'mouse',
            75: 'remote', 76: 'keyboard', 77: 'cell phone', 78: 'microwave', 79: 'oven',
            80: 'toaster', 81: 'sink', 82: 'refrigerator', 84: 'book', 85: 'clock',
            86: 'vase', 87: 'scissors', 88: 'teddy bear', 89: 'hair drier', 90: 'toothbrush' 
        }
    },
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

def label_class(img, detection, score, className, boxColor=None):
    rows = img.shape[0]
    cols = img.shape[1]

    if boxColor == None:
        boxColor = (23, 230, 210)
    
    xLeft = int(detection[3] * cols)
    yTop = int(detection[4] * rows)
    xRight = int(detection[5] * cols)
    yBottom = int(detection[6] * rows)
    cv.rectangle(img, (xLeft, yTop), (xRight, yBottom), boxColor, thickness=4)

    label = className + ": " + str(int(round(score * 100))) + '%'
    labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    yTop = max(yTop, labelSize[1])
    cv.rectangle(img, (xLeft, yTop - labelSize[1]), (xLeft + labelSize[0], yTop + baseLine),
        (255, 255, 255), cv.FILLED)
    cv.putText(img, label, (xLeft, yTop), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

def track_object(img, detections, score_threshold, classNames, className, tracking_threshold):
    for detection in detections:
        score = float(detection[2])
        class_id = int(detection[1])
        if className in classNames.values() and className == classNames[class_id] and score > score_threshold:
            rows = img.shape[0]
            cols = img.shape[1]
            marginLeft = int(detection[3] * cols) # xLeft
            marginRight = cols - int(detection[5] * cols) # cols - xRight
            xMarginDiff = abs(marginLeft - marginRight)
            marginTop = int(detection[4] * rows) # yTop
            marginBottom = rows - int(detection[6] * rows) # rows - yBottom
            yMarginDiff = abs(marginTop - marginBottom)
            
            if xMarginDiff < tracking_threshold and yMarginDiff < tracking_threshold:
                boxColor = (0, 255, 0)
            else:
                boxColor = (0, 0, 255)

            label_class(img, detection, score, classNames[class_id], boxColor)

def run_video_detection(netModel, classNameToDetect):
    scoreThreshold = 0.3
    trackingThreshold = 50

    cvNet = cv.dnn.readNetFromTensorflow(netModel['modelPath'], netModel['configPath'])
    cap = create_capture()
    
    while True:
        _, img = cap.read()

        # run detection
        cvNet.setInput(cv.dnn.blobFromImage(img, 1.0/127.5, (300, 300), (127.5, 127.5, 127.5), swapRB=True, crop=False))
        detections = cvNet.forward()
        track_object(img, detections[0,0,:,:], scoreThreshold, netModel['classNames'], classNameToDetect, trackingThreshold)
        cv.imshow('Real-Time Object Detection', img)

        ch = cv.waitKey(1)
        if ch == 27:
            break

    print('exiting...')
    cv.destroyAllWindows()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("net_model", type=int, help="The neural net model index.")
    parser.add_argument("detect_class", type=str, help="The class name to detect.")
    args = parser.parse_args()

    run_video_detection(netModels[args.net_model], args.detect_class)
