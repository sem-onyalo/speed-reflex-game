import cv2 as cv

# Set constants
userDirectory = '/home/pi'

# Set run params
scoreThreshold = 0.2
inputImagePath = userDirectory + '/code/speed-reflex-game/test/test-image.jpeg'

# Load the model 
modelDirectory = userDirectory + '/Downloads/inference_engine_vpu_arm/deployment_tools/inference_engine/samples/build'
xmlFile = modelDirectory + '/face-detection-adas-0001.xml'
binFile = modelDirectory + '/face-detection-adas-0001.bin'
net = cv.dnn.readNet(xmlFile, binFile)

# Specify target device 
net.setPreferableTarget(cv.dnn.DNN_TARGET_MYRIAD)
      
# Read an image 
frame = cv.imread(inputImagePath)
      
# Prepare input blob and perform an inference 
blob = cv.dnn.blobFromImage(frame, size=(672, 384), ddepth=cv.CV_8U) 
net.setInput(blob) 
out = net.forward()
      
# Draw detected faces on the frame 
for detection in out.reshape(-1, 7): 
    confidence = float(detection[2]) 
    xmin = int(detection[3] * frame.shape[1]) 
    ymin = int(detection[4] * frame.shape[0]) 
    xmax = int(detection[5] * frame.shape[1]) 
    ymax = int(detection[6] * frame.shape[0])

    if confidence > scoreThreshold:
        cv.rectangle(frame, (xmin, ymin), (xmax, ymax), color=(0, 255, 0))

# Save the frame to an image file 
cv.imwrite(userDirectory + '/code/speed-reflex-game/test/out-fd.png', frame) 
