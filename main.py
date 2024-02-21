# Install Anaconda from the following link: https://www.anaconda.com/download
# Run and open, use the VSCode launcher, open the terminal and use
# pip install opencv-contrib-python # some people ask the difference between this and opencv-python
                                    # and opencv-python contains the main packages wheras the other
                                    # contains both main modules and contrib/extra modules
# pip install cvlib # for object detection
# pip install tensorflow --user
# use `pip3 install PyObjC`

import cv2
import cvlib as cv
from cvlib.object_detection import draw_bbox

video = cv2.VideoCapture(0) # webcam selector

while True:
    ret, frame = video.read()
    bbox, label, conf = cv.detect_common_objects(frame) # charcteristics of obj
    output_image = draw_bbox(frame, bbox, label, conf) # overlay
    
    cv2.imshow("Detection", output_image) #name of the webcam window

    if cv2.waitKey(1) & 0xFF == ord("q"): # to turn off webcam when running press q in code
        break
