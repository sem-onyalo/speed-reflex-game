import cv2 as cv

# Set constants
userDirectory = '/home/pi'

# Set run params
scoreThreshold = 0.3
inputImagePath = userDirectory + '/code/speed-reflex-game/test/test-image.jpeg'

# Load the model 
modelDirectory = userDirectory + '/code/speed-reflex-game/models/mobilenet_ssd_v1_boxing/FP16'
xmlFile = modelDirectory + '/transformed_frozen_inference_graph.xml'
binFile = modelDirectory + '/transformed_frozen_inference_graph.bin'
net = cv.dnn.readNet(xmlFile, binFile)

# Specify target device 
net.setPreferableTarget(cv.dnn.DNN_TARGET_MYRIAD)
      
# Read an image 
frame = cv.imread(inputImagePath)
      
# Prepare input blob and perform an inference 
blob = cv.dnn.blobFromImage(frame, size=(300, 300), swapRB=True, crop=False)
net.setInput(blob) 
det = net.forward()

# Draw detections
rows = frame.shape[0]
cols = frame.shape[1]
for detection in det[0,0,:,:]:
    score = float(detection[2])
    if score > scoreThreshold:
        xmin = int(detection[3] * cols)
        ymin = int(detection[4] * rows)
        xmax = int(detection[5] * cols)
        ymax = int(detection[6] * rows)
        cv.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0))

# Save the frame to an image file 
cv.imwrite(userDirectory + '/code/speed-reflex-game/test/out-boxing.png', frame) 
