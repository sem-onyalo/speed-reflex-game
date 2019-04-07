import cv2 as cv

# Set run params
scoreThreshold = 0.3
inputImage = '/home/pi/Downloads/boxing-1.jpeg'

# Load the model 
modelDirectory = '/home/pi/code/speed-reflex-game/models/mobilenet_ssd_v1_boxing/FP16'
xmlFile = modelDirectory + '/transformed_frozen_inference_graph.xml'
binFile = modelDirectory + '/transformed_frozen_inference_graph.bin'
net = cv.dnn.readNet(xmlFile, binFile)

# Specify target device 
net.setPreferableTarget(cv.dnn.DNN_TARGET_MYRIAD)
      
# Read an image 
frame = cv.imread(inputImage)
      
# Prepare input blob and perform an inference 
#blob = cv.dnn.blobFromImage(frame, size=(672, 384), ddepth=cv.CV_8U)
blob = cv.dnn.blobFromImage(frame, 1.0/127.5, (300, 300), (127.5, 127.5, 127.5), swapRB=True, crop=False)
net.setInput(blob) 
det = net.forward()

# Draw detections
rows = det.shape[0]
cols = det.shape[1]
for detection in det[0,0,:,:]:
    score = float(detection[2])
    class_id = int(detection[1])
    if score > scoreThreshold:
        xLeftPos = int(detection[3] * cols) # marginLeft
        yTopPos = int(detection[4] * rows) # marginTop
        xRightPos = int(detection[5] * cols)
        yBottomPos = int(detection[6] * rows)
        cv.rectangle(self.img, (xLeftPos, yTopPos), (xRightPos, yBottomPos), (0, 255, 0))

# Save the frame to an image file 
cv.imwrite('/home/pi/code/speed-reflex-game/test/out.png', frame) 
