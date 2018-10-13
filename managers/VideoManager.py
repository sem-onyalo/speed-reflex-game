import cv2 as cv

class VideoManager:
    centreChallengeWinGameText = 'YOU WIN!' # TEMP - TO BE REMOVED
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
    frameWidth = 640#1920
    frameHeight = 480#1200

    def __init__(self, windowName, netModel, scoreThreshold, trackingThreshold):
        self.netModel = netModel
        self.scoreThreshold = scoreThreshold
        self.trackingThreshold = trackingThreshold
        cv.namedWindow(windowName, cv.WINDOW_NORMAL)
        # cv.setWindowProperty(windowName, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
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
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, self.frameWidth) # default: 640
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, self.frameHeight) # default: 480

    def readNewFrame(self):
        _, img = self.cap.read()
        self.img = cv.flip(img, 1)

    def runDetection(self):
        self.readNewFrame()
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
            if label == self.centreChallengeWinGameText: # TODO: move this put text code into CentreChallenge class somehow
                xPadding = 200
            cv.putText(self.img, label, (int(cols/2) - xPadding, int(rows/2)), cv.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), thickness=7)

        # cv.line(self.img, (0,self.imgMargin), (cols,self.imgMargin), (0, 0, 255), thickness=2)
        # cv.line(self.img, (0,rows-self.imgMargin), (cols,rows-self.imgMargin), (0, 0, 255), thickness=2)
        return isObjectInPosition