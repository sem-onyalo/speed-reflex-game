import cv2 as cv

class VideoManager:
    imgMargin = 60
    img = None
    netModel = None
    windowName = ""
    detections = None
    scoreThreshold = None
    trackingThreshold = None
    xLeftPos = None
    xRightPos = None
    yTopPos = None
    yBottomPos = None

    def __init__(self, windowName, frameWidth, frameHeight, netModel, scoreThreshold, trackingThreshold):
        self.netModel = netModel
        self.windowName = windowName
        self.frameWidth = frameWidth
        self.frameHeight = frameHeight
        self.scoreThreshold = scoreThreshold
        self.trackingThreshold = trackingThreshold
        cv.namedWindow(self.windowName, cv.WINDOW_NORMAL)
        self.cvNet = cv.dnn.readNetFromTensorflow(self.netModel['modelPath'], self.netModel['configPath'])
        self.create_capture()

    def getImage(self):
        return self.img

    def getXCoordDetectionDiff(self):
        return self.xRightPos - self.xLeftPos if self.xRightPos != None and self.xLeftPos != None else None

    def getYCoordDetectionDiff(self):
        return self.yBottomPos - self.yTopPos if self.yBottomPos != None and self.yTopPos != None else None

    def getDefaultFont(self):
        return cv.FONT_HERSHEY_SIMPLEX

    def getKeyPress(self):
        return cv.waitKey(1)

    def getTextSize(self, text, font, scale, thickness):
        return cv.getTextSize(text, font, scale, thickness)[0]

    def showImage(self):
        cv.imshow(self.windowName, self.img)

    def addText(self, text, pt, font, scale, color, thickness):
        cv.putText(self.img, text, pt, font, scale, color, thickness, cv.LINE_AA)

    def addRectangle(self, pt1, pt2, color, thickness, isFilled=False):
        if isFilled:
            thickness = cv.FILLED
        cv.rectangle(self.img, pt1, pt2, color, thickness, cv.LINE_AA)

    def addLine(self, pt1, pt2, color, thickness):
        cv.line(self.img, pt1, pt2, color, thickness)

    def shutdown(self):
        cv.destroyAllWindows()

    def create_capture(self, source = 0):
        self.cap = cv.VideoCapture(source)
        if self.cap is None or not self.cap.isOpened():
            raise RuntimeError('Warning: unable to open video source: ', source)
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, self.frameWidth) # default: 640
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, self.frameHeight) # default: 480

    def readNewFrame(self):
        _, img = self.cap.read()
        self.img = cv.flip(img, 1)

    def runDetection(self):
        self.readNewFrame()
        self.cvNet.setInput(cv.dnn.blobFromImage(self.img, 1.0/127.5, (300, 300), (127.5, 127.5, 127.5), swapRB=True, crop=False))
        self.detections = self.cvNet.forward()

    def labelDetections(self, classNames, trackingFunc):
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
            if score > self.scoreThreshold and self.netModel['classNames'][class_id] in classNames:
                self.xLeftPos = int(detection[3] * cols) # marginLeft
                self.yTopPos = int(detection[4] * rows) # marginTop
                self.xRightPos = int(detection[5] * cols)
                self.yBottomPos = int(detection[6] * rows)
                isObjectInPosition = trackingFunc(cols, rows, self.xLeftPos, self.yTopPos, self.xRightPos, self.yBottomPos)
                boxColor = (0, 255, 0) if isObjectInPosition else (0, 0, 255)
                self.addRectangle((self.xLeftPos, self.yTopPos), (self.xRightPos, self.yBottomPos), boxColor, 6)

        # self.addLine((0,self.imgMargin), (cols,self.imgMargin), (0, 0, 255), 2)
        # self.addLine((0,rows-self.imgMargin), (cols,rows-self.imgMargin), (0, 0, 255), 2)
        return isObjectInPosition